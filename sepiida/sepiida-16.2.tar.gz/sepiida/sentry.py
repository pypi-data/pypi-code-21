import logging

import flask
from raven.contrib.flask import Sentry
from werkzeug.contrib.fixers import ProxyFix

LOGGER = logging.getLogger(__name__)

def handle_reverse_proxy(app):
    LOGGER.info("Adding support for nginx reverse proxy fix in sentry")
    app.wsgi_app = ProxyFix(app.wsgi_app)

class SepiidaSentry(Sentry):
    def get_user_info(self, request):
        if hasattr(flask.g, 'current_user'):
            return flask.g.current_user

def add_sentry_support(application, sentry_dsn, version):
    raven = SepiidaSentry(app=application, dsn=sentry_dsn, logging=True, level=logging.ERROR)
    raven.client.release = version
    application.config.setdefault('RAVEN', raven)
    logging.getLogger('webargs.flaskparser').setLevel(logging.CRITICAL)
    return raven
