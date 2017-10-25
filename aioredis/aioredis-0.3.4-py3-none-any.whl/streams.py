import asyncio
from asyncio import (
    StreamReaderProtocol,
    StreamReader as BaseReader,
    StreamWriter
    )

from .parser import Reader

_DEFAULT_LIMIT = 2 ** 16


@asyncio.coroutine
def open_connection(host=None, port=None, *,
                    loop=None, limit=_DEFAULT_LIMIT,
                    parser=None, **kwds):
    if loop is None:
        loop = asyncio.get_event_loop()
    reader = StreamReader(limit=limit, parser=parser, loop=loop)
    protocol = StreamReaderProtocol(reader, loop=loop)
    transport, _ = yield from loop.create_connection(
        lambda: protocol, host, port, **kwds)
    writer = StreamWriter(transport, protocol, reader, loop)
    return reader, writer


class StreamReader(BaseReader):

    def __init__(self, limit=_DEFAULT_LIMIT, parser=None, loop=None):
        super().__init__(limit, loop=loop)
        if parser is None:
            parser = Reader
        self._parser = parser()

    def feed_data(self, data):
        assert not self._eof, "feed_data after feed_eof"
        if not data:
            return

        self._parser.feed(data)
        self._wakeup_waiter()

        # TODO: implement pause_reading

    @asyncio.coroutine
    def read_response(self):
        if self._exception is not None:
            raise self._exception
        resp = self._parser.gets()
        while resp is False:
            yield from self._wait_for_data('read_response')
            resp = self._parser.gets()
        return resp
