import asyncio
import functools
import pickle
import logging

logger = logging.getLogger(__name__)

import ws_storage.packet
import async_patterns.protocol
import ws_storage.exceptions

class Storage(ws_storage.base.Storage, async_patterns.protocol.Protocol):
    """
    This implementation of the Storage interface is also an asyncio Protocol

    :param loop: asyncio event loop

    .. note: This object has a cache and the server storage object will have a cache.
    """
    def __init__(self, loop):
        ws_storage.base.Storage.__init__(self)
        async_patterns.protocol.Protocol.__init__(self, loop)
        self.loop = loop

    async def _read_binary(self, id_):
        p = ws_storage.packet.ReadBinary(id_)
        resp = await self.write(p)

        if isinstance(resp, ws_storage.packet.FileNotFound):
            raise ws_storage.exceptions.FileNotFound(id_)

        return resp.b

    async def _delete(self, id_):
        p = ws_storage.packet.Delete(id_)
        resp = await self.write(p)

        if isinstance(resp, ws_storage.packet.FileNotFound):
            raise ws_storage.exceptions.FileNotFound(id_)

    async def _write_binary(self, id_, b):
        p = ws_storage.packet.WriteBinary(id_, b)
        self.write(p)

    async def list_files(self):
        p = ws_storage.packet.ListFiles()
        resp = await self.write(p)
        logger.debug('resp={}'.format(resp))
        return resp.files

    @classmethod
    async def create(cls, loop, host, port):
        """
        :param loop: asyncio event loop
        :param str host: host
        :param int port: port
        :return: Storage object
        """
        coro = loop.create_connection(
            functools.partial(cls, loop),
            host, 
            port)
        
        _, protocol = await coro
        
        return protocol
        
