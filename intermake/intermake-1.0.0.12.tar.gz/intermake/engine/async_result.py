from traceback import format_exc
from typing import Callable


__author__ = "Martin Rusilowicz"


class AsyncResult:
    """
    Holds an asynchronous result - or exception.
    """
    def __init__( self, title, result, exception, stacktrace, messages ):
        self.title = title
        self.result = result
        self.exception = exception
        self.traceback = stacktrace
        self.messages = messages
    
    
    @staticmethod
    def construct( fn: Callable[ [ ], object ], title = None ) -> "AsyncResult":
        try:
            result = fn( )
            return AsyncResult( title, result, None, None, None )
        except Exception as ex:
            return AsyncResult( title, None, ex, format_exc(), None )
    
    
    def raise_exception( self ):
        if self.exception:
            raise self.exception
        
    @property
    def success(self):
        return self.exception is None
    
    @property
    def is_error(self):
        return self.exception is not None
    
    @property
    def foremost(self):
        if self.success:
            return self.result
        else:
            return self.exception
    
    
    def __str__( self ):
        if self.success:
            if self.result is None:
                return str(self.title) + " = (Success)"
            else:
                return str(self.title) + " = "+ str( self.result )
        else:
            return str(self.title) + " = (Error:" + str( self.exception )+")"

