import datetime
import logging
import re
from urllib.parse import quote

import redis
from django.conf import settings
from django.utils import timezone

from eveapi import huey
from eveapi.sso import refresh

logger = logging.getLogger(__name__)
redis = redis.Redis(connection_pool=settings.REDIS_POOL)

base_url = 'https://esi.tech.ccp.is'
oauth_url = 'https://login.eveonline.com/oauth'
token_url = 'https://login.eveonline.com/oauth/token'
authorize_url = 'https://login.eveonline.com/oauth/authorize'


# replace updating db objects with a central token management server at some point
def get_auth(access_token, refresh_token):
    if access_token.created_date < timezone.now() - datetime.timedelta(seconds=access_token.expires_in):
        logger.info('refreshing access token for {}'.format(refresh_token.character.pk))

        tokens = refresh(refresh_token.pk, refresh_token.refresh_token)
        access_token.access_token = tokens['access_token']
        access_token.expires_in = tokens['expires_in']
        access_token.save()

    return '{} {}'.format(refresh_token.token_type, access_token.access_token)


class ESI:
    # for now, take refresh and access tokens as model objects
    def __init__(self, base=None, endpoint=None, method=None, version=None, scopes=None, blocking=True, character=None,
                 access_token=None, refresh_token=None):

        self._endpoint = endpoint

        if base:
            self._version = version or base._version
            self._datasource = base._datasource
            self._method = method or base._method
            self._scopes = scopes or base._scopes
            self._headers = base._headers
            self._blocking = base._blocking
            self._character = base._character

            self._access_token = base._access_token
            self._refresh_token = base._refresh_token

        else:
            self._version = version or 'latest'
            self._datasource = 'tranquility'
            self._method = method or 'GET'
            self._scopes = scopes or []
            self._blocking = blocking
            self._character = character
            self._headers = {
                'User-Agent': 'eve-shekel.com (by Rsgm Vaille)',
                'Accept': 'application/json',
            }

            self._access_token = access_token
            self._refresh_token = refresh_token

    def __str__(self):
        return '{} {}'.format(self._method, '/'.join([
            base_url,
            self._version,
            self._endpoint or '',  # endpoint may be None
        ]))

    def __getattr__(self, attr):
        if attr.startswith('_'):
            logger.error('ESI attr {} starts with _, this should not happen'.format(attr))

        if attr == 'self' and self._character:
            attr = self._character

        elif attr in ['get', 'options', 'head', 'post', 'put', 'patch', 'delete']:
            return ESI(self, self._endpoint, method=attr.upper())

        elif re.match(r'(v\d+|latest|dev|legacy)', attr):
            return ESI(self, self._endpoint, version=attr)

        url = self._endpoint + '/' + str(attr) if self._endpoint else str(attr)  # endpoint may be None
        return ESI(self, url)

    def __getitem__(self, key):
        return self.__getattr__(key)

    def __call__(self, value='', data=None, **kwargs):
        url = '/'.join([
            base_url,
            self._version,
            self._endpoint or '',  # endpoint may be None
            quote(str(value))
        ])
        params = {key: quote(str(value_)) for key, value_ in kwargs.items()}

        if self._access_token:
            self._headers['Authorization'] = get_auth(self._access_token, self._refresh_token)

        task = huey.esi(url, self._headers, params, method=self._method, data=data)

        if self._blocking:
            logger.debug('waiting for ESI task response')
            return task(blocking=self._blocking)
