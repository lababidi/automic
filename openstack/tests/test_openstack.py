import unittest
import mock

import logging

import oslo_config

import panosdag.openstack

LOG = logging.getLogger(__name__)

CONF = oslo_config.cfg.CONF

CONF.register_opts(panosdag.OPTIONS)
CONF.register_opts(panosdag.openstack.OPTIONS, group='openstack')

CONF.openstack.username = 'admin'
CONF.openstack.password = 'supersecret'
CONF.openstack.auth_url = 'http://192.168.0.67:35357/v2.0'
CONF.openstack.tenant_name = 'admin'


class OpenStackStatusTests(unittest.TestCase):
    def test_refresh(self):
        os = panosdag.openstack.OpenStackStatus()
        os.refresh()

        self.assertEqual(len(os.sg_details), 2)
        self.assertEqual(len(os.tenant_details), 4)
        self.assertEqual(len(os.sg_members), 2)

    def test_refresh_sg(self):
        os = panosdag.openstack.OpenStackStatus()
        os.refresh()

        os2 = panosdag.openstack.OpenStackStatus()
        print os2.refresh_sg(os.sg_details.keys()[0])

    def test_delta(self):
        os = panosdag.openstack.OpenStackStatus()
        os.refresh()

        print os.delta([])
