import datetime
import json
import logging

import redis
import requests
from django.conf import settings
from django.utils import timezone
from huey.contrib.djhuey import task

from eveapi.esi.errors import ESIErrorLimitReached

TIMEOUT = 5000

logger = logging.getLogger(__name__)
redis = redis.Redis(connection_pool=settings.REDIS_POOL)


def get_cache_url(url, params):
    """
    Appends the parameters to the url.
    This is used to cache urls with specific parameters.
    Parameters are sorted by key names since parameters are unordered.

    This may not generate valid urls, this should only be used for redis keys.
    """
    params = map(lambda param: str(param[0]) + '=' + str(param[1]), params.items())  # join param key/value pairs
    params = '&'.join(sorted(params))  # sort since dicts can be in any order, sort by key
    return url + '?' + params


def error_limit_retry(delay=settings.ESI_RETRY, *args, **kwargs):
    """
    Schedule another esi task after the esi error limit reset ends then return the result.
    """
    return esi.schedule(
        args=args,
        kwargs=kwargs,
        delay=delay,
    ).get(blocking=True)


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


@task(retries=5, retry_delay=5)
def esi(method, url, headers, params, data, fetch_pages, auth_callback, page=False):
    logger.info('({}) {}'.format(method, url))

    # set page number
    if page:
        params['page'] = page  # unspecified gives the first page in esi

    # check for cached request
    cached = redis.get(get_cache_url(url, params))
    if method == 'GET' and cached:  # retrun cached get response
        logger.info('Cached ESI call')
        return json.loads(cached.decode('utf-8'))

    # check for esi_api_client_delay to esi rate limit
    delay = redis.ttl('esi_api_client_delay')
    if delay and delay > 0:
        logger.warning('error limit hit, retrying soon')
        return error_limit_retry(auth_callback, data, fetch_pages, headers, method, page, params, url, delay=delay)

    # set auth header using auth_callback
    if auth_callback:
        headers['Authorization'] = auth_callback

    # make request
    r = requests.request(method, url, params=params, headers=headers, data=data, timeout=TIMEOUT)

    # check ESI error rate limiting
    if int(r.headers['X-Esi-Error-Limit-Remain']) <= 20:
        redis.setex('esi_api_client_delay', r.headers['X-Esi-Error-Limit-Reset'], r.headers['X-Esi-Error-Limit-Reset'])

    if r.status_code == 200:
        response_data = r.json()

        # load multiple pages if able to
        total_pages = int(r.headers.get('x-pages', 1))
        if fetch_pages and total_pages > 1:
            pages = [
                esi(method, url, headers, params, data, False, auth_callback, page=p + 2)  # +2 since 1-based indexing
                for p in range(total_pages - 1)
            ]
            for page_request in pages:
                data = page_request.get(blocking=True)  # block to get result
                response_data.extend(data)  # assume both are lists

        # cache response if get request
        if method == 'GET':  # assume fetch_pages and save the full data list for page=false
            cache_response(get_cache_url(url, params), r.headers.get('Expires', None), response_data)

        return response_data

    else:
        # remake request if token was expired
        if r.json()['error'] == 'expired':
            return esi(method, url, headers, params, data, fetch_pages, auth_callback, page=page).get(blocking=True)

        # log error for esi rate limiting
        if int(r.headers['X-Esi-Error-Limit-Remain']) == 0:
            logger.error('ESI error limit hit 0')
            return error_limit_retry(auth_callback, data, fetch_pages, headers, method, page, params, url)

        logger.error('ESI request {} error: {} - {}, {}'.format(
            r.url,
            r.status_code,
            r.content,
            r.headers['X-ESI-Error-Limit-Remain']
        ))
        raise Exception('ESI error')
