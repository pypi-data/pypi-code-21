import numpy
import traceback
import sys
import io
import logging
import contextlib

logger = logging.getLogger(__name__)
loggerScript = logging.getLogger(__name__+'/script')

import ws_sheets.context

class Script(object):
    def __init__(self, book):
        self.book = book
        self.__string = ""
        self.output = ""
    
    def __getstate__(self):
        state = {'string': self.__string}
        #return dict((k, getattr(self, k)) for k in ["__string"])
        return state
    	
    def __setstate__(self, state):
        self.__string = state['string']

    def set_string(self,s):
        logger.debug('\n' + '-'*10 + '\n' + self.__string + '\n' + '-'*10+ ' \n' + s)
        
        if s == self.__string:
            logger.debug('script string unchanged')
            return False
        
        logger.debug('script string changed')
        
        self.__string = s
        self.comp()
        return True

    def get_string(self):
        return self.__string    

    def comp(self):
        logger.debug('{} compile'.format(self.__class__.__name__))
	
        try:
            self.code = compile(self.__string, '<script>', 'exec')
        except Exception as e:
            self.code = None
            self.comp_exc = e

            l = traceback.format_exc().split("\n")
            #l.pop(1)
            #l.pop(1)
            self.output = "\n".join(l)
            return
        else:
            self.comp_exc = None

        try:
            self.book.middleware_security.call_check_script_code(self)
        except ws_sheets.exception.NotAllowedError as e:
            self.code = None
            self.comp_exc = e
    
    def execute1(self, g):
        code = self.code

        """
        try:
            with sheets.context.script_exec(self.book, self):
                exec(code, g)
        except Exception as e:
            print(e)
            #traceback.print_exc()
            return e
        """
        with ws_sheets.context.context(self.book, ws_sheets.context.Context.SCRIPT):
            try:
                #exec(code, g)
                self.book.middleware_security.call_script_exec(self.book, self, self.code, g)
            except Exception as e:
                logger.debug(e)
            
                exc_string = traceback.format_exc().split('\n')
            	#exc_string.pop(1)
            	#exc_string.pop(1)
                exc_string = "\n".join(exc_string)
                #traceback.print_exc()
                return e, exc_string

        return None, ''

    def execute(self, g):
        logger.debug('script evaluate')

        assert(self.book.context == ws_sheets.context.Context.NONE)

        if not hasattr(self, "code"): self.comp()

        if self.code is None: return

        out = io.StringIO()
        
        """
        old = sys.stdout
        sys.stdout = out
        try:
            exec(self.code, g)
        except Exception as e:
            sys.stdout = old

            self.exec_exc = e

            exc_string = traceback.format_exc().split('\n')
            #exc_string.pop(1)
            #exc_string.pop(1)
            exc_string = "\n".join(exc_string)
        else:
            sys.stdout = old
            self.exec_exc = None
            exc_string = ''

        """

        with contextlib.redirect_stdout(out):
            self.exec_exc, exc_string = self.execute1(g)

        self.output = out.getvalue() + "".join(exc_string)

        logger.debug('string = {}'.format(repr(self.__string)))
        logger.debug('output = {}'.format(repr(self.output)))
    
    def jkhkjfskaf():
        # inspect the cells global
        try:
            cells = self.glo["cells"]

            print()
            print("after script exec")
            print("cells")
            print(repr(cells))

            if not isinstance(cells, numpy.ndarray):
                raise TypeError("cells is not a numpy array")

            print("ndim:", repr(cells.ndim))

            if cells.ndim != 2:
                raise TypeError("cells does not have dimension of 2")

            print("dtype:", repr(cells.dtype))

            if cells.dtype != numpy.dtype("<U1"):
                raise TypeError("cells dtype is not '<U1'")

        except Exception as e:
            print(e)





