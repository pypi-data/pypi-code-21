import argparse
import asyncio
import concurrent.futures
import json
import numpy
import functools
import logging
import logging.config
import modconf
import pickle
import sys

import ws_storage
import async_patterns.coro_queue
import async_patterns.protocol
import ws_storage.impl.client

import ws_sheets
import ws_sheets_server.packet

logger = logging.getLogger(__name__)

class ServerClientProtocol(async_patterns.protocol.Protocol):
    def __init__(self, loop, app):
        super(ServerClientProtocol, self).__init__(loop)
        self.app = app
        self.app.protos.append(self)

class Script(async_patterns.coro_queue.CoroQueueClass):
    def __init__(self, book, script):
        self.book = book
        self.__script = script
        async_patterns.coro_queue.CoroQueueClass.__init__(self, book.coro_queue, book.loop)

    @async_patterns.coro_queue.CoroQueueClass.wrap
    async def get_string(self):
        return self.__script.get_string()

    @async_patterns.coro_queue.CoroQueueClass.wrap
    async def set_string(self, value):
        self.__script.set_string(value)

    @async_patterns.coro_queue.CoroQueueClass.wrap
    async def get_output(self):
        return self.__script.output

class Sheet(async_patterns.coro_queue.CoroQueueClass):
    def __init__(self, book, sheet):
        self.book = book
        self.__sheet = sheet
        async_patterns.coro_queue.CoroQueueClass.__init__(self, book.coro_queue, book.loop)

    @async_patterns.coro_queue.CoroQueueClass.wrap
    async def getitem(self, args):
        return self.__sheet.__getitem__(args)

    @async_patterns.coro_queue.CoroQueueClass.wrap
    async def setitem(self, args, string):
        return self.__sheet.__setitem__(args, string)

    @async_patterns.coro_queue.CoroQueueClass.wrap
    async def add_row(self, i):
        self.__sheet.add_row(i)
    
    @async_patterns.coro_queue.CoroQueueClass.wrap
    async def add_column(self, i):
        self.__sheet.add_column(i)

    @async_patterns.coro_queue.CoroQueueClass.wrap
    async def convert_cells(self):
        def f(c):
            if c is None:
                return ws_sheets_server.Cell('','')
            
            if False:
                v = c.value
                if isinstance(v, str):
                    v = "\"" + v + "\""
                else:
                    v = str(v)
            else:
                v = c.value
            
            return ws_sheets_server.Cell(c.string, v)

        fv = numpy.vectorize(f, otypes=[ws_sheets_server.Cell])

        return fv(self.__sheet.cells.cells)

class Book(async_patterns.coro_queue.CoroQueueClass):
    def __init__(self, app, loop, id_, book):
        self.app = app
        self.loop = loop
        self.id_ = id_
        self.__book = book

        self.__coro_queue = async_patterns.coro_queue.CoroQueue(loop)
        
        #super(Book, self).__init__(self.__coro_queue)
        async_patterns.coro_queue.CoroQueueClass.__init__(self, self.__coro_queue, loop)
        async_patterns.coro_queue.CoroQueueClass.schedule_run_forever(self)
        
        self.sheets = dict((i, Sheet(self, s)) for i, s in self.__book.sheets.items())

        self.script_pre = Script(self, self.__book.script_pre)
        self.script_post = Script(self, self.__book.script_post)

    def _put(self, f, *args):
        return self.__coro_queue.put_nowait(f, *args)
    
    @async_patterns.coro_queue.CoroQueueClass.wrap
    async def calculate(self):
        task = self.loop.run_in_executor(None, functools.partial(self.__book.do_all))
        return (await task)
    
    @async_patterns.coro_queue.CoroQueueClass.wrap
    async def write(self):
        b = pickle.dumps(self.__book)
        await self.app.storage.write_binary(self.id_, b)

    @async_patterns.coro_queue.CoroQueueClass.wrap
    async def set_docs(self, s):
        self.__book.set_docs(s)

    @property
    def docs(self):
        return self.__book.docs

    async def close(self):
        logger.debug('book close')
        await async_patterns.coro_queue.CoroQueueClass.close(self)

class Application(object):
    """
    Controls server instance.
    This class is an `asynchronous context manager`_.
    
    .. _`asynchronous context manager` https://www.python.org/dev/peps/pep-0492/#asynchronous-context-managers-and-async-with
    """
    def __init__(self, loop, args):
        kwargs = {
                'dev': args.get('dev', False,),
                'port': args.get('port', None),
                'console': args.get('console', False),
                'addr_storage': args.get('addr_storage', None),
                }

        conf = modconf.import_class(args['conf_mod'], 'Conf', tuple(),
                kwargs=kwargs,
                folder=args.get('conf_dir',None))

        logging.config.dictConfig(conf.LOGGING)

        loop.set_debug(True)
    
        self.executor = concurrent.futures.ProcessPoolExecutor()
        
        self.loop = loop
        self.conf = conf
        self.concurrent = concurrent
        self.books = {}

        self.protos = []

    async def get_storage(self):
        addr = self.conf.STORAGE_ADDR
        host, port = addr[0], addr[1]

        self.storage = await ws_storage.impl.client.Storage.create(
                    self.loop,
                    host,
                    port)
        # TODO make sure the effect this deprecated line is performed elsewhere
        #self.storage.set_object_new_args((self.conf.conf_sheets.Settings,))

    async def read_book(self, id_):
        b = await self.storage.read_binary(id_)
        
        book = pickle.loads(b)
        
        assert id_ not in self.books

        bookc = Book(
                self,
                self.loop,
                id_,
                book)

        self.books[id_] = bookc
        return bookc

    async def get_book(self, book_id):
        if book_id in self.books:
            return self.books[book_id]

        book = await self.read_book(book_id)
        return book

    async def book_new(self):
        id_ = await self.storage.next_id()

        assert id_ not in self.books

        bookc = Book(
                self,
                self.loop,
                id_,
                ws_sheets.Book(self.conf.conf_sheets.Settings))

        self.books[id_] = bookc
       
        return id_, bookc

    async def close(self):
        logger.debug('close')
        # Close the server
        self.server.close()
        await self.server.wait_closed()

        logger.debug('close protocols')
        for p in self.protos:
            logger.debug('  {}'.format(repr(p)))
            await p.close()

        logger.debug('close books')
        for book_id, book in self.books.items():
            logger.debug('  {}'.format(book_id))
            await book.close()

    async def __aenter__(self):
        """
        Returns a tuple of ``(app, address)`` where ``address`` is a tuple of ``(host, port)``.
        """
        await self.get_storage()

        self.server = await self.loop.create_server(
                functools.partial(ServerClientProtocol, self.loop, self),
                'localhost', 
                self.conf.PORT)

        addr = self.server.sockets[0].getsockname()

        logger.debug('Serving on {}'.format(addr))

        return self, addr

    async def __aexit__(self, exc_type, exc_value, traceback):
        logger.debug('closing')
        await self.close()

async def async_runserver(loop, args, future):
    async with Application(loop, args) as (app, addr):
        t = args.get('test_timeout', None)
        if t is not None:
            await asyncio.sleep(t)
        else:
            await future
    logger.debug('async_runserver return')

def runserver(args):
    logger = logging.getLogger(__name__)
    
    try:
        loop = asyncio.get_event_loop()
        print('got existing event loop')
        new_loop = False
    except:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        print('got new event loop')
        new_loop = True

    if loop.is_running():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        print('got new event loop')
        new_loop = True


    future = loop.create_future()
    try:
        loop.run_until_complete(async_runserver(loop, args, future))
    except KeyboardInterrupt:
        pass
    
    print('closing event loop')
    
    if new_loop:
        loop.close()



