
import asyncio
import logging

import ws_storage
import ws_storage.exceptions

logger = logging.getLogger(__name__)

class Packet(object):
    def __init__(self, response_to=None):
        if response_to is not None:
            self.response_to = response_to

    async def __call__(self, proto):
        pass

class WriteBinary(Packet):
    def __init__(self, id_, o):
        self.id_ = id_
        self.o = o

    async def __call__(self, proto):
        logger.debug('{} call'.format(self.__class__.__name__))

        await proto.app.write_binary(self.id_, self.o)

class ReadBinary(Packet):
    def __init__(self, id_):
        self.id_ = id_

    async def __call__(self, proto):
        logger.debug('{} call'.format(self.__class__.__name__))
        
        try:
            b = await proto.app.read_binary(self.id_)
        except ws_storage.exceptions.FileNotFound:
            logger.info('sending FileNotFound')
            proto.write(FileNotFound(self.id_, self.message_id))
            return
        except Exception as e:
            logger.error('error in ReadBinary call: {}'.format(e))
            proto.write(ServerError(repr(e), self.message_id))
            raise

        logger.debug('read {} bytes'.format(len(b)))

        proto.write(ResponseReadBinary(self.id_, b, self.message_id))

class ServerError(Packet):
    def __init__(self, msg, response_to):
        self.msg = msg
        self.response_to = response_to

class Delete(Packet):
    def __init__(self, id_):
        self.id_ = id_

    async def __call__(self, proto):
        logger.debug('{} call'.format(self.__class__.__name__))
        
        try:
            b = await proto.app.delete(self.id_)
        except ws_storage.exceptions.FileNotFound:
            logger.info('sending FileNotFound')
            proto.write(FileNotFound(self.id_, self.message_id))
            return
        except Exception as e:
            logger.error('error in Delete call: {}'.format(e))
            proto.write(ServerError(repr(e), self.message_id))
            raise

        proto.write(Packet(self.message_id))

class FileNotFound(Packet):
    def __init__(self, id_, response_to):
        self.id_ = id_
        self.response_to = response_to

class ResponseReadBinary(Packet):
   def __init__(self, id_, b, response_to):
        self.id_ = id_
        self.b = b
        self.response_to = response_to

class ListFiles(Packet):
    async def __call__(self, proto):
        logger.debug('{} call'.format(self.__class__.__name__))

        l = await proto.app.list_files()

        logger.debug('l={}'.format(l))

        proto.write(ResponseListFiles(l, self.message_id))

class ResponseListFiles(Packet):
    def __init__(self, files, response_to):
        self.files = files
        self.response_to = response_to


