# panw-dagger

PANW Dagger is a tool that allows for synchronization of the Dynamic Address Groups (DAG) with 3rd party meta-data services (such as OpenStack Nova, OpenStack Neutron, Nuage SDN Controller, etc.).

The current implementation supports:
- OpenStack

## Prerequisites

- git, python-dev, pip

## Installation

    $ sudo -H pip install virtualenv
    $ virtualenv venv
    $ source ./venv/bin/activate
    $ tar -xvzf pan-os-dag-XXX.tar.gz
    $ cd pan-os-dag
    $ python setup.py install
    
## Configuration

Modify 'os-dag.conf' and in particular sections: oslo_messaging_rabbit, openstack, and panwdevice.

## Running

    $ python panosdag/cli.py --config-file ./os-dag.conf


## How it works

The current code:

- retrieve the status of security groups and VMs from Neutron using the 
  Neutron API
- connect to the RabbitMQ instance used as OpenStack message bus, and listen
  to ML2 *security_groups_member_updated* and *port_update* messages
- connect to Panorama and periodically checks for device that should receive
  registered IPs from OpenStack
- push the registered IPs to the selected devices via Panorama

## ML2 messages

Every time there is a change in the members of a security group, ML2 sends
a message to the *q-agent-notifier-security_group-update_fanout* exchange. This
exchange is a *fanout* exchange. Using the oslo.messaging OpenStack library,
the code in panosdag.sg_listener connects to this exchange and triggers a
refresh of the members of that specific security group.

Same applies to the *port_update* message. This message is hooked because if
the security groups applied to a Neutron port are changed after the
initiliazation using the `neutron port-update` command, no *security_groups_member_updated*
message is generated, only a *port_update* message.

## DAG Tags generated

Current code generates the following DAG tags:

- *tag_prefix*-security_group-\<sgid\>
- *tag_prefix*-security_group-\<sgname\>
- *tag_prefix*-tenant-\<tenantid\>
- *tag_prefix*-tenant-\<tenantname\>
- *tag_prefix*-pushed

By default *tag_prefix* is `openstack`. This can be changed from the config file.

Example tags:

    registered IP                             Tags
    ----------------------------------------  -----------------
    
    10.0.0.9 #
                                             "openstack-tenant-demo"
                                             "openstack-security_group-f6af2080-f689-4378-827a-d681d45855db"
                                             "openstack-pushed"
                                             "openstack-tenant-c7d6e954b2a24169a35f7fedd7074d55"
                                             "openstack-security_group-default"
                                             "openstack-security_group-4800c3c1-d05d-474a-93d8-97bb274d7f2c"
                                             "openstack-security_group-sg1"

## Device tags on Panorama

Registered IP messages are routed to target devices via Panorama Device Tags:

- devices with tag *device_tag_prefix*-all receive all the registered IPs
- devices with one or more tag *device_tag_prefix*-\<tenantname\> or 
  *device_tag_prefix*-\<tenantid\> receive only the registered IPs of that 
  specific tenant

By default *device_tag_prefix* is `openstack`.

