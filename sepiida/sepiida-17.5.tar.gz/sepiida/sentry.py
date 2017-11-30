import logging

import flask
import raven.base
import raven.utils.conf
from raven.contrib.flask import Sentry
from werkzeug.contrib.fixers import ProxyFix

import sepiida.environment

LOGGER = logging.getLogger(__name__)

def handle_reverse_proxy(app):
    LOGGER.info("Adding support for nginx reverse proxy fix in sentry")
    app.wsgi_app = ProxyFix(app.wsgi_app)

class SepiidaSentry(Sentry):
    def get_user_info(self, request):
        if hasattr(flask.g, 'current_user'):
            return flask.g.current_user

def add_sentry_support(application, sentry_dsn, version, tags=None):
    tags = tags or {}
    settings = sepiida.environment.get()
    options = raven.utils.conf.convert_options(application.config, defaults={
        'dsn'   : sentry_dsn,
        'include_paths' :
            set(application.config.get('SENTRY_INCLUDE_PATHS', [])) | set([application.import_name]),
        'extra' : {
            'app' : application,
        },
        # The above is taken from sentry's flask contrib module
        'environment'   : settings.ENVIRONMENT,
        'release'       : version,
        'site'          : settings.SERVER_NAME,
        'tags'          : tags,
    })

    client = raven.base.Client(**options)
    sentry = SepiidaSentry(app=application, client=client, dsn=sentry_dsn, logging=True, level=logging.ERROR)
    application.config.setdefault('RAVEN', sentry)
    logging.getLogger('webargs.flaskparser').setLevel(logging.CRITICAL)
    return sentry
