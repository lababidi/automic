import sys
import logging
import eventlet
eventlet.monkey_patch()
import oslo_config.cfg
import panw_device
import sg_listener
import pu_listener
import openstack

CONF = oslo_config.cfg.CONF
LOG = logging.getLogger(__name__)

def main():
    OPTIONS = [
        oslo_config.cfg.StrOpt(
            'host',
            default='localhost'
        ),
        oslo_config.cfg.StrOpt(
            'tag_prefix',
            default='openstack'
        ),
        oslo_config.cfg.BoolOpt(
            'debug',
            default='false'
        ),
        oslo_config.cfg.StrOpt(
            'device_tag_prefix',
            default='openstack'
        ),
        oslo_config.cfg.StrOpt(
            'api_username',
            default='admin'
        ),
        oslo_config.cfg.StrOpt(
            'hostname',
            default='192.168.1.1'
        )
    ]

    CONF.register_opts(OPTIONS)
    CONF.register_opts(openstack.OPTIONS, group='openstack')
#    CONF.register_opts(panw_device.OPTIONS, group='panwdevice')
    CONF(sys.argv[1:])

    if CONF.debug:
        logging.basicConfig(
            format='%(asctime)s [%(levelname)s] (%(filename)s:%(lineno)d) %(name)s %(message)s',
            datefmt='%Y%m%d %T',
            level=logging.DEBUG)
        CONF.log_opt_values(LOG, logging.INFO)
    else:
        logging.basicConfig(level=logging.INFO)

    openstack_status = openstack.OpenStackStatus()
#    panw_device = panw_device.DeviceHandler(openstack_status)

    LOG.info("retrieving OpenStack status")
    openstack_status.refresh()
    openstack_status.run()

    LOG.info("starting PAN device puller poller")
    panw_device.run()

    LOG.info("starting Port Update and Security Groups Update listeners")
    serversg = sg_listener.factory(openstack_status)
    severpu = pu_listener.factory(openstack_status)

    serversg.wait()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGood bye!")
