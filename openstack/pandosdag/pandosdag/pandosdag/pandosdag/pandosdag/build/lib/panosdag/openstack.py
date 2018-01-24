import logging
import collections
import time
import greenlet

import oslo_config
import neutronclient.neutron.client
import keystoneclient.v2_0.client

import utils

import eventlet.queue


LOG = logging.getLogger(__name__)

CONF = oslo_config.cfg.CONF

OPTIONS = [
    oslo_config.cfg.StrOpt(
        'username'
    ),
    oslo_config.cfg.StrOpt(
        'password'
    ),
    oslo_config.cfg.StrOpt(
        'auth_url'
    ),
    oslo_config.cfg.StrOpt(
        'tenant_name'
    ),
    oslo_config.cfg.StrOpt(
        'insecure_ssl'
    )
]

def rlock(f):
    def wrapper(*args, **kwargs):
        rwlock = args[0].rwlock

        rwlock.rlock()
        try:
            result = f(*args, **kwargs)
            return result

        finally:
            rwlock.runlock()

    return wrapper

def wlock(f):
    def wrapper(*args, **kwargs):
        rwlock = args[0].rwlock

        rwlock.lock()
        try:
            result = f(*args, **kwargs)
            return result

        finally:
            rwlock.unlock()

    return wrapper

class OpenStackStatus(object):
    def __init__(self):
        self.nclient = neutronclient.neutron.client.Client(
            '2.0',
            username=CONF.openstack.username,
            password=CONF.openstack.password,
            tenant_name=CONF.openstack.tenant_name,
            auth_url=CONF.openstack.auth_url,
            insecure=CONF.openstack.insecure_ssl,
            debug=CONF.debug
        )
        self.nclient.format = 'json'

        self.kclient = keystoneclient.v2_0.client.Client(
            username=CONF.openstack.username,
            password=CONF.openstack.password,
            tenant_name=CONF.openstack.tenant_name,
            auth_url=CONF.openstack.auth_url,
            insecure=CONF.openstack.insecure_ssl,
            debug=CONF.debug
        )

        self.rwlock = panosdag.utils.RWLock()

        self.subscribers = collections.defaultdict(set)
        self.sg_subscribers = set()

        self.tenant_details = collections.defaultdict(dict)
        self.sg_details = collections.defaultdict(dict)

        self.sg_members = collections.defaultdict(set)
        self.registerd_ips = collections.defaultdict(set)

        self._gthread = None
        self.q = eventlet.queue.LightQueue()

    def _get_sg_members(self, sgid, tenant_id=None):
        LOG.info("retrieving sg memebr for security_group %s {%s}",
                 sgid, tenant_id)
        if tenant_id is None:
            if sgid not in self.sg_details:
                raise RuntimeError('unknown security_group id %s' % sgid)

            tenant_id = self.sg_details[sgid]['tenant_id']

        LOG.debug("retrieving port list for tenant_id %s", tenant_id)
        ports = self.nclient.list_ports(
                    tenant_id=tenant_id,
                    fields=['fixed_ips', 'security_groups']
                )
        ports = ports['ports']

        member_fips = [fip['ip_address']
                       for p in ports
                       if 'fixed_ips' in p and sgid in p['security_groups']
                       for fip in p['fixed_ips']]
        LOG.debug("members: %s", member_fips)

        return set(member_fips)

    def _add_sg_details(self, sgid):
        LOG.info("retrieving details for security_group %s", sgid)
        sg = self.nclient.list_security_groups(
            id=sgid,
            fields=['name', 'tenant_id']
        )['security_groups'][0]

        if sg['tenant_id'] not in self.tenant_details:
            LOG.info("retrieving details for tenant %s", sg['tenant_id'])
            t = self.kclient.tenants.get(sg['tenant_id'])
            self.tenant_details[t.id]['name'] = t.name
            self.tenant_details[t.id]['security_groups'] = set()

        self.sg_details[sgid]['name'] = sg['name']
        self.sg_details[sgid]['tenant_id'] = sg['tenant_id']
        LOG.debug("security_group %s details: %s", sgid, self.sg_details[sgid])

        self.tenant_details[sg['tenant_id']]['security_groups'].add(sgid)
        LOG.debug("tenant %s details: %s", 
                  sg['tenant_id'], self.tenant_details[sg['tenant_id']])

    @rlock
    def refresh_port(self, port):
        fips = [fip['ip_address'] for fip in port.get('fixed_ips', [])]
        sgs = set(port.get('security_groups', []))

        sg_changed = set()

        for fip in fips:
            if fip not in self.registerd_ips:
                continue
    
            cur_sgs = self.registerd_ips[fip]
            LOG.debug('cur_sgs: %s sgs: %s', cur_sgs, sgs)
    
            for sg in cur_sgs ^ sgs:
                sg_changed.add(sg)
    
        for sg in sg_changed:
            self.refresh_sg(sg)

        return len(sg_changed)

    def refresh_sg(self, sgid):
        self.q.put(['refresh_sg', [sgid, time.time()]])

    @wlock
    def _refresh_sg(self, sgid, timestamp):
        LOG.info("refresh security_group %s", sgid)

        old_tags = self._get_sg_tags(sgid)
        LOG.debug("current tags for security_group %s: %s", sgid, old_tags)

        if sgid not in self.sg_details:
            LOG.debug("unknown security_group %s, retrieving details",
                      sgid)
            self._add_sg_details(sgid)

        cur_registered_ips = self._get_sg_members(sgid)

        if sgid not in self.sg_members:
            old_registerd_ips = set()

            self.sg_members[sgid] = cur_registered_ips

            for rip in cur_registered_ips:
                self.registerd_ips[rip].add(sgid)

        else:
            old_registerd_ips = self.sg_members[sgid]

            for rip in (cur_registered_ips - old_registerd_ips):
                self.registerd_ips[rip].add(sgid)

            for rip in (old_registerd_ips - cur_registered_ips):
                self.registerd_ips[rip].discard(sgid)

            self.sg_members[sgid] = cur_registered_ips
        LOG.debug("security_group %s members: %s", sgid, self.sg_members[sgid])

        cur_tags = self._get_sg_tags(sgid)
        LOG.debug("new tags for security_group %s: %s", sgid, cur_tags)

        for rip in old_registerd_ips:
            if len(self.registerd_ips[rip]) != 0:
                cur_tags |= set([
                    '%s@%s' % (rip, self._get_pushed_tag()),
                    '%s@%s' % (rip, self._get_tenant_tag(self.sg_details[sgid]['tenant_id'])),
                    '%s@%s' % (rip, self._get_tenant_tag(self.tenant_details[self.sg_details[sgid]['tenant_id']]['name'])),
                ])
        LOG.debug("new tags after treatment for security_group %s: %s",
                  sgid, cur_tags)

        delta = self._get_tags_delta(old_tags, cur_tags)
        LOG.debug("delta for security_group %s: %s", sgid, delta)

        if len(delta[0])+len(delta[1]) != 0:
            tid = self.sg_details[sgid]['tenant_id']
            tname = self.tenant_details[tid]['name']
            LOG.debug("pushing delta to subscribers of %s", tid)
    
            for s in self.subscribers['*']:
                s.put('change', delta)
    
            for s in self.subscribers[tid]:
                s.put('change', delta)
    
            for s in self.subscribers[tname]:
                s.put('change', delta)

        return delta

    @wlock
    def refresh(self):
        cur_tenants = collections.defaultdict(dict)

        LOG.info("retrieving tenant list from OpenStack")
        for t in self.kclient.tenants.list():
            cur_tenants[t.id]['name'] = t.name
            cur_tenants[t.id]['security_groups'] = set()
        LOG.debug("tenants: %s", cur_tenants.keys())

        cur_sg_members = collections.defaultdict(set)
        cur_sg_details = collections.defaultdict(dict)

        LOG.info("retrieving security groups list")
        sgs = self.nclient.list_security_groups(
            fields=['name', 'id', 'tenant_id']
        )
        LOG.debug("security groups: %s", sgs)

        for sg in sgs['security_groups']:
            tid = sg.get('tenant_id', None)
            if tid not in cur_tenants:
                LOG.error('security_group %s with unknown tenant_id %s',
                          sg['id'], tid)
                continue

            sgid = sg['id']
            cur_sg_members[sgid] = self._get_sg_members(sgid, sg['tenant_id'])

            cur_tenants[sg['tenant_id']]['security_groups'].add(sgid)

            cur_sg_details[sgid]['name'] = sg['name']
            cur_sg_details[sgid]['tenant_id'] = sg['tenant_id']

        LOG.info("updating status with status retrieved")
        cur_registered_ips = collections.defaultdict(set)
        for sgid, members in cur_sg_members.iteritems():
            for m in members:
                cur_registered_ips[m].add(sgid)

        self.sg_members = cur_sg_members
        self.registerd_ips = cur_registered_ips
        self.sg_details = cur_sg_details
        self.tenant_details = cur_tenants

    def _get_sg_tag(self, sg):
        return '%s-%s-%s' % (CONF.tag_prefix, 'security_group', sg)

    def _get_tenant_tag(self, t):
        return '%s-%s-%s' % (CONF.tag_prefix, 'tenant', t)

    def _get_pushed_tag(self):
        return '%s-%s' % (CONF.tag_prefix, 'pushed')

    def _get_sg_tags(self, sg):
        tags = set()

        if sg not in self.sg_details or sg not in self.sg_members:
            return tags

        sgd = self.sg_details[sg]
        td = self.tenant_details[sgd['tenant_id']]

        for rip in self.sg_members[sg]:
            tags.add('%s@%s' % (rip, self._get_pushed_tag()))

            tags.add('%s@%s' % (rip, self._get_tenant_tag(sgd['tenant_id'])))
            tags.add('%s@%s' % (rip, self._get_tenant_tag(td['name'])))

            tags.add('%s@%s' % (rip, self._get_sg_tag(sg)))
            tags.add('%s@%s' % (rip, self._get_sg_tag(sgd['name'])))

        return tags

    def _get_tags_delta(self, old, new):
        register = collections.defaultdict(set)
        unregister = collections.defaultdict(set)

        for tag in (new - old):
            rip, tag = tag.split('@', 1)
            register[rip].add(tag)

        for tag in (old - new):
            rip, tag = tag.split('@', 1)
            unregister[rip].add(tag)

        return register, unregister

    @rlock
    def delta(self, callee_tags, tenant_ids=None):
        LOG.debug('delta called, tenant_ids: %s', tenant_ids)

        callee_tags = set(callee_tags)

        if tenant_ids is None:
            tenant_ids = set(self.tenant_details.keys())

        sgs = set()
        for tid in tenant_ids:
            if tid not in self.tenant_details:
                tid = next(
                    (t for t, v in self.tenant_details.iteritems() if v['name'] == tid),
                    None
                )
                if tid is None:
                    LOG.error('unknown tenant id %s', tid)
                    continue

            sgs |= self.tenant_details[tid]['security_groups']

        tags = set()
        for sg in sgs:
            if sg not in self.sg_members:
                continue

            tags |= self._get_sg_tags(sg)

        return self._get_tags_delta(callee_tags, tags)

    @wlock
    def subscribe(self, object, tenant=None, event='members'):
        if event == 'members':
            self.subscribers[tenant].add(object)
        elif event == 'security_groups':
            self.sg_subscribers.add(object)

    @wlock
    def unsubscribe(self, object, tenant=None, event='members'):
        if event == 'members':
            if tenant not in self.subscribers:
                return
            self.subscribers[tenant].discard(object)

        elif event == 'security_groups':
            self.sg_subscribers.discard(object)

    def _gthread_exit(self, gt):
        try:
            gt.wait()

        except:
            LOG.exception("OpenStackStatus terminated with exception")

        else:
            return

        LOG.info("respawning greenthread for OpenStackStatus")
        self._gthread = eventlet.spawn(self.run)
        self._gthread.link(self._gthread_exit)

    def _run(self):
        while True:
            try:
                cmd, args = self.q.get()

                if cmd == 'refresh_sg':
                    self._refresh_sg(*args)

                else:
                    LOG.error('unkown command in OpenStackStatus: %s', cmd)

            except greenlet.GreenletExit:
                break

            except:
                LOG.exception('exception in main loop of OpenStackStatus')
                eventlet.sleep(30)

    def run(self):
        self._gthread = eventlet.spawn(self._run)
        self._gthread.link(self._gthread_exit)
