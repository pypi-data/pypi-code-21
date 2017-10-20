import logging

from raven.contrib.pylons import Sentry

from logilab.common.decorators import monkeypatch
from logilab.common.clcommands import Command
from cubicweb import ConfigurationError
from cubicweb.cwconfig import CubicWebConfiguration
try:
    from pyramid_cubicweb import settings_from_cwconfg, wsgi_application_from_cwconfig
    from cubes.pyramid.ccplugin import PyramidStartHandler
    HAS_PYRAMID = True
except ImportError:
    HAS_PYRAMID = False

logger = logging.getLogger(__name__)

original_main_run = Command.main_run


@monkeypatch(Command, 'main_run')
def sentry_main_run(self, args, rcfile=None):
    try:
        return original_main_run(self, args, rcfile=rcfile)
    except Exception:
        cmd_args = self.load_command_line_configuration(args)
        if cmd_args:
            try:
                config = CubicWebConfiguration.config_for(cmd_args[0])
            except ConfigurationError:
                pass
            else:
                sentry_dsn = config.get('sentry-dsn')
                if sentry_dsn:
                    from raven import Client
                    client = Client(sentry_dsn)
                    extra = {'args': args}
                    ident = client.get_ident(
                        client.captureException(extra=extra))
                    msg = "Exception caught; reference is %s" % ident
                    logger.critical(msg)
        raise

if HAS_PYRAMID:
    @monkeypatch(PyramidStartHandler, 'get_wsgi_app')
    def get_wsgi_app(self, cwconfig):
        app = wsgi_application_from_cwconfig(
            cwconfig, profile=self['profile'],
            profile_output=self['profile-output'],
            profile_dump_every=self['profile-dump-every']
        )
        # TODO - avoid double call to collect_settings
        settings = settings_from_cwconfg(cwconfig)
        if settings.get('sentry.dsn'):
            return Sentry(app, settings)
        else:
            return app
