import datetime
import json
import logging

import redis
import requests
from django.conf import settings
from django.utils import timezone
from huey.contrib.djhuey import task

from eveapi.esi.errors import ESIErrorLimitReached, ESIPermissionRevoked
from eveapi.sso import refresh

TIMEOUT = 10000

logger = logging.getLogger(__name__)
redis = redis.Redis(connection_pool=settings.REDIS_POOL)


def get_auth(access_token, refresh_token):
    if access_token.created_date < timezone.now() - datetime.timedelta(seconds=access_token.expires_in):
        logger.info('refreshing access token for {}'.format(refresh_token.character.pk))

        if refresh_token.revoked_permission:
            raise ESIPermissionRevoked()

        try:
            tokens = refresh(refresh_token.pk, refresh_token.refresh_token)
        except ESIPermissionRevoked:
            refresh_token.revoked_permission = True
            refresh_token.save()
            raise

        access_token.access_token = tokens['access_token']
        access_token.expires_in = tokens['expires_in']
        access_token.save()

    return '{} {}'.format(refresh_token.token_type, access_token.access_token)


def cache_response(endpoint, expires, data):
    if expires:
        cached_until = timezone.make_aware(datetime.datetime.strptime(expires, '%a, %d %b %Y %H:%M:%S %Z'))
        time_delta = cached_until - timezone.now()
        seconds = int(time_delta.total_seconds())
    else:
        seconds = 300  # default to 5 minutes

    data = json.dumps(data)
    redis.setex(endpoint, data, seconds)
    return True


@task(retries=5, retry_delay=settings.ESI_RETRY / 2)
def esi(method, url, headers, params, data, fetch_pages, access_token, refresh_token):
    # check for esi_pause to esi rate limit
    pause = redis.get('esi_api_client_pause')
    if pause:
        logger.warning('error limit hit, retrying soon')
        raise ESIErrorLimitReached(pause)

    logger.info('({}) {}'.format(method, url))

    # check for cached request
    cached = redis.get(url)
    if method == 'GET' and cached:  # retrun cached get response
        logger.info('Cached ESI call')
        return json.loads(cached.decode('utf-8'))

    # set auth header and refresh token if necessary
    if access_token:
        headers['Authorization'] = get_auth(access_token, refresh_token)

    # set page number
    if fetch_pages and fetch_pages > 1:
        params['page'] = fetch_pages  # unspecified gives the first page in esi

    # make request
    r = requests.request(method, url, params=params, headers=headers, data=data, timeout=TIMEOUT)

    # check ESI error rate limiting
    if int(r.headers['X-Esi-Error-Limit-Remain']) <= 20:
        redis.setex('esi_api_client_pause', r.headers['X-Esi-Error-Limit-Reset'], r.headers['X-Esi-Error-Limit-Reset'])

    if r.status_code == 200:
        response_data = r.json()

        # load multiple pages if able to
        total_pages = int(r.headers.get('x-pages', 1))
        if fetch_pages and total_pages > 1:
            pages = [
                esi(method, url, headers, params, data, access_token, refresh_token, fetch_pages=p + 1)
                for p in range(total_pages - 1)
            ]
            for page in pages:
                data = page.get(blocking=True)  # block to get result
                response_data.extend(data.json())  # assume both are lists

        # cache if get request
        if method == 'GET':
            cache_response(r.url, r.headers.get('Expires', None), r.json())  # cache response

        return response_data

    else:
        # remake request if token was expired
        if r.json()['error'] == 'expired':
            return esi(method, url, headers, params, data, fetch_pages, access_token, refresh_token).get(blocking=True)

        # log error for esi rate limiting
        if int(r.headers['X-Esi-Error-Limit-Remain']) == 0:
            logger.error('ESI error limit hit 0')

        logger.error('ESI request {} error: {} - {}, {}'.format(
            r.url,
            r.status_code,
            r.content,
            r.headers['X-ESI-Error-Limit-Remain']
        ))
        return False
