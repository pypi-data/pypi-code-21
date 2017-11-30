from .cli import command, arg

@command('config',
    arg('-p', '--show-password', action="store_true", help="unless specified, password will not be shown")
    )
def config(config):
    """Get or set configuration.

    For configuring the default base

    """
    if config.get('baseurl'):
        config.setConfig()
    else:
        cfg = config.getConfig()
        if cfg.get('password') and not config.get('show-password'):
            cfg['password'] = '******'

        pyaml.p(cfg)
