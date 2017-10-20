import asyncio
import functools
import logging
import numpy

logger = logging.getLogger(__name__)

class Script(object):
    def __init__(self):
        pass

class Cells(object):
    def __init__(self, proto):
        self.proto = proto
        self.up_to_date = False
        
        self.proto.callback_on_write.add_callback(functools.partial(self.set_up_to_date, False))

    def set_up_to_date(self, up_to_date):
        logger.debug('set_up_to_date{}'.format((up_to_date,)))
        self.up_to_date = up_to_date

class DescCells(object):

    def __get__(self, obj, objtype):
        """
        :param obj: a Sheet object
        """
        logger.debug('DescCells.__get__{} up_to_date={}'.format((self, obj, objtype), obj._cells.up_to_date))

        if not obj._cells.up_to_date:
            fut = obj.proto.request_sheet_data(obj.id_)
            logger.debug('fut = {}'.format(fut))
            res = obj.proto.loop.run_until_complete(fut)
            logger.debug('res = {}'.format(res))
        
        return obj._cells.cells
    
    def __set__(self, obj, val):
        logger.debug('DescCells.__set__{}'.format((self, obj, str(val)[:16]+'...')))
        obj._cells.cells = val
        obj._cells.up_to_date = True

class Book(object):
    def __init__(self, proto):
        self.proto = proto
        self.sheets = {}
        self.script_pre = Script()
        self.script_post = Script()

    def __getitem__(self, sheet_id):
        if not sheet_id in self.sheets:
            self.sheets[sheet_id] = Sheet(sheet_id, self.proto)
        return self.sheets[sheet_id]

class Sheet(object):
    cells = DescCells()

    def __init__(self, id_, proto):
        self.id_ = id_
        self.proto = proto
        self._cells = Cells(proto)
    
    def add_row(self, i):
        self.proto.add_row(self.id_, i)
     
    def add_column(self, i):
        self.proto.add_column(self.id_, i)
   
    async def get_cells(self):
        if not self._cells.up_to_date:
            fut = self.proto.request_sheet_data(self.id_)
            resp = await fut
            logger.debug('resp={}'.format(resp))
            await resp._task_acall
        
        return self._cells.cells

    async def getitem(self, args):
        def f(c):
            if c is None: return None
            return c.value
        
        cells = await self.get_cells()

        try:
            a = numpy.vectorize(f, otypes=[object])(cells.__getitem__(args))
        except IndexError as e:
            logger.error('{}\n shape = {}'.format(e, numpy.shape(self.cells)))
            raise

        return a

    def __getitem__(self, args):
        def f(c):
            if c is None: return None
            return c.value
        
        try:
            a = numpy.vectorize(f, otypes=[object])(self.cells.__getitem__(args))
        except IndexError as e:
            logger.error('{}\n shape = {}'.format(e, numpy.shape(self.cells)))
            raise

        return a

    def __setitem__(self, *args):
        logger.debug('{} setitem'.format(*args))
        object.__setitem__(self, *args)


