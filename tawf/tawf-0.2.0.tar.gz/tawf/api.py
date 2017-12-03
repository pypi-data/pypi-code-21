#
# TAWF ain't web framework.
#
# Copyright (C) 2015 by Artur Wroblewski <wrobell@pld-linux.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import asyncio
import logging
import re
from collections import OrderedDict
from enum import Enum
from functools import partial

from .handler import RestHandler, HandlerType

import tornado.web
from tornado.platform.asyncio import AsyncIOMainLoop

logger = logging.getLogger(__name__)

# detect route argument
RE_ARG = re.compile(r'{([A-Za-z_0-9]+)}')

# check if path is going to be dynamic route
has_args = RE_ARG.search

# convert path having arguments into a regular expression string
path_convert = partial(RE_ARG.sub, r'(?P<\1>[^/]+)')


class Method(Enum):
    """
    HTTP method.

    See `http://www.w3.org/Protocols/rfc2616/rfc2616-sec9.html`_.
    """
    GET = 'GET'
    OPTIONS = 'OPTIONS'
    PUT = 'PUT'
    POST = 'POST'


class Application(tornado.web.Application):
    """
    Web application based on Tornado web server application.
    """
    def __init__(self, *args, **kw):
        """
        Create instance of an application.

        The constructor parameters are the same as of `tornado.web.Application`
        class.
        """
        super().__init__(*args, **kw)
        self._handlers = OrderedDict()


    def listen(self, port, address='', **kwargs):
        AsyncIOMainLoop().install()
        self.add_handlers('.*', self._handlers.values())
        if __debug__:
            logger.debug('handlers: {}'.format(self._handlers))
        super().listen(port, address, **kwargs)


    def route(self, path, method=Method.GET, mimetype=None):
        """
        Function decorator to map URI to a function.

        :param path: URI specification.
        :param method: HTTP method or collection of HTTP methods.
        :param mimetype: Mimetype of value returned by function.
        """
        if __debug__:
            logger.debug('route uri {} for method {}'.format(path, method))

        def wrapper(f):
            methods = (method, ) if isinstance(method, Method) else method
            is_async = asyncio.iscoroutinefunction(f)
            handler_type = HandlerType.ASYNC if is_async else HandlerType.SYNC
            self._add_uri_handler(path, f, methods, mimetype, handler_type)
            return f
        return wrapper


    def sse(self, path, mimetype=None):
        """
        Function decorator to map URI path to a coroutine serving data with
        Server-Sent Event messages.

        :param path: URI specification.
        :param mimetype: Mimetype of values sent by coroutine.
        """
        if __debug__:
            logger.debug('server-sent event at {}'.format(path))

        def wrapper(f):
            self._add_uri_handler(path, f, (Method.GET,), mimetype, HandlerType.SSE)
            return f
        return wrapper


    def _add_uri_handler(self, path, f, methods, mimetype, handler_type):
        for m in methods:
            p = '^' + path_convert(path) + '$'
            if p not in self._handlers:
                self._handlers[p] = (p, RestHandler.copy())
            cls = self._handlers[p][1]
            cls.add_method(m.value.lower(), f, mimetype, handler_type)


# vim: sw=4:et:ai
