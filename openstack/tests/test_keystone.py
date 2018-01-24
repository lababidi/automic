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

__author__ = 'Ivan Bojer'

import logging
import sys
import oslo_config
from keystoneclient.v2_0 import client
#from keystoneclient.v3 import client

CONF = oslo_config.cfg.CONF

LOG = logging.getLogger(__name__)

def main():
    kclient = client.Client(
                username=CONF.openstack.username,
                password=CONF.openstack.password,
                tenant_name=CONF.openstack.tenant_name,
                auth_url=CONF.openstack.auth_url,
                insecure=CONF.openstack.insecure_ssl,
                debug=True
    )

    #auth_ref = kclient.auth_ref
    #new_client = client.Client(auth_ref=auth_ref)
    #admin_token='B5ZRf2BT'
    #new_client = client.Client(
                                # token=admin_token,
                                # endpoint=CONF.openstack.auth_url,
                                # insecure=CONF.openstack.insecure_ssl,debug=True)

    #tenants = new_client.tenants.list()
    tenants = kclient.tenants.list()
    for tenant in tenants:
        print tenant



if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s [%(levelname)s] (%(filename)s:%(lineno)d) %(name)s %(message)s',
        datefmt='%Y%m%d %T',
        level=logging.DEBUG)

    OPTIONS = [
        oslo_config.cfg.StrOpt(
            'host',
            default='localhost'
        ),
        oslo_config.cfg.StrOpt(
            'tag_prefix',
            default='openstack'
        ),
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

    CONF.register_opts(OPTIONS)
    CONF.register_opts(OPTIONS, group='openstack')
    CONF.register_opts(OPTIONS, group='panorama')
    CONF(sys.argv[1:])
    CONF.log_opt_values(LOG, logging.INFO)

    main()
