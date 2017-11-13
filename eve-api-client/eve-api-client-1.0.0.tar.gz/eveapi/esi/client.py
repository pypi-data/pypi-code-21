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

        self.endpoint = endpoint

        if base:
            self.version = version or base.version
            self.datasource = base.datasource
            self.method = method or base.method
            self.scopes = scopes or base.scope
            self.headers = base.headers
            self.blocking = base.blocking
            self.character = base.character

            self.access_token = base.access_token
            self.refresh_token = base.refresh_token

        else:
            self.version = version or 'latest'
            self.datasource = 'tranquility'
            self.method = method or 'GET'
            self.scopes = scopes or []
            self.blocking = blocking
            self.character = character
            self.headers = {
                'User-Agent': 'eve-shekel.com (by Rsgm Vaille)',
                'Accept': 'application/json',
            }

            self.access_token = access_token
            self.refresh_token = refresh_token

    def __str__(self):
        return '{} {}'.format(self.method, '/'.join([
            base_url,
            self.version,
            self.endpoint or '',  # endpoint may be None
        ]))

    def __getattr__(self, attr):
        if attr == 'self' and self.character:
            attr = self.character

        elif attr in ['get', 'options', 'head', 'post', 'put', 'patch', 'delete']:
            return ESI(self, self.endpoint, method=attr.upper())

        elif re.match(r'(v\d+|latest|dev|legacy)', attr):
            return ESI(self, self.endpoint, version=attr)

        url = self.endpoint + '/' + str(attr) if self.endpoint else str(attr)  # endpoint may be None
        return ESI(self, url)

    def __getitem__(self, key):
        return self.__getattr__(key)

    def __call__(self, value='', data=None, **kwargs):
        url = '/'.join([
            base_url,
            self.version,
            self.endpoint or '',  # endpoint may be None
            quote(str(value)),
            ''  # add final /
        ])
        params = {key: quote(str(value_)) for key, value_ in kwargs.items()}

        if self.access_token:
            self.headers['Authorization'] = get_auth(self.access_token, self.refresh_token)

        task = huey.esi(url, self.headers, params, method=self.method, data=data)

        if self.blocking:
            logger.debug('waiting for ESI task response')
            return task(blocking=self.blocking)
