import time
import urllib
import urlparse
from abc import ABCMeta, abstractmethod
from email.utils import parsedate_tz, mktime_tz

import requests

from .endpoints import API_ENDPOINT_URLS, EASE_ENDPOINT_URLS
from ..exceptions import APIError, reraise


class AuthenticationStore(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get(self):
        pass  # pragma: no cover

    @abstractmethod
    def set(self, value):
        pass  # pragma: no cover


class DictAuthenticationStore(AuthenticationStore):
    def __init__(self, data=None):
        self.data = data or {}

    def get(self):
        return self.data

    def set(self, value):
        self.data = value


class Authenticator(object):
    def __init__(self, client_id, client_secret, redirect_url, store=None, endpoint='live'):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_url = redirect_url
        self.endpoint = endpoint
        if store is None:
            store = DictAuthenticationStore()
        self.store = store

    @property
    def ease_endpoint_url(self):
        return EASE_ENDPOINT_URLS[self.endpoint]

    @property
    def api_endpoint_url(self):
        return API_ENDPOINT_URLS[self.endpoint]

    @property
    def authorization_url(self):
        """
        Retrieve the Lingo24 URL which the user should visit in order to
        login and grant OAuth2 access. Upon completion, the user will be
        redirected back to the specified `redirect_url`.

        When redirected, the URL will include the **AUTHORIZATION CODE** as a
        GET parameter. This value should be passed to the `request_access_token`
        method in order to obtain the **ACCESS TOKEN**.
        """
        query = urllib.urlencode({
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_url,
        })
        return urlparse.urljoin(self.ease_endpoint_url, 'oauth/authorize?{}'.format(query))

    @property
    def access_token(self):
        if self.access_token_expired:
            self.refresh_access_token()
        try:
            return self.store.get()['access_token']
        except KeyError:
            raise ValueError(
                "No access token available. Ensure the authenticator's "
                "request_access_token method has been called with a valid "
                "OAuth2 authorization code."
            )

    @property
    def access_token_expired(self):
        """
        Returns `True` if there is an access token in the store and it has
        expired; otherwise `False`.
        """
        try:
            expires_at = self.store.get()['expires_at']
        except KeyError:
            return False
        return expires_at < time.time()

    def request_access_token(self, authorization_code):
        self._request_oauth2_access(
            grant_type='authorization_code',
            code=authorization_code,
        )

    def refresh_access_token(self):
        self._request_oauth2_access(
            grant_type='refresh_token',
            refresh_token=self.store.get()['refresh_token'],
        )

    def _request_oauth2_access(self, **kwargs):
        query = urllib.urlencode(dict(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_url,
            **kwargs
        ))
        url = urlparse.urljoin(self.api_endpoint_url, 'oauth2/access?{}'.format(query))
        try:
            response = requests.post(url)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            reraise(APIError)
        try:
            now = mktime_tz(parsedate_tz(response.headers['Date']))
        except (KeyError, TypeError):
            now = int(time.time())
        json_response = response.json()
        self.store.set({
            'access_token': json_response['access_token'],
            'refresh_token': json_response['refresh_token'],
            'expires_in': json_response['expires_in'],
            'expires_at': now + json_response['expires_in'],
        })
