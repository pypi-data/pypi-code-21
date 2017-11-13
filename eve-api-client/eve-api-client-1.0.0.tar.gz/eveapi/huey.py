import json
import logging

import datetime
import redis
import requests
from django.conf import settings
from django.utils import timezone
from huey.contrib.djhuey import task

from eveapi.esi.errors import ESIErrorLimitReached

logger = logging.getLogger(__name__)
redis = redis.Redis(connection_pool=settings.REDIS_POOL)


def get_cached_url(endpoint):
    data = redis.get(endpoint)
    if data:
        data = json.loads(data.decode('utf-8'))
    return data


def set_url_cache(endpoint, expires, data):
    cached_until = datetime.datetime.strptime(expires, '%a, %d %b %Y %H:%M:%S %Z')
    if not cached_until:
        cached_until = timezone.now() + datetime.timedelta(seconds=300)

    now = timezone.now() - cached_until
    tdelta = cached_until - now
    seconds = int(tdelta.total_seconds())
    data = json.dumps(data)

    redis.setex(endpoint, seconds, data)
    return True


@task(retries=10, retry_delay=settings.ESI_RETRY / 2)
def esi(url, headers, params, method='GET', data=None):
    pause = redis.get('esi_pause')
    if pause:
        logger.warning('error limit hit, retrying soon')
        raise ESIErrorLimitReached(pause)

    logger.info('({}) {}'.format(method, url))

    cached = get_cached_url(url)
    if method == 'GET' and cached:  # retrun cached get response
        return cached

    r = requests.request(method, url, params=params, headers=headers, data=data)

    if int(r.headers['X-Esi-Error-Limit-Remain']) <= 20:
        redis.setex('esi_pause', r.headers['X-Esi-Error-Limit-Reset'], r.headers['X-Esi-Error-Limit-Reset'])

    if int(r.headers['X-Esi-Error-Limit-Remain']) == 0:
        logger.error('ESI error limit hit 0')

    if r.status_code == 200:

        if method == 'GET':  # only cache if get
            set_url_cache(url, r.headers['Expires'], r.json())  # cache response

        data = r.json()
        return data

    else:
        logger.error('ESI request {} error: {} - {}, {}'.format(
            r.url,
            r.status_code,
            r.content,
            r.headers['X-ESI-Error-Limit-Remain']
        ))
        return False
