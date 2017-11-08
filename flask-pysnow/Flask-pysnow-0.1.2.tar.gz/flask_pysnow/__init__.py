# -*- coding: utf-8 -*-

"""
    flask_pysnow
    ~~~~~~~~~~~~

    Adds pysnow (ServiceNow) support to Flask

"""

__author__ = "Robert Wikman <rbw@vault13.org>"
__version__ = "0.1.2"

import logging

from flask import current_app
from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session
from .client import PysnowClient
from ._logging import ContextualFilter

try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack


class Pysnow(object):
    def __init__(self, app=None, refresh_token=None, access_token=None):
        """Takes tokens later used to create an OAuth session (if enabled in config)

        :param app: Flask app
        :param refresh_token: refresh token (if OAuth enabled in config)
        :param access_token: access token (if OAuth enabled in config)
        """

        self.app = app
        self.refresh_token = refresh_token
        self.access_token = access_token

        self.logger = None
        self._session = None

        if app is not None:
            self.init_app(app)

    def _get_oauth_session(self, oauth):
        """Takes oauth config (tokens and URL) and returns a session compatible with pysnow

        :param oauth: Dict containing tokens and OAuth URL
        :return: pysnow / requests compatible session object
        """
        oauth_session = OAuth2Session(
            client=LegacyApplicationClient(client_id=oauth['client_id']),
            token={
                "refresh_token": self.refresh_token,
                "access_token": self.access_token
            },

            auto_refresh_url=oauth['url'],
            auto_refresh_kwargs={
                "client_id": oauth['client_id'],
                "client_secret": oauth['client_secret']
            })

        return oauth_session

    def init_app(self, app):
        app.config.setdefault('PYSNOW_INSTANCE', None)
        app.config.setdefault('PYSNOW_HOST', None)
        app.config.setdefault('PYSNOW_USER', None)
        app.config.setdefault('PYSNOW_PASSWORD', None)
        app.config.setdefault('PYSNOW_OAUTH', None)
        app.config.setdefault('PYSNOW_REQUEST_PARAMS', {})
        app.config.setdefault('PYSNOW_ENABLE_LOGGING', True)
        app.config.setdefault('PYSNOW_USE_SSL', True)
        app.config.setdefault('PYSNOW_RAISE_ON_EMPTY', False)

        # Logging was requested, set it up
        if app.config['PYSNOW_ENABLE_LOGGING'] is True:
            self.logger = logging.getLogger('flask_pysnow')
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("[PYSNOW %(levelname)s %(asctime)s] %(message)s , "
                                                   "instance: %(instance)s, token: %(token)s, user: %(user)s"))

            self.logger.addFilter(ContextualFilter(user=app.config['PYSNOW_USER'],
                                                   token=self.refresh_token,
                                                   instance=app.config['PYSNOW_INSTANCE']))
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.DEBUG)

    # Convenience function
    def query(self, *args, **kwargs):
        return self.connection.query(*args, **kwargs)

    # Convenience function
    def insert(self, *args, **kwargs):
        return self.connection.insert(*args, **kwargs)

    # Pysnow client instantiation
    def _create_client(self):
        if current_app.config['PYSNOW_OAUTH'] is not None:
            # Make sure user passed the expected tokens
            if not self.access_token or not self.refresh_token:
                raise Exception("Pysnow was configured to use oauth, "
                                "but access_token and refresh_token hasn't been set")

            self._session = self._get_oauth_session(current_app.config['PYSNOW_OAUTH'])

        return PysnowClient(instance=current_app.config['PYSNOW_INSTANCE'],
                            host=current_app.config['PYSNOW_HOST'],
                            user=current_app.config['PYSNOW_USER'],
                            password=current_app.config['PYSNOW_PASSWORD'],
                            raise_on_empty=current_app.config['PYSNOW_RAISE_ON_EMPTY'],
                            request_params=current_app.config['PYSNOW_REQUEST_PARAMS'],
                            use_ssl=current_app.config['PYSNOW_USE_SSL'],
                            session=self._session,
                            logger=self.logger)

    @property
    def connection(self):
        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, 'pysnow_client'):
                ctx.pysnow_client = self._create_client()

            return ctx.pysnow_client
