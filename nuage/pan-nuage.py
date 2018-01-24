#!/usr/bin/env python

# simple service that translates VM information taken from 
# Nuage VSD into PAN-OS DAG calls

# Assumptions
# - 1:1 relationship between VPort and VMInterface
# - once a VPort is created in a subnet (and hence in a zone) it can't be moved

# Limitations (that could be easily fixed)
# - only one Nuage domain is checked
# - VM-Series should be predeployed

import eventlet
eventlet.monkey_patch()

import logging
import sys
import getopt
import pprint

import pan.xapi
import nuage

LOG = logging.getLogger(__name__)

class NuageListener(object):
    def __init__(self, do, conf):
        self.do = do
        self.conf = conf

    def run(self):
        LOG.debug("NuageListener started")

        n = nuage.NuageAPI(self.conf['nuage-vsd'],
                           self.conf['nuage-login'],
                           self.conf['nuage-password'],
                           self.conf['nuage-organization'])

        while True:
            events = n.nevents()

            for e in events:
                if e['entityType'] == 'policygroup':
                    if e['type'] == 'UPDATE':
                        for et in e['entities']:
                            self.do.put('policygroup_update', { 'ID': et['ID'] })
                    elif e['type'] == 'DELETE':
                        for et in e['entities']:
                            self.do.put('policygroup_delete', { 'ID': et['ID'] })
                elif e['entityType'] == 'vminterface':
                    if e['type'] == 'CREATE':
                        for et in e['entities']:
                            self.do.put('vminterface_create', { 
                                'VPortID': et['VPortID'], 
                                'IPAddress': et['IPAddress'],
                                'zoneID': et['zoneID'] 
                            })
                    elif e['type'] == 'UPDATE':
                        for et in e['entities']:
                            self.do.put('vminterface_update', { 
                                'VPortID': et['VPortID'], 
                                'IPAddress': et['IPAddress'],
                                'zoneID': et['zoneID'] 
                            })
                    elif e['type'] == 'DELETE':
                        for et in e['entities']:
                            self.do.put('vminterface_delete', { 
                                'VPortID': et['VPortID'], 
                                'IPAddress': et['IPAddress'],
                                'zoneID': et['zoneID'] 
                            })
                elif e['entityType'] == 'vport':
                    if e['type'] == 'DELETE':
                        for et in e['entities']:
                            self.do.put('vport_delete', { 'ID': et['ID'] })
                    elif e['type'] in ['CREATE', 'UPDATE']:
                        for et in e['entities']:
                            if et['parentType'] == 'subnet':
                                self.do.put('vport_update', { 'ID': et['ID'], 'subnetID': et['parentID'] })
                else:
                    pass
                    # LOG.debug("ignored event: %s", pprint.pformat(e))

class DagOrchestrator(object):
    def __init__(self, conf):
        self.conf = conf

        self.msg_queue = eventlet.queue.LightQueue()
        self.dag_pushers = {}

        self.build_nuage_image()

    def build_nuage_image(self):
        self.vports = {}
        self.policy_groups = {}

        n = nuage.NuageAPI(self.conf['nuage-vsd'],
                           self.conf['nuage-login'],
                           self.conf['nuage-password'],
                           self.conf['nuage-organization'])

        for z in n.list_domain_zones(self.conf['nuage-domain']):
            for s in n.list_zone_subnets(z['ID']):
                for vp in n.list_subnet_vports(s['ID']):
                    vmis = set()
                    for vmi in n.list_vport_vminterfaces(vp['ID']):
                        vmis.add(vmi['IPAddress'])
                    if len(vmis) != 0:
                        self.vports[vp['ID']] = {
                            'zone': z['ID'],
                            'subnet': s['ID'],
                            'addresses': vmis
                        }

        for pg in n.list_domain_policygroups(self.conf['nuage-domain']):
            self.policy_groups[pg['ID']] = set()
            for vp in n.list_policygroup_vports(pg['ID']):
                self.policy_groups[pg['ID']].add(vp['ID'])

        LOG.debug("vports: %s", self.vports)
        LOG.debug("policy_groups: %s", self.policy_groups)

    def put(self, command, args=None):
        self.msg_queue.put((command, args))

    def register_tags(self, vpid, tags):
        if not vpid in self.vports:
            LOG.error("register_tags for unknown vport: %s", vpid)

        addr = next(iter(self.vports[vpid]['addresses']))
        if addr is None:
            return

        LOG.info("register tags %s for %s", tags, addr)

        for dpaddr, dp in self.dag_pushers.iteritems():
            dp.put('register', addr, tags)

    def unregister_tags(self, vpid, tags=None):
        if not vpid in self.vports:
            LOG.error("unregister_tags for unknown vport: %s", vpid)

        addr = next(iter(self.vports[vpid]['addresses']))
        if addr is None:
            return

        LOG.info("unregister tags %s for %s", tags, addr)

        for dpaddr, dp in self.dag_pushers.iteritems():
            dp.put('unregister', addr, tags)

    def register_vport(self, vpid):
        if not vpid in self.vports:
            LOG.error("unregister_tags for unknown vport: %s", vpid)

        vp = self.vports[vpid]
        addr = next(iter(vp['addresses']))
        if addr is None:
            return

        tags = [self.pgtag(pg) for pg in self.policy_groups.keys() if vpid in self.policy_groups[pg]]
        if vp['zone'] is not None:
            tags += [self.zonetag(vp['zone'])]
        if vp['subnet'] is not None:
            tags += [self.subnettag(vp['subnet'])]

        LOG.debug("registering vport %s - %s", vpid, pprint.pformat(vp))
        self.register_tags(vpid, tags)

    def pgtag(self, pgid):
	n = nuage.NuageAPI(self.conf['nuage-vsd'],
                       self.conf['nuage-login'],
                       self.conf['nuage-password'],
                       self.conf['nuage-organization'])
        for pg in n.list_domain_policygroups(self.conf['nuage-domain']):
            LOG.info("pgtag %s %s", pg['ID'], pgid)
            if pg['ID'] == pgid:
	        LOG.info("pgtag found %s %s", pg['ID'], pg['externalID'])
                if pg['externalID'] is not None:
	            LOG.info("policygroup name %s", pg['description'])
                    return "NuageVSP-policygroup-%s"%pg['description']
                else:
                    LOG.info("policygroup name %s", pg['name'])
                    return "NuageVSP-policygroup-%s"%pg['name']
        return "NuageVSP-policygroup-%s"%pgid

    def zonetag(self, zid):
        return 'zone-%s'%zid

    def subnettag(self, sid):
        return 'subnet-%s'%sid

    def policygroup_update(self, pgid):
        n = nuage.NuageAPI(self.conf['nuage-vsd'],
                           self.conf['nuage-login'],
                           self.conf['nuage-password'],
                           self.conf['nuage-organization'])

        curpg = set([vp['ID'] for vp in n.list_policygroup_vports(pgid)])

        mypg = self.policy_groups.get(pgid, set([]))
        self.policy_groups[pgid] = curpg

        added = curpg-mypg
        deleted = mypg-curpg

        for vpid in added:
            if vpid in self.vports:
                self.register_tags(vpid, [self.pgtag(pgid)])
        for vpid in deleted:
            if vpid in self.vports:
                self.unregister_tags(vpid, [self.pgtag(pgid)])

    def policygroup_delete(self, pgid):
        if not mypg in self.policy_groups:
            return

        mypg = self.policy_groups.pop(pgid)

        for vpid in mypg:
            if vpid in self.vports:
                self.unregister_tags(vpid, [self.pgtag(pgid)])

    def vport_update(self, vpid, address=None, zoneid=None, subnetid=None):
        if vpid in self.vports:
            curvp = self.vports[vpid]
            if address is not None and address not in curvp['addresses']:
                self.unregister_tags(vpid)
                curvp['addresses'] = set([address])
                self.register_vport(vpid)
            if zoneid is not None and curvp['zone'] != zoneid:
                if curvp['zone'] is not None:
                    self.unregister_tags(vpid, [self.zonetag(curvp['zone'])])
                self.register_tags(vpid, [self.zonetag(zoneid)])
                curvp['zone'] = zoneid
            if subnetid is not None and curvp['subnet'] != subnetid:
                if curvp['subnet'] is not None:
                    self.unregister_tags(vpid, [self.subnettag(curvp['subnet'])])
                self.register_tags(vpid, [self.subnettag(subnetid)])
                curvp['subnet'] = subnetid           
        else:
            self.vports[vpid] = {
                'zone': zoneid,
                'addresses': set([address]),
                'subnet': subnetid
            }
            if address is not None:
                self.register_vport(vpid)

    def vport_delete(self, vpid):
        if not vpid in self.vports:
            return
        self.unregister_tags(vpid)
        del self.vports[vpid]

    def vmseries_create(self, ipaddress, serial=None):
        vmid = ipaddress
        if serial is not None:
            vmid += ":"+serial

        if vmid in self.dag_pushers:
            return

        dp = DagPusher(ipaddress, serial=serial, conf=self.conf)
        self.dag_pushers[vmid] = dp

        for vpid in self.vports:
            curvp = self.vports[vpid]
            address = next(iter(curvp['addresses']))
            if address is None:
                continue

            if curvp['zone'] is not None:
                tags = [self.zonetag(curvp['zone'])]
            tags += [self.pgtag(pg) for pg in self.policy_groups if vpid in self.policy_groups[pg]]
            if curvp['subnet'] is not None:
                tags += [self.subnettag(curvp['subnet'])]

            dp.put('register', address, tags)

    def vmseries_delete(self, ipaddress, serial=None):
        vmid = ipaddress
        if serial is not None:
            vmid += ":"+serial

        if not vmid in self.dag_pushers:
            return

        self.dag_pushers[vmid].kill()
        del self.dag_pushers[vmid]

    def run(self):
        LOG.info("DagOrchestrator started")
        while True:
            try:
                cmd, args = self.msg_queue.get()
                LOG.debug("DagOrchestrator msg: %s", (cmd, args))
    
                if cmd == 'policygroup_update':
                    self.policygroup_update(args['ID'])
                elif cmd == 'policygroup_delete':
                    self.policygroup_delete(args['ID'])
                elif cmd == 'vminterface_create' or cmd == 'vminterface_update':
                    self.vport_update(args['VPortID'], address=args['IPAddress'], zoneid=args['zoneID'])
                elif cmd == 'vminterface_delete':
                    self.vport_delete(args['VPortID'])
                elif cmd == 'vport_delete':
                    self.vport_delete(args['ID'])
                elif cmd == 'vport_update':
                    self.vport_update(args['ID'], subnetid=args['subnetID'])
                elif cmd == 'vmseries_create':
                    self.vmseries_create(args['IPAddress'], serial=args.get('SN', None))
                elif cmd == 'vmseries_delete':
                    self.vmseries_delete(args['IPAddress'], serial=args.get('SN', None))
                else:
                    LOG.error("unknown cmd: %s", cmd)
            except gevent.GreenletExit:
                return
            except:
                LOG.exception("Exception in DagOrchestrator main loop")

class DagPusherGTKilled(Exception):
    pass

class DagPusher(object):
    def __init__(self, ipaddress, serial=None, conf=None):
        self.ipaddress = ipaddress
        self.conf = conf
        self.msg_queue = eventlet.queue.LightQueue()
        params = {
            'api_username': self.conf['pan-admin'],
            'api_password': self.conf['pan-password'],
            'timeout': 60,
            'hostname': ipaddress
        }
        if serial is not None:
            params['serial'] = serial

        self.xapi = pan.xapi.PanXapi(**params)

        self.g = eventlet.spawn(self.run)
        self.g.link(self._g_terminated)

        LOG.info("DagPusher for %s(:%s) started", ipaddress, serial)

    def put(self, cmd, address, tags=None):
        self.msg_queue.put((cmd, address, tags))

    def _g_terminated(self, gt):
        try:
            gt.wait()
        except DagPusherGTKilled:
            return
        except:
            LOG.exception("DagPusher for vmseries %s terminated with exception", self.ipaddress)

        LOG.info("respawning greenthread for vmseries %s", self.ipaddress)
        self.g = eventlet.spawn(self.run)
        self.g.link(self._g_terminated)

    def _unregister(self, ops):
        entries = {}
        for op, address, tags in ops:
            if address in entries:
                if entries[address] is not None:
                    if tags is None:
                        entries[address] = None
                    else:
                        entries[address] += tags
            else:
                entries[address] = tags

        uidmessage = ["<uid-message>",
                      "<version>1.0</version>",
                      "<type>update</type>",
                      "<payload>",
                      "<unregister>"]
        for address, tags in entries.iteritems():
            uidmessage += ['<entry ip="%s">'%address]
            if tags is not None:
                uidmessage += ['<tag>']
                for t in tags:
                    uidmessage += ['<member>%s</member>'%t]
                uidmessage += ['</tag>']
            uidmessage += ['</entry>']
        uidmessage += ["</unregister>",
                        "</payload>",
                        "</uid-message>"]

        cmd = ''.join(uidmessage)
        LOG.debug("unregister cmd: %s", cmd)
        self.xapi.user_id(cmd=cmd)

    def _register(self, ops):
        entries = {}
        for op, address, tags in ops:
            if tags is None:
                LOG.error("tags None in register")
                continue

            if address in entries:
                entries[address] += tags
            else:
                entries[address] = tags

        uidmessage = ["<uid-message>",
                      "<version>1.0</version>",
                      "<type>update</type>",
                      "<payload>",
                      "<register>"]
        for address, tags in entries.iteritems():
            uidmessage += ['<entry ip="%s">'%address]
            if len(tags) != 0:
                uidmessage += ['<tag>']
                for t in tags:
                    uidmessage += ['<member>%s</member>'%t]
                uidmessage += ['</tag>']
            uidmessage += ['</entry>']
        uidmessage += ["</register>",
                        "</payload>",
                        "</uid-message>"]

        cmd = ''.join(uidmessage)
        LOG.debug("register cmd: %s", cmd)
        try:
            self.xapi.user_id(cmd=cmd)
        except pan.xapi.PanXapiError as e:
            if not 'already exists, ignore' in e.msg.lower():
                raise

    def run(self):
        while True:
            try:
                self.xapi.keygen()
            except:
                LOG.exception("Exception in keygen for vmseries %s", self.ipaddress)
            else:
                break
            eventlet.sleep(30)

        while True:
            eventlet.sleep(0.2)
            # push new ones
            if self.msg_queue.qsize() == 0:
                continue

            # wow, something in the queue !!
            # let's aggregate all the ops with the same type
            ops = []
            msgcnt = 0

            ops.append(self.msg_queue.queue[0])
            optype = ops[0][0]
            while len(ops) < self.msg_queue.qsize() and self.msg_queue.queue[len(ops)][0] == optype:
                ops.append(self.msg_queue.queue[len(ops)])

            LOG.info("op %s in vmseries %s #%d", optype, self.ipaddress, len(ops))
            try:
                if optype == 'register':
                    self._register(ops)
                elif optype == 'unregister':
                    self._unregister(ops)
                else:
                    LOG.warn("Unknown op type in DagPusher for vmseries %s: %s", self.ipaddress, optype)
            except:
                LOG.exception("Exception in DagPusher for vmseries %s", self.ipaddress)
                eventlet.sleep(30)
            else:
                for i in ops:
                    self.msg_queue.get()

    def kill(self):
        self.g.kill(DagPusherGTKilled)
        self.msg_queue = None
        self.g = None

class PanoramaChecker(object):
    def __init__(self, address, do, conf):
        self.conf = conf
        self.address = address
        self.do = do
        self.xapi = pan.xapi.PanXapi(api_username=self.conf['pan-admin'],
                                     api_password=self.conf['pan-password'],
                                     timeout=60,
                                     hostname=address)
        self.vmseries = set([])

    def run(self):
        LOG.info("PanoramaChecker for %s started", self.address)

        device_tag = "nuage-%s"%('-'.join(self.conf['nuage-domain'].split('-')[:2]))
        xpath = "/config/mgt-config/devices/entry[vsys/entry/tags/member = '%s']"%device_tag
        LOG.debug("xpath %s", xpath)

        while True:
            try:
                self.xapi.get(xpath=xpath)
                devices = self.xapi.element_root.findall('./result/entry')
                current = set([])
                for d in devices:
                    sn = d.get('name', None)
                    if sn is None:
                        continue
                    current.add(sn)

                added = current-self.vmseries
                deleted = self.vmseries-current

                for a in added:
                    self.do.put('vmseries_create', {
                        'IPAddress': self.address,
                        'SN': a
                    })
                for d in deleted:
                    self.do.put('vmseries_delete', {
                        'IPAddress': self.address,
                        'SN': a
                    })

                self.vmseries = current
                
            except:
                LOG.exception("Error in retrieving devices with tag %s from panorama %s", device_tag, self.address)
            eventlet.sleep(60)

def build_conf(argv):
    res = {}

    options = [
        "nuage-vsd=", 
        "nuage-login=", 
        "nuage-password=", 
        "nuage-organization=",
        "nuage-domain=",
        "pan-admin=",
        "pan-password=",
        "vmseries=",
        "panorama="
    ]

    try:
        popts, pargs = getopt.getopt(argv, "", options)
    except getopt.GetoptError as err:
        LOG.critical("Error in command line: %s", err)
        sys.exit(1)

    for n, v in popts:
        if n[:2] == '--':
            n = n[2:]

        if res.has_key(n):
            if type(res[n]) != set:
                ov = res[n]
                res[n] = set()
                res[n].add(ov)
                res[n].add(v)
            else:
                res[n].add(v)
        else:
            res[n] = v

    LOG.debug("configuration: %s", res)

    return res

def main(argv):
    conf = build_conf(argv)

    try:
        pool = eventlet.GreenPool()

        do = DagOrchestrator(conf)
        pool.spawn(do.run)

        nl = NuageListener(do, conf)
        pool.spawn(nl.run)

        vms = conf.get('vmseries', None)
        if type(vms) == set:
            for v in vms:
                do.put('vmseries_create', { 'IPAddress': v })
        elif type(vms) == str:
            do.put('vmseries_create', { 'IPAddress': vms })

        pms = conf.get('panorama', None)
        if type(pms) == set:
            for p in pms:
                po = PanoramaChecker(p, do, conf)
                pool.spawn(po.run)
        elif type(pms) == str:
            po = PanoramaChecker(pms, do, conf)
            pool.spawn(po.run)

        pool.waitall()
    except KeyboardInterrupt:
        LOG.info("KeyboardInterrupt - exiting")

    except RuntimeError as e:
        LOG.error("RuntimeError: %s", e)
        sys.exit(1)

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p', level=logging.DEBUG)
    main(sys.argv[1:])
