from typing import Union


class Logger:
    def __init__( self, name: Union[ str, bool ], enabled: bool = None ):
        if isinstance( name, bool ) and enabled is None:
            enabled = name
            name = "untitled"
        
        if name:
            self.__prefix = name + ": "
        else:
            self.__prefix = ""
        
        if not enabled:
            self.__print = self.__print_nowhere
        else:
            self.__print = print
    
    
    def __print_nowhere( self, *args, **kwargs ):
        pass
    
    
    def __call__( self, *args, **kwargs ):
        if len( args ) == 1:
            self.print( args[ 0 ] )
        elif len( args ) > 1:
            self.print( args[ 0 ].format( *args[ 1: ] ) )
        
        return self
    
    
    def print( self, message ):
        self.__print( self.__prefix + message )
    
    
    def indent( self ):
        self.__prefix += "    "
        
        if len( self.__prefix ) > 100:
            from mhelper.exception_helper import ImplementationError
            raise ImplementationError( "Log indent too far." )
    
    
    def unindent( self ):
        self.__prefix = self.__prefix[ :len( self.__prefix ) - 4 ]
    
    
    def __enter__( self ):
        self.indent()
    
    
    def __exit__( self, exc_type, exc_val, exc_tb ):
        self.unindent()
