import datetime
import logging
import re
from urllib.parse import quote

import redis
from django.conf import settings
from django.utils import timezone

from eveapi import huey
from eveapi.esi.errors import ESIPermissionRevoked
from eveapi.sso import refresh

logger = logging.getLogger(__name__)
redis = redis.Redis(connection_pool=settings.REDIS_POOL)

base_url = 'https://esi.tech.ccp.is'
oauth_url = 'https://login.eveonline.com/oauth'
token_url = 'https://login.eveonline.com/oauth/token'
authorize_url = 'https://login.eveonline.com/oauth/authorize'


class ESI:
    # for now, take refresh and access tokens as model objects
    def __init__(self, base=None, endpoint=None, method=None, user_agent=None, version=None, blocking=True,
                 character=None, auth_callback=None):

        if base:
            self._endpoint = endpoint or base._endpoint
            self._version = version or base._version
            self._datasource = base._datasource
            self._method = method or base._method
            self._headers = base._headers
            self._blocking = base._blocking
            self._character = character or base._character
            self._auth_callback = auth_callback or base._auth_callback

        else:
            self._version = version or 'latest'
            self._datasource = 'tranquility'
            self._method = method or 'GET'
            self._blocking = blocking
            self._character = character
            self._auth_callback = auth_callback
            self._headers = {
                'User-Agent': user_agent,
                'Accept': 'application/json',
            }

            if not user_agent:
                raise Exception('User agent required')

    def __str__(self):
        return '{} {}'.format(self._method, '/'.join([
            base_url,
            self._version,
            self._endpoint or '',  # endpoint may be None
        ]))

    def __getattr__(self, attr):
        """
        Adds to the esi path.

        If attr is an http method name, it will set the method attribute instead.
        Similarly, this sets the version.
        This allows you to reuse esi clients as a base for multiple routes that may need different methods or esi versions.

        Example:
            ```
            client = ESI(authtokens, etc.).v1.fleets[id]
            a = client.v2.members
            b = client.wings
            c = b.post()
            ```
        """
        if attr.startswith('_'):  # this gets called if you misspell an attribute
            logger.error('ESI attr {} starts with _, this should not happen'.format(attr))

        if attr == 'self' and self._character:  # replace self with auth character id
            attr = self._character

        elif attr in ['get', 'options', 'head', 'post', 'put', 'patch', 'delete']:  # set http method
            return ESI(self, method=attr.upper())

        elif re.match(r'(v\d+|latest|dev|legacy)', attr):  # set esi version instead of adding to the path
            return ESI(self, version=attr)

        url = self._endpoint + '/' + str(attr) if self._endpoint else str(attr)  # endpoint may be None
        return ESI(self, url)

    def __getitem__(self, key):
        return self.__getattr__(str(key))

    def __call__(self, value='', data=None, fetch_pages=False, **kwargs):
        url = '/'.join([
            base_url,
            self._version,
            self._endpoint or '',  # endpoint may be None
            quote(str(value))
        ])
        params = {key: quote(str(value_)) for key, value_ in kwargs.items()}

        task = huey.esi(
            self._method,
            url,

            self._headers,
            params,
            data,
            fetch_pages,

            self._auth_callback
        )

        if self._blocking:
            logger.debug('waiting for ESI task response')
            return task(blocking=self._blocking)

    def _fork(self, **kwargs):
        return ESI(self, **kwargs)
