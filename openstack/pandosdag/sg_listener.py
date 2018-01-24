import logging

import oslo_config
import oslo_messaging

LOG = logging.getLogger(__name__)

CONF = oslo_config.cfg.CONF


class SecurityGroupUpdateServer(object):
    target = oslo_messaging.Target(version='1.4')

    def __init__(self, osstatus):
        self.osstatus = osstatus

    def __getattr__(self, attr):
        LOG.debug('__getattr__ %s', attr)
        return self._catchall

    def security_groups_member_updated(self, context, **kwargs):
        security_groups = kwargs.get('security_groups', None)
        LOG.info('update security_group %s', security_groups)

        if security_groups is None:
            LOG.info('security_groups_member_updated with no security_groups')
            return

        for sgid in security_groups:
            try:
                ret_msg = self.osstatus.refresh_sg(sgid)
                LOG.debug(ret_msg)

            except:
                LOG.exception('exception refreshing sg %s', sgid)

    def _catchall(self, *args, **kwargs):
        LOG.debug('%s %s', args, kwargs)

def factory(osstatus):
    transport = oslo_messaging.get_transport(CONF)

    endpoints = [
        SecurityGroupUpdateServer(osstatus)
    ]

    targetsg = oslo_messaging.Target(
        # this is the topic we are interested in
        topic='q-agent-notifier-security_group-update',
        server=CONF.host
    )
    serversg = oslo_messaging.get_rpc_server(transport, targetsg, endpoints,
                                             executor='eventlet')
    serversg.start()

    return serversg
