import os
import asyncio
import functools
import logging
import logging.config

logger = logging.getLogger(__name__)

import toml

import async_patterns
import async_patterns.protocol
import async_patterns.coro_queue
import ws_storage.impl.as3
import ws_storage.impl.filesystem

class ServerClientProtocol(async_patterns.protocol.Protocol):
    def __init__(self, loop, app):
        logger.debug('{} created'.format(self.__class__.__name__))
        super(ServerClientProtocol, self).__init__(loop)
        logger.debug('super initialized')
        self.app = app

class Application(async_patterns.coro_queue.CoroQueueClass):
    """
    Storage Server

    This class is an async context manager.

    Parameters:

    - dev ``bool``
    - console ``bool``
    - port ``int``
    
    :param loop: event loop
    :param args: dictionary of parameters
    """
    def __init__(self, loop, args):
        self.loop = loop
        self.args = args

        super(Application, self).__init__(loop=loop)
        
    @async_patterns.CoroQueueClass.wrap
    async def write_binary(self, id_, b):
        return (await self.storage.write_binary(id_, b))

    @async_patterns.CoroQueueClass.wrap
    async def read_binary(self, id_):
        res = await self.storage.read_binary(id_)

        if isinstance(res, Exception):
            raise res
    
        logger.debug('read binary id = {} len = {} bytes'.format(repr(id_), len(res)))

        return res

    @async_patterns.CoroQueueClass.wrap
    async def delete(self, id_):
        res = await self.storage.delete(id_)
        
        if isinstance(res, Exception):
            raise res
        
        logger.debug('delete. id = {}'.format(repr(id_)))
        
    @async_patterns.CoroQueueClass.wrap
    async def list_files(self):
        return (await self.storage.list_files())

    async def close(self):
        await super(Application, self).close()
        
        self.server.close()
        await self.server.wait_closed()

    def create_storage(self):
        factory = {
                'FILESYSTEM': ws_storage.impl.filesystem.Storage,
                'AS3': ws_storage.impl.as3.Storage,}
        logger.debug('impl={}'.format(repr(self.conf['implementation'])))
        self.storage = factory[self.conf['implementation']](self.conf, self.loop)
    
    async def __aenter__(self):
        loop, args = self.loop, self.args


        #self.conf = modconf.import_class(
        #        args['conf_mod'], 
        #        'Conf', 
        #        tuple(),
        #        kwargs={
        #            'dev': args.get('dev', False),
        #            'port': args['port'],
        #            'impl': args.get('impl','AS3'),
        #            'conf_dir': args.get('conf_dir', None),
        #            },
        #        folder=args.get('conf_dir', None))
        
        with open('ws_storage.toml') as f:
            self.conf = toml.loads(f.read())
        
        self.create_storage()

        try:
            os.makedirs(os.path.dirname(self.conf['logging']['handlers']['file']['filename']))
        except FileExistsError:
            pass

        logging.config.dictConfig(self.conf['logging'])
    
        coro = loop.create_server(
                functools.partial(ServerClientProtocol, loop, self),
                'localhost', 
                self.conf['port'])
        
        logger.debug('start server')
        self.server = await coro
    
        addr = self.server.sockets[0].getsockname()
        port = addr[1]
        
        logger.debug('serving on {}'.format(addr))
        logger.debug('port = {}'.format(port))
        logger.debug('ws_storage version = {}'.format(ws_storage.__version__))
        
        return self, addr
    
    async def __aexit__(self, exc_type, exc, tb):
        #def stop(loop, app):
        logger.debug('closing')
        # Close the server
        await self.close()

    def __enter__(self):
        return self.loop.run_until_complete(self.__aenter__())

    def __exit__(self, exc_type, exc, tb):
        return self.loop.run_until_complete(self.__aexit__(exc_type, exc, tb))

async def arunserver(future, loop, args):
    async with Application(loop, args) as app:
        await future

def runserver(args):
    loop = asyncio.get_event_loop()
    
    future = loop.create_future()

    try:
        # run forever
        loop.run_until_complete(arunserver(future, loop, args))
    except KeyboardInterrupt:
        logger.debug('got keyboard interrupt')
    except Exception as e:
        logger.error(e)



