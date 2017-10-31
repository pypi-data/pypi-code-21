from typing import Callable, Optional


class PropertySetInfo:
    def __init__( self, source, name, value ):
        self.source = source
        self.name = name
        self.value = value
        self.cancel = False


class SimpleProxy:
    def __init__( self, source: Callable[[], object], watch: Optional[Callable[[PropertySetInfo], None]] = None ):
        object.__setattr__( self, "__source", source )
        object.__setattr__( self, "__watch", watch )
    
    
    def __getattribute__( self, name: str ) -> object:
        if name == "__class__":
            return SimpleProxy
        
        source = object.__getattribute__( self, "__source" )
        return getattr( source(), name )
    
    
    def __delattr__( self, name ):
        delattr( object.__getattribute__( self, "__source" )(), name )
    
    
    def __setattr__( self, name, value ):
        watch = object.__getattribute__( self, "__watch" )
        source = object.__getattribute__( self, "__source" )()
        
        if watch is not None:
            args = PropertySetInfo( source, name, value )
            watch( args )
            
            if args.cancel:
                return
        
        setattr( source, name, value )
    
    
    def __str__( self ) -> str:
        return str( object.__getattribute__( self, "__source" )() )
    
    
    def __repr__( self ) -> str:
        return repr( object.__getattribute__( self, "__source" )() )
