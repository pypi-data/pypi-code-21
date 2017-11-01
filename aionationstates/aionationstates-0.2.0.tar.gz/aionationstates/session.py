import logging
from warnings import warn
from collections import namedtuple
import xml.etree.ElementTree as ET

import aiohttp

from aionationstates import __version__
from aionationstates import ratelimit
from aionationstates.types import (
    RateLimitError, SessionConflictError, AuthenticationError, NotFound)


NS_URL = 'https://www.nationstates.net/'
API_PATH = 'cgi-bin/api.cgi'
API_URL = NS_URL + API_PATH

logger = logging.getLogger('aionationstates')


class ApiQuery:
    """A request to the NationStates API.

    Although you, as a user, will never need to interact with this
    class "directly," it is quite a bit more than an implementation
    detail.

    It it here to provide a way to combine multiple API shards into a
    single HTTP request.

    To achieve that, it overloads the ``+`` operator.  By "adding"
    ApiQueries together, you get an ApiQuery which, when awaited, will
    return a tuple of what the original ApiQueries would have
    returned by themselves.  Let me illustrate.

    This code::

        name = await nation.name()
        population = await nation.population()
        wa = await nation.wa()

    is functionally equivalent to this::

        name, population, wa = await (
            nation.name() + nation.population() + nation.wa())

    with the tiny difference that the latter sample sends but a single
    HTTP request to the API, as opposed to the former, which bombards
    the poor server hamsters with all three.

    As you may have already realized at this point, combining shards
    into a single request this way is preferable, and you should do
    that in your code wherever possible.

    .. note::

        Standard NS rules for combining shards still apply.  Code such
        as this is not going to work::

            nation.name() + region.name()
            # ValueError: ApiQueries do not share the same session

            nation.census() + nation.censushistory()
            # ValueError: ApiQueries contain conflicting params
    """
    def __init__(self, *, session, result, q, params=None):
        self.session = session
        self.results = [result]
        self.q = set(q)
        self.params = params or {}

    def __await__(self):
        return self._wrap().__await__()

    async def _wrap(self):
        self.params['q'] = '+'.join(self.q)
        resp = await self.session._call_api(self.params)
        root = ET.fromstring(resp.text)
        results = [
            await result(self.session, root)
            for result in self.results
        ]
        return results[0] if len(results) == 1 else tuple(results)

    def __add__(self, other):
        if self.session is not other.session:
            raise ValueError('ApiQueries do not share the same session')
        if set(self.params) & set(other.params):
            raise ValueError('ApiQueries contain conflicting params')

        self.q |= other.q
        self.params.update(other.params)
        self.results += other.results
        return self


def api_query(*q, **params):
    def decorator(func):
        def wrapper(self):
            return ApiQuery(session=self, q=q,
                            params=params, result=func)
        # Can't use @functools.wraps because it would preserve the signature,
        # meaning we would get nonsense arguments intended for the decorator.
        wrapper.__doc__ = func.__doc__
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator


def api_command(c, **data):
    def decorator(func):
        async def wrapper(session):
            data['c'] = c
            resp = await session._call_api_command(data)
            root = ET.fromstring(resp.text)
            return await func(session, root)
        wrapper.__doc__ = func.__doc__
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator


def set_user_agent(user_agent: str) -> None:
    Session._USER_AGENT = user_agent


# Needed because aiohttp's API is weird and every my attempt at making
# a proper use of it has led to sadness and despair.
RawResponse = namedtuple('RawResponse', ('status url text'
                                         ' cookies headers'))


class Session:
    _USER_AGENT = None

    async def _request(self, method, url, headers=None, cookies=None, **kwargs):
        headers = headers or {}

        standard_user_agent = f'aionationstates/{__version__}'
        if not self._USER_AGENT:
            warn('Please supply a useragent by calling aionationstates.'
                 'set_user_agent("your useragent here")')
            headers['User-Agent'] = standard_user_agent
        else:
            headers['User-Agent'] = \
                f'{self._USER_AGENT} ({standard_user_agent})'

        async with aiohttp.ClientSession(cookies=cookies) as session:
            async with session.request(method, url, allow_redirects=False,
                                       headers=headers, **kwargs) as resp:
                return RawResponse(
                    status=resp.status,
                    url=resp.url,
                    cookies=resp.cookies,
                    headers=resp.headers,
                    text=await resp.text()
                )

    @ratelimit.api
    async def _base_call_api(self, method, **kwargs):
        logger.debug(f'Calling API {method} {kwargs}')
        resp = await self._request(method, API_URL, **kwargs)
        if resp.status == 403:
            raise AuthenticationError
        if resp.status == 429:
            raise RateLimitError(
                f'ratelimited for {resp.headers["X-Retry-After"]} seconds')
        if resp.status == 409:
            raise SessionConflictError('previous login too recent')
        if resp.status == 404:
            raise NotFound
        assert resp.status == 200
        return resp

    async def _call_api(self, params, **kwargs):
        return await self._base_call_api('GET', params=params, **kwargs)

    @ratelimit.web
    async def _call_web(self, path, *, method='GET', **kwargs):
        logger.debug(f'Calling web {method} {path} {kwargs}')
        resp = await self._request(method, NS_URL + path.strip('/'), **kwargs)
        if '<html lang="en" id="page_login">' in resp.text:
            raise AuthenticationError
        assert resp.status == 200
        return resp
