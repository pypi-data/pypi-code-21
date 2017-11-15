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
def esi(url, headers, params, method='GET', data=None):
    pause = redis.get('esi_pause')
    if pause:
        logger.warning('error limit hit, retrying soon')
        raise ESIErrorLimitReached(pause)

    logger.info('({}) {}'.format(method, url))

    cached = redis.get(url)
    if method == 'GET' and cached:  # retrun cached get response
        logger.info('Cached ESI call')
        return json.loads(cached.decode('utf-8'))

    r = requests.request(method, url, params=params, headers=headers, data=data)

    if int(r.headers['X-Esi-Error-Limit-Remain']) <= 20:
        redis.setex('esi_pause', r.headers['X-Esi-Error-Limit-Reset'], r.headers['X-Esi-Error-Limit-Reset'])

    if int(r.headers['X-Esi-Error-Limit-Remain']) == 0:
        logger.error('ESI error limit hit 0')

    if r.status_code == 200:

        if method == 'GET':  # only cache if get
            cache_response(url, r.headers.get('Expires', None), r.json())  # cache response

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
