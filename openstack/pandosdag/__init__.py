__version__ = "0.1.1"

try:
    import oslo_config.cfg

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
        )
    ]

except ImportError:
    pass
