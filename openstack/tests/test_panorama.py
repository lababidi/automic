import unittest
import mock

import greenlet
import eventlet
eventlet.monkey_patch(thread=False)

import logging

import oslo_config

import panos_mock

import pan.xapi
import panosdag.panw_device
import panosdag.dag

LOG = logging.getLogger(__name__)

CONF = oslo_config.cfg.CONF

CONF.register_opts(panosdag.OPTIONS)
CONF.register_opts(panosdag.panw_device.OPTIONS, group='panorama')

CONF.panorama.api_username = 'admin'
CONF.panorama.api_password = 'admin'

class PanoramaHandlerTests(unittest.TestCase):
    @mock.patch.object(panosdag.dag, 'DagPusher')
    @mock.patch.object(pan.xapi, 'PanXapi', side_effect=panos_mock.factory)
    def test_collect(self, pxapi_mock, dp_mock):
        CONF.panorama.hostname = 'test_panorama'

        os = mock.MagicMock()

        p = panosdag.panw_device.DeviceHandler(os)

        result = p._collect_tagged_devices_from_panorama()

        self.assertEqual(len(result), 2)

    @mock.patch.object(eventlet, 'sleep', side_effect=greenlet.GreenletExit())
    @mock.patch.object(panosdag.dag, 'DagPusher')
    @mock.patch.object(pan.xapi, 'PanXapi', side_effect=panos_mock.factory)
    def test_run(self, pxapi_mock, dp_mock, sleep_mock):
        CONF.panorama.hostname = 'test_panorama'

        os = mock.MagicMock()

        p = panosdag.panw_device.DeviceHandler(os)

        p._run()

        self.assertItemsEqual(p.devices.keys(), ['007000004847', '007000004848'])
        self.assertItemsEqual(p.devices['007000004847'], set(['*']))
        self.assertItemsEqual(p.devices['007000004848'], set(['demo']))
        self.assertEqual(len(dp_mock.call_args_list), 2)

    @mock.patch.object(eventlet, 'sleep', side_effect=greenlet.GreenletExit())
    @mock.patch.object(panosdag.dag, 'DagPusher')
    @mock.patch.object(pan.xapi, 'PanXapi', side_effect=panos_mock.factory)
    def test_drun(self, pxapi_mock, dp_mock, sleep_mock):
        CONF.panorama.hostname = 'test_panorama'

        os = mock.MagicMock()

        p = panosdag.panw_device.DeviceHandler(os)

        p._run()

        dp_mock.reset_mock()
        p._run()

        self.assertItemsEqual(p.devices.keys(), ['007000004847', '007000004849'])
        self.assertItemsEqual(p.devices['007000004847'], set(['demo']))
        self.assertItemsEqual(p.devices['007000004849'], set(['demo2']))
        self.assertEqual(len(dp_mock.call_args_list), 1)
