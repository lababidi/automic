#  Copyright 2016 Palo Alto Networks, Inc
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

__author__ = 'techbizdev@paloaltonetworks.com'

import logging
import collections

import eventlet
import greenlet
import pan.xapi

import oslo_config.cfg

import dag


LOG = logging.getLogger(__name__)

CONF = oslo_config.cfg.CONF

OPTIONS = [
    oslo_config.cfg.StrOpt(
        'api_username'
    ),
    oslo_config.cfg.StrOpt(
        'api_password'
    ),
    oslo_config.cfg.StrOpt(
        'hostname'
    ),
    oslo_config.cfg.StrOpt(
        'device_tag_prefix',
        default='openstack'
    ),
    oslo_config.cfg.IntOpt(
        'port',
        default=443
    ),
    oslo_config.cfg.BoolOpt(
        'is_panorama',
        default=False
    )
]


class DeviceHandler(object):
    """
    Device handler can handler either panorama or single firewall
    """
    def __init__(self, osstatus):
        self.osstatus = osstatus
        self.osstatus.subscribe(self, event='security_groups')

        self.devices = {}
        self.device_pushers = {}

        self.xapi = pan.xapi.PanXapi(
            api_username=CONF.panwdevice.api_username,
            api_password=CONF.panwdevice.api_password,
            hostname=CONF.panwdevice.hostname,
            port=CONF.panwdevice.port
        )

        self._gthread = None

    def run(self):
        if self._gthread is not None:
            return

        self._gthread = eventlet.spawn(self._run)
        self._gthread.link(self._gthread_exit)

        return self._gthread

    def _collect_tagged_devices_from_panorama(self):
        xpath = "/config/mgt-config/devices"

        self.xapi.show(xpath=xpath)

        devices = self.xapi.element_root.findall('./result/devices/entry')
        LOG.debug(devices)

        result = collections.defaultdict(set)

        for d in devices:
            sn = d.get('name', None)
            if sn is None:
                continue
            LOG.debug('device %s', sn)

            tags = d.findall('./vsys/entry/tags/member')
            LOG.debug('tags: %s', tags)
            for t in tags:
                if t.text is None:
                    continue

                # on Panorama one can decide which devices will receive the notifications based on the tags
                # of the device
                #
                # with a tag openstack-<tenant> the device will receive notifications for  tenant  <tenant>
                # with a tag "openstack-all" the device will receive everything
                if t.text.startswith(CONF.panorama.device_tag_prefix):
                    toks = t.text.split('-', 1)
                    if len(toks) != 2:
                        continue

                    tenant = toks[1]
                    if tenant == 'all':
                        tenant = '*'

                    result[sn].add(tenant)

        return result

    def _gthread_exit(self, gt):
        try:
            gt.wait()

        except:
            LOG.exception("DeviceHandler terminated with exception")

        else:
            return

        LOG.info("respawning greenthread for DeviceHandler")
        self._gthread = eventlet.spawn(self.run)
        self._gthread.link(self._gthread_exit)

    def _run(self):
        while True:
            try:
                if CONF.panwdevice.is_panorama:
                    cur_devices = self._collect_tagged_devices_from_panorama()
                else:
                    result = collections.defaultdict(set)
                    result[CONF.panwdevice.hostname] = "*"
                    cur_devices = result

                oldd = set(self.devices.keys())
                curd = set(cur_devices.keys())

                for d in (oldd - curd):
                    LOG.info("removing DAG pusher for device %s", d)
                    self.device_pushers[d].kill()
                    self.devices.pop(d, None)
                    self.device_pushers.pop(d, None)

                for d in curd:
                    if d in self.devices:
                        if cur_devices[d] != self.devices[d]:
                            LOG.info("set subscriptions to %s for DAG pusher for device %s",
                                     cur_devices[d], d)
                            self.device_pushers[d].put('subscriptions', cur_devices[d])
                            self.devices[d] = cur_devices[d]

                    else:
                        LOG.info("adding DAG pusher for device %s {%s}",
                                 d, cur_devices[d])
                        self.devices[d] = cur_devices[d]
                        if CONF.panwdevice.is_panorama:
                            self.device_pushers[d] = panosdag.dag.DagPusher(d, self.osstatus)
                        else:
                            self.device_pushers[d] = panosdag.dag.DagPusher(None, self.osstatus, CONF.panwdevice.hostname)
                        self.device_pushers[d].put('subscriptions', cur_devices[d])
                        self.device_pushers[d].run()

                eventlet.sleep(60)

            except greenlet.GreenletExit:
                break

            except:
                LOG.exception('Exception in DeviceHandler main loop')
                eventlet.sleep(60)

    def wait(self):
        return self._gthread.wait()
