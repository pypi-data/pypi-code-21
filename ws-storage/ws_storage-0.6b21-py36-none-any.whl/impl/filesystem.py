import asyncio
import os
import pickle
import logging

import ws_storage
import ws_storage.base
import ws_storage.exceptions

logger = logging.getLogger(__name__)

class Storage(ws_storage.base.Storage):
    def __init__(self, conf, loop):
        super(Storage, self).__init__()

        # for the purposes of testing I should create system to create a temp folder for this
        self.dir_ = conf['storage_dir']

    async def _write_binary(self, id_, b):
        logger.debug('_write_binary id={} {} bytes'.format(repr(id_), len(b)))

        try:
            os.makedirs(self.dir_)
        except FileExistsError as e: pass

        filename = os.path.join(self.dir_, str(id_))
        with open(filename, 'wb') as f:
            f.write(b)

    async def _read_binary(self, id_):
        logger.debug('_read_binary({})'.format(id_))

        filename = os.path.join(self.dir_, str(id_))
        
        logger.debug('exists = {}'.format(os.path.exists(filename)))
        
        try:
            with open(filename, 'rb') as f:
                b = f.read()
        except FileNotFoundError:
            raise ws_storage.exceptions.FileNotFound(id_)

        logger.debug('b = {}'.format(repr(b)))

        return b

    async def list_files(self):
        return os.listdir(self.dir_)

    async def _delete(self, id_):
        logger.debug('delete {}'.format(id_))

        filename = os.path.join(self.dir_, str(id_))

        try:
            os.remove(filename)
        except FileNotFoundError:
            raise ws_storage.exceptions.FileNotFound(id_)


