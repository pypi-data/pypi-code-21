import struct
import logging

import ws_storage.exceptions

logger = logging.getLogger(__name__)

class Storage(object):
    """
    """
    async def _read_binary(self, id_):
        """
        to be defined by implementation
        """
        pass

    async def _write_binary(self, id_, b):
        """
        to be defined by implementation
        """
        pass

    async def _delete(self, id_):
        raise NotImplemented

    async def list_files(self):
        """
        To be defined by implementation.

        Return a list of the names of all stored files.
        """
        pass

    def __init__(self):
        self._cache = {}

    async def next_id(self):
        logger.debug('next_id')
        try:
            b = await self.read_binary('_counter')
        except ws_storage.exceptions.FileNotFound:
            i = 0
        except Exception as e:
            logger.error(e)
            raise
        else:
            t = struct.unpack('<L', b)
            logger.debug('unpacked = {}'.format(t))
            i = t[0] + 1

        await self.write_binary('_counter', struct.pack('<L', i))
        
        return str(i)

    async def read_binary(self, id_):
        if not id_ in self._cache:
            b = await self._read_binary(id_)
            self._cache[id_] = b
        
        return self._cache[id_]

    async def write_binary(self, id_, b):
        self._cache[id_] = b
        await self._write_binary(id_, b)

    async def delete(self, id_):
        if id_ in self._cache:
            del self._cache[id_]

        await self._delete(id_)



