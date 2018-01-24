import unittest
import mock

import eventlet
eventlet.monkey_patch(thread=False)

import logging

import pan.xapi

import oslo_config

import panosdag.dag
import panosdag.panw_device

import panos_mock

LOG = logging.getLogger(__name__)

CONF = oslo_config.cfg.CONF

CONF.register_opts(panosdag.OPTIONS)
CONF.register_opts(panosdag.panw_device.OPTIONS, group='panorama')

CONF.panorama.api_username = 'admin'
CONF.panorama.api_password = 'admin'
CONF.panorama.hostname = 'test_dag'


class DagPusherTests(unittest.TestCase):
    def test_uid_message(self):
        RESULT = '<uid-message><version>1.0</version><type>update</type><payload><register><entry ip="192.168.1.1"><tag><member>a</member><member>b</member></tag></entry></register><unregister><entry ip="192.168.1.2"><tag><member>c</member><member>d</member></tag></entry></unregister></payload></uid-message>'

        os = mock.MagicMock()
        dp = panosdag.dag.DagPusher('DEADBEEF', os)

        register = {
            '192.168.1.1': ['a', 'b']
        }

        unregister = {
            '192.168.1.2': ['c', 'd']
        }

        msg = dp._build_dag_message([register, unregister])

        self.assertEqual(msg, RESULT)

    @mock.patch.object(pan.xapi, 'PanXapi', side_effect=panos_mock.factory)
    def test_get_all_registered_ips(self, panxapi_mock):
        os = mock.MagicMock()

        dp = panosdag.dag.DagPusher('DEADBEEF', os)

        rips = dp._get_all_registered_ips()

        self.assertItemsEqual(rips.keys(), ['1.1.1.1', '1.1.1.2'])
        self.assertItemsEqual(rips['1.1.1.1'], ['openstack-a'])
        self.assertItemsEqual(rips['1.1.1.2'], ['openstack-b'])

    @mock.patch.object(pan.xapi, 'PanXapi', side_effect=panos_mock.factory)
    def test_push_change(self, panxapi_mock):
        RESULT = '<uid-message><version>1.0</version><type>update</type><payload><register><entry ip="192.168.1.1"><tag><member>a</member><member>b</member></tag></entry></register><unregister><entry ip="192.168.1.2"><tag><member>c</member><member>d</member></tag></entry></unregister></payload></uid-message>'

        os = mock.MagicMock()
        dp = panosdag.dag.DagPusher('DEADBEEF', os)

        register = {
            '192.168.1.1': ['a', 'b']
        }

        unregister = {
            '192.168.1.2': ['c', 'd']
        }

        dp._push_change([register, unregister])

        self.assertEqual(dp.xapi.last_user_id, RESULT)
