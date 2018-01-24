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

import greenlet
import eventlet
import eventlet.queue
import pan.xapi

import oslo_config.cfg

LOG = logging.getLogger(__name__)

CONF = oslo_config.cfg.CONF


class DagPusher(object):
    def __init__(self, serial_number, osstatus, fw_addr=None):
        if serial_number and fw_addr:
            LOG.fatal("Only one of serial_number or fw_addr can be defined")
            raise SyntaxError("Only one of serial_number or fw_addr can be defined")

        LOG.info("DAG pusher for %s created", serial_number)

        self.serial_number = serial_number
        self.fw_addr = fw_addr
        self.osstatus = osstatus

        if not fw_addr:
            self.device_id = serial_number
            self.xapi = pan.xapi.PanXapi(
                api_username=CONF.panwdevice.api_username,
                api_password=CONF.panwdevice.api_password,
                hostname=CONF.panwdevice.hostname,
                port=CONF.panwdevice.port,
                serial=self.serial_number
            )
        else:
            self.device_id = fw_addr
            self.xapi = pan.xapi.PanXapi(
                api_username=CONF.panwdevice.api_username,
                api_password=CONF.panwdevice.api_password,
                port=CONF.panwdevice.port,
                hostname=self.fw_addr
            )

        self._gthread = None

        self.subscriptions = set()
        self.q = eventlet.queue.LightQueue()

    def _gthread_exit(self, gt):
        LOG.debug("_gthread_exit called for %s", self.device_id)
        try:
            gt.wait()

        except greenlet.GreenletExit:
            LOG.info("DagPusher %s killed", self.device_id)
            return

        except:
            LOG.exception("exception in main loop of DagPusher %s", self.device_id)

        LOG.info("respawning DAG pusher for %s in 30 seconds", self.device_id)
        eventlet.sleep(30)

        self._gthread = eventlet.spawn(self._run)
        self._gthread.link(self._gthread_exit)

    def _build_dag_message(self, delta):
        register, unregister = delta

        if len(register) + len(unregister) == 0:
            return None

        message = [
            "<uid-message>",
            "<version>1.0</version>",
            "<type>update</type>",
            "<payload>"
        ]

        if len(register) != 0:
            message.append('<register>')
            for a, tags in register.iteritems():
                message.append('<entry ip="%s">' % a)

                if tags is not None:
                    message.append('<tag>')
                    for t in tags:
                        LOG.info('TAG %s with %s', a, t)
                        message.append('<member>%s</member>' % t)
                    message.append('</tag>')

                message.append('</entry>')
            message.append('</register>')

        if len(unregister) != 0:
            message.append('<unregister>')
            for a, tags in unregister.iteritems():
                message.append('<entry ip="%s">' % a)

                if tags is not None:
                    message.append('<tag>')
                    for t in tags:
                        LOG.info('UNTAG %s from %s', a, t)
                        message.append('<member>%s</member>' % t)
                    message.append('</tag>')

                message.append('</entry>')
            message.append('</unregister>')

        message.append('</payload></uid-message>')

        return ''.join(message)

    def _push_change(self, delta):
        msg = self._build_dag_message(delta)
        if msg is None:
            return

        while True:
            try:
                self.xapi.user_id(cmd=msg)

            except greenlet.GreenletExit:
                raise

            except pan.xapi.PanXapiError as e:
                if 'already exists, ignore' in e.message or \
                   'does not exist, ignore' in e.message:
                    LOG.debug('exception from PAN-OS API: %s', e.message)
                    break

                LOG.exception("exception pushing change to %s", self.device_id)
                eventlet.sleep(30)

            except:
                LOG.exception("exception pushing change to %s", self.device_id)
                eventlet.sleep(30)

            else:
                break

    def _get_all_registered_ips(self):
        while True:
            try:
                self.xapi.op(
                    cmd='show object registered-ip all',
                    cmd_xml=True
                )

            except greenlet.GreenletExit:
                raise

            except:
                LOG.exception("exception in DagPusher %s", self.device_id)
                eventlet.sleep(30)

            else:
                break

        entries = self.xapi.element_root.findall('./result/entry')
        if not entries:
            return {}

        addresses = {}
        for entry in entries:
            ip = entry.get("ip")

            members = entry.findall("./tag/member")

            tags = set([member.text for member in members
                       if member.text and member.text.startswith(CONF.tag_prefix)])

            if len(tags) > 0:
                addresses[ip] = (tags if len(tags) != members else None)

        return addresses

    def _change_subscriptions(self, subs2):
        subs = set(subs2)
        removed = self.subscriptions - subs
        added = subs - self.subscriptions

        cur_rips = self._get_all_registered_ips()
        cur_rips = ['%s@%s' % (rip, tag)
                    for rip in cur_rips.keys()
                    for tag in cur_rips[rip]]

        for r in removed:
            self.osstatus.unsubscribe(self, r)

        tids = subs
        if tids == { '*' }:
            tids = None

        delta = self.osstatus.delta(cur_rips, tenant_ids=tids)
        self._push_change(delta)

        for a in added:
            self.osstatus.subscribe(self, a)

    def _run(self):
        while True:
            try:
                cmd, args = self.q.get()

                if cmd == 'change':
                    LOG.debug('change command in %s', self.device_id)
                    self._push_change(args)

                elif cmd == 'subscriptions':
                    LOG.debug('subscriptions command in %s', self.device_id)
                    self._change_subscriptions(args)

                else:
                    LOG.error('unkown command in DagPusher %s: %s', self.device_id, cmd)

            except greenlet.GreenletExit:
                raise

            except:
                LOG.exception('exception in main loop of DagPusher %s', self.device_id)
                eventlet.sleep(30)

    def run(self):
        self._gthread = eventlet.spawn(self._run)
        self._gthread.link(self._gthread_exit)

    def put(self, command, args):
        self.q.put([command, args])

    def kill(self):
        LOG.info("kill request to DAG pusher for device %s", self.device_id)
        for s in self.subscriptions:
            self.osstatus.unsubscribe(self, s)

        self._gthread.kill()
