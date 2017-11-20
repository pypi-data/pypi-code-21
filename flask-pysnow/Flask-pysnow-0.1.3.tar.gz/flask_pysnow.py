# -*- coding: utf-8 -*-

"""
    flask_pysnow
    ~~~~~~~~~~~~

    Adds pysnow (ServiceNow) support to Flask

    More information:
    https://github.com/rbw0/flask-pysnow
    https://github.com/rbw0/pysnow
"""

__author__ = "Robert Wikman <rbw@vault13.org>"
__version__ = "0.1.3"

from flask import current_app

try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack

from pysnow import Client, OAuthClient


class Pysnow(object):
    """Central controller class that can be used to configure how
    Flask-pysnow behaves.  Each application that wants to use Flask-pysnow
    has to create, or run :meth:`init_app` on, an instance of this class
    after the configuration was initialized.
    """

    def __init__(self, app=None):
        self.app = app

        if app is not None:
            self.init_app(app)

    def init_app(self, app, **kwargs):
        """Set up this instance for use with *app*, if no app was passed to
        the constructor.
        """

        app.config.setdefault('PYSNOW_INSTANCE', None)
        app.config.setdefault('PYSNOW_HOST', None)
        app.config.setdefault('PYSNOW_USER', None)
        app.config.setdefault('PYSNOW_PASSWORD', None)
        app.config.setdefault('PYSNOW_OAUTH_CLIENT_ID', kwargs.get('client_id', None))
        app.config.setdefault('PYSNOW_OAUTH_CLIENT_SECRET', kwargs.get('client_secret', None))
        app.config.setdefault('PYSNOW_REQUEST_PARAMS', {})
        app.config.setdefault('PYSNOW_ENABLE_LOGGING', True)
        app.config.setdefault('PYSNOW_USE_SSL', True)
        app.config.setdefault('PYSNOW_RAISE_ON_EMPTY', False)

    def get_connection(self, session=None):
        """Creates new client object or returns an existing one

        :param session: optional requests-compatible session object
        :return: Pysnow Client
        """

        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, 'pysnow_client'):
                return Client(instance=current_app.config['PYSNOW_INSTANCE'],
                              host=current_app.config['PYSNOW_HOST'],
                              user=current_app.config['PYSNOW_USER'],
                              password=current_app.config['PYSNOW_PASSWORD'],
                              raise_on_empty=current_app.config['PYSNOW_RAISE_ON_EMPTY'],
                              request_params=current_app.config['PYSNOW_REQUEST_PARAMS'],
                              use_ssl=current_app.config['PYSNOW_USE_SSL'],
                              session=session)

            return ctx.pysnow_client

    def get_oauth_connection(self, token=None, token_updater=None, client_id=None, client_secret=None):
        """Creates a new client with OAuth extras

        :param token: optional - token to set before returning client instance
        :param token_updater: optional - token_updater to set upon creating client instance
        :param client_id: optional - OAuth provider client_id, overrides PYSNOW_OAUTH_CLIENT_ID
        :param client_secret: optional - OAuth provider client_secret, overrides PYSNOW_OAUTH_CLIENT_SECRET
        :return: pysnow OAuthClient
        """

        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, 'pysnow_oauth_client'):
                c_client_id = current_app.config['PYSNOW_OAUTH_CLIENT_ID']
                c_client_secret = current_app.config['PYSNOW_OAUTH_CLIENT_SECRET']
                ctx.pysnow_client = OAuthClient(instance=current_app.config['PYSNOW_INSTANCE'],
                                                host=current_app.config['PYSNOW_HOST'],
                                                user=current_app.config['PYSNOW_USER'],
                                                password=current_app.config['PYSNOW_PASSWORD'],
                                                raise_on_empty=current_app.config['PYSNOW_RAISE_ON_EMPTY'],
                                                request_params=current_app.config['PYSNOW_REQUEST_PARAMS'],
                                                token_updater=token_updater,
                                                client_id=client_id or c_client_id,
                                                client_secret=client_secret or c_client_secret,
                                                use_ssl=current_app.config['PYSNOW_USE_SSL'])

            ctx.pysnow_client.set_token(token)
            return ctx.pysnow_client
