# The following are decorators, they don't do anything, they're just used as comments
from inspect import isclass


def ignore( *_, **__ ):
    """
    Ignores its parameters
    """
    pass

def protected( f ):
    return f


def sealed( f ):
    return f


def override( f ):  # means "I'm not documenting this because the documentation is in the base class"
    return f


def overrides( interface ):
    ignore(interface)
    return override


def virtual( f ):
    return f


def abstract( f ):
    if isclass( f ):
        return f
    
    
    def fn( self, *_, **__ ):
        raise NotImplementedError( "An attempt has been made to call a method but this object has an abstract method «{}». The type of object is «{}» and its string representation is «{}».".format( f.__name__, type( self ).__name__, repr( self ) ) )
    
    
    return fn



