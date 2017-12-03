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

"""
RESTful application support.
"""

import asyncio
import enum
import functools
import json
import logging

from collections import namedtuple

import tornado.web

logger = logging.getLogger(__name__)

class HandlerType(enum.Enum):
    SYNC = 'SYNC'
    ASYNC = 'ASYNC'
    SSE = 'SSE'


HANDLER_METHOD = {
    HandlerType.SYNC: '_handle_request',
    HandlerType.ASYNC: '_handle_request_async',
    HandlerType.SSE: '_handle_request_sse',
}


# HTTP methods, which receive data
DATA_METHODS = {'put', 'post'}


RequestMeta = namedtuple('RequestMeta', (
    'callback', 'mimetype', 'serializer'
))
RequestMeta.__doc__ = """
Request meta data.

URI is mapped to an application function. Two functions can handle requests
with different HTTP methods. Request meta data determines, which
function is the handler and what content type should be returned. For
example `GET` method might return `text/plain`, but `OPTIONS` method might
return JSON data.

Based on `mimetype`, the data serializer is defined.

:var callback: Application function handling business request.
:var mimetype: Response content type.
:var serializer: Response data serializer.

.. seealso:: :py:meth:`RestHandler.add_method`
"""


SERIALIZER = {
    'text/plain': str,
    'application/json': json.dumps,
}

DESERIALIZER = {
    'text/plain': bytes.decode,
    'application/json': lambda s: json.loads(bytes.decode(s)),
}


# FIXME: allow charset override
fmt_content_type = '{}; charset=utf-8'.format


class RestHandler(tornado.web.RequestHandler):
    def on_connection_close(self):
        try:
            self._task.cancel()
        except asyncio.CancelledError:
            pass
        if __debug__:
            logger.debug('client closed connection')


    def _parse_args(self, meta, **args):
        f = meta.callback
        f_ann = f.__annotations__
        parse = lambda k, v: f_ann[k](v) if k in f_ann else v
        args = {k: parse(k, v) for k, v in args.items()}
        return args


    def _parse_args_data(self, meta, **args):
        args['data'] = self.request.body
        args = self._parse_args(meta, **args)
        return args


    def _handle_request(self, parse, meta, **args):
        args = parse(self, meta, **args)
        value = meta.callback(**args)

        content_type = fmt_content_type(meta.mimetype)
        self.set_header('Content-Type', content_type)
        self.write(meta.serializer(value))


    async def _handle_request_async(self, parse, meta, **args):
        args = parse(self, meta, **args)
        self._task = asyncio.ensure_future(meta.callback(**args))
        value = await self._task

        content_type = fmt_content_type(meta.mimetype)
        self.set_header('Content-Type', content_type)
        self.write(meta.serializer(value))


    async def _handle_request_sse(self, parse, meta, **args):
        args = parse(self, meta, **args)

        self.set_header('Content-Type', 'text/event-stream; charset=utf-8')
        self.set_header('Cache-Control', 'no-cache')
        self.set_header('Connection', 'keep-alive')
        self.set_header('X-Accel-Buffering', 'no')

        send_event = functools.partial(
            self._send_event, serializer=meta.serializer
        )
        coro = meta.callback(**args, callback=send_event)
        self._task = asyncio.ensure_future(coro)
        await self._task


    def _send_event(self, content, type='message', serializer=None):
        content = serializer(content)

        data = '\n'.join('data: ' + s for s in content.split('\n'))
        self.write('event: {}\n{}\n\n'.format(type, data))
        self.flush()


    @classmethod
    def copy(cls):
        class Handler(cls): pass
        return Handler


    @classmethod
    def add_method(cls, name, callback, mimetype, handler_type):
        # FIXME: allow to override both mimetype and serialization
        # function, i.e. to support JSON or XML
        mimetype = 'text/plain' if mimetype is None else mimetype
        #serializer = SERIALIZER[mimetype] # FIXME
        serializer = SERIALIZER.get(mimetype, lambda v: v)
        meta = RequestMeta(callback, mimetype, serializer)

        has_data = name in DATA_METHODS
        if has_data:
            parse = cls._parse_args_data

            # set default parser of request body
            f_ann = callback.__annotations__
            if 'data' not in f_ann:
                f_ann['data'] = DESERIALIZER[mimetype]
        else:
            parse = cls._parse_args

        call = getattr(cls, HANDLER_METHOD[handler_type])
        call = functools.partialmethod(call, parse, meta)

        setattr(cls, name, call)


# vim: sw=4:et:ai
