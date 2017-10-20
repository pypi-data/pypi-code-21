import asyncio
import aiohttp.abc
import aiohttp.web
from json import dumps

from aiohttp import hdrs
from aiohttp.web_exceptions import HTTPMethodNotAllowed

__all__ = ["View", "Response"]


class Response(aiohttp.web.Response):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class View(aiohttp.abc.AbstractView):
    def __init__(self, request):
        super().__init__(request)
        self.app = request.app

    @asyncio.coroutine
    def __iter__(self):
        if self.request._method not in hdrs.METH_ALL:
            self._raise_allowed_methods()
        method = getattr(self, self.request._method.lower(), None)
        if method is None:
            self._raise_allowed_methods()
        resp = yield from method()
        return resp

    async def options(self):
        return self.response({})

    def __await__(self):
        return (yield from self.__iter__())

    @staticmethod
    def response(body, content_type='text/html', charset='utf-8', status_code=200, **kwargs):
        kwargs.update({'body': body, 'content_type': content_type, 'charset': charset, 'status': status_code})
        if isinstance(body, str):
            kwargs['body'] = body.encode('utf-8')
        elif isinstance(body, dict) or isinstance(body, list):
            kwargs['content_type'] = 'application/json'
            kwargs['body'] = dumps(body).encode('utf-8')
        elif isinstance(body, int) or isinstance(body, float):
            kwargs['body'] = str(body).encode('utf-8')
        return Response(**kwargs)

    def _raise_allowed_methods(self):
        allowed_methods = {
            m for m in hdrs.METH_ALL if hasattr(self, m.lower())}
        raise HTTPMethodNotAllowed(self.request.method, allowed_methods)
