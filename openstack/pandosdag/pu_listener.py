import logging

import oslo_config
import oslo_messaging

LOG = logging.getLogger(__name__)

CONF = oslo_config.cfg.CONF


class PortUpdateServer(object):
    target = oslo_messaging.Target(version='1.4')

    def __init__(self, osstatus):
        self.osstatus = osstatus

    def __getattr__(self, attr):
        LOG.debug('__getattr__ %s', attr)
        return self._catchall

    def port_update(self, context, **kwargs):
        port_id = kwargs.get('port', None)
        LOG.info('update port %s', port_id)

        if port_id is None:
            LOG.info('port_update with no port_id')
            return

        try:
            LOG.debug(self.osstatus.refresh_port(port_id))

        except:
            LOG.exception('exception refreshing port %s', port_id)

    def _catchall(self, *args, **kwargs):
        LOG.debug('%s %s', args, kwargs)

def factory(osstatus):
    transport = oslo_messaging.get_transport(CONF)

    endpoints = [
        PortUpdateServer(osstatus)
    ]

    targetsg = oslo_messaging.Target(
        topic='q-agent-notifier-port-update',
        server=CONF.host
    )
    serversg = oslo_messaging.get_rpc_server(transport, targetsg, endpoints,
                                             executor='eventlet')
    serversg.start()

    return serversg
