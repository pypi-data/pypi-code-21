from typing import Optional, Callable


class ManagedWith:
    """
    Wraps a (presumably pooled) object.
    
    Usage:

        ```
        with ManagedWith(...):
            ...
        ```
        
    Example (database provider):
    
        def get_database():
            return ManagedWith(pool.pop(), pool.push)
        
    Example (from `Plugin`):
        
        ```
        with get_database() as db:
            db.execute("RETURN 1")
        ```
    """
    
    
    def YOURE_USING_THE_WRONG_THING( self ):
        """
        Message to an IDE user telling them they're using the wrong thing! (should be using `with`)
        """
        pass
    
    
    def __init__( self,
                  target: Optional[ object ] = None,
                  callback: Callable[ [ Optional[ object ] ], None ] = None,
                  call_into: Callable[ [ Optional[ object ] ], None ] = None,
                  obtain: Callable[ [ ], object ] = None ):
        """
        :param target: Object to manage 
        :param callback: What to do when the caller has finished with the target 
        """
        self.__target = target
        self.__callback = callback
        self.__call_into = call_into
        self.__obtain = obtain
        
        if self.__obtain is not None and self.__target is not None:
            raise ValueError( "Cannot specify both 'obtain' and 'target' parameters." )
    
    
    def __enter__( self ):
        if self.__obtain is not None:
            self.__target = self.__obtain()
        
        if self.__call_into is not None:
            self.__call_into( self.__target )
        
        return self.__target
    
    
    def __exit__( self, exc_type, exc_val, exc_tb ):
        if self.__callback is not None:
            self.__callback( self.__target )
        
        if self.__obtain is not None:
            self.__target = None
