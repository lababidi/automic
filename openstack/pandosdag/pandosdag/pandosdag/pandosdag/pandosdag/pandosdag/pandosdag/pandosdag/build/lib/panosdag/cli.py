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
    CONF.register_opts(OPTIONS)
    CONF.register_opts(openstack.OPTIONS, group='openstack')
    CONF.register_opts(panosdag.panw_device.OPTIONS, group='panwdevice')
    CONF(sys.argv[1:])

    if CONF.debug:
        logging.basicConfig(
            format='%(asctime)s [%(levelname)s] (%(filename)s:%(lineno)d) %(name)s %(message)s',
            datefmt='%Y%m%d %T',
            level=logging.DEBUG)
        CONF.log_opt_values(LOG, logging.INFO)
    else:
        logging.basicConfig(level=logging.INFO)

    openstack_status = panosdag.openstack.OpenStackStatus()
    panw_device = panosdag.panw_device.DeviceHandler(openstack_status)

    LOG.info("retrieving OpenStack status")
    openstack_status.refresh()
    openstack_status.run()

    LOG.info("starting PAN device puller poller")
    panw_device.run()

    LOG.info("starting Port Update and Security Groups Update listeners")
    serversg = panosdag.sg_listener.factory(openstack_status)
    severpu = panosdag.pu_listener.factory(openstack_status)

    serversg.wait()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGood bye!")
