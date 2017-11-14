from typing import Any, Callable, Optional, Type, TypeVar, Union, cast, Sequence, Generic

# Decorator function, returns a function that takes and returns a function
from mhelper import array_helper


DECORATOR_FUNCTION = Callable[..., Callable[[Callable], Callable]]
# Decorator - takes a function, returns a function
DECORATOR = Callable[[Callable], Callable]
DECORATED = Optional[object]

T = TypeVar( "T" )


class MGenericMeta( type ):
    """
    Base class for generics.
    For example see `MGeneric` documentation.
    
    :data __parameters__:   Field containing the generic parameters.
                            Empty for the non-generic base.
                            
    :remarks: Nb. Name of `__parameters__` violates PEP8 but is coherent with PEP464 implementation and signifies a meta-field. 
    """
    
    
    def __new__( mcs, name, bases, namespace, parameters = None ):
        cls = super().__new__( mcs, name, bases, namespace )
        return cls
    
    
    def __init__( cls, name, bases, namespace, parameters = None ):
        super().__init__( name, bases, namespace )
        
        if parameters is None:
            if bases:
                for base in bases:
                    if hasattr( base, "__parameters__" ):
                        if parameters is not None:
                            raise TypeError( "Cannot inherit parameters because I don't know which subclass to use." )
                        
                        parameters = base.__parameters__
            
            if parameters is None:
                parameters = tuple()
        
        cls.__parameters__ = parameters
        cls.__CACHE = { }
    
    
    def __getitem__( cls: T, parameters ) -> T:
        """
        Obtains a class with the specified generic parameters.
        Results are cached, so asking for the same parameters again yields the same class instance.
        
        If the called class itself has generic parameters, the parameters are concatenated, for instance all of:
            A = MGeneric[int, bool]
            B = MGeneric[int][bool]
            C = MGeneric[int][bool]
        Have the same generic parameters (int, bool).
        However, the instances are different, hence:
            A.__parameters__ == B.__parameters__ == C.__parameters__
            A is not B
            B is C 
        
        :param parameters: Generic parameters. 
        """
        if parameters is None:
            parameters = ()
        elif not isinstance( parameters, tuple ):
            parameters = (parameters,)
        
        if parameters in cls.__CACHE:
            return cls.__CACHE[parameters]
        
        if cls.__parameters__:
            all_parameters = cls.__parameters__ + parameters
        else:
            all_parameters = parameters
        
        result = cls.__class__( cls.__name__,
                                (cls,) + cls.__bases__,
                                dict( cls.__dict__ ),
                                parameters = all_parameters )
        
        cls.__CACHE[parameters] = result
        
        return result
    
    
    def __str__( self ):
        """
        Returns a string similar to normal Python classes, but includes the generic parameters.
        Note that this is not the same as `__name__`, which always holds only the base class name, without the generics.
        """
        if self.__parameters__:
            return "<class {}{}>".format( self.__name__, ("[" + (", ".join( str( x ) for x in self.__parameters__ ) + "]")) )
        else:
            return "<class {}>".format( self.__name__ )


class MGeneric( metaclass = MGenericMeta ):
    """
    Instantiation of class with MGenericMeta meta-class.
    
    EXAMPLE:
        
        ```
        class MyList( MGeneric ):
            def item_type(self):
                return self.__parameters__[0]
            
            def append( item ):
                assert isinstance(item, self.item_type())
                ...
        ```
    """
    pass


# noinspection PyUnusedLocal
def placeholder( type_: Type[T] ) -> T:
    """
    Always returns `None`.
    For fixing lint errors where the specified type is expected
    """
    # noinspection PyTypeChecker
    return None


class MAnnotationFactory:
    """
    Class that generates objects intended to be used as a function parameter annotations.
    See `MAnnotation` for usage.
    """
    
    
    def __init__( self, name: str,
                  processing: "Optional[Callable[[MAnnotation], None]]" = None,
                  annotation_type: "Type[MAnnotation]" = None ):
        """
        CONSTRUCTOR
        :param name:            Name of the annotation class (generally the same as the variable name). 
        :param processing:      If not none, specifies a function called on all new annotations.
        :param annotation_type: If not none, specifies the type of MAnnotation to create. 
        """
        self.name = name
        self.processing = processing or None
        self.children = { }
        self.annotation_type = MAnnotation if annotation_type is None else annotation_type
    
    
    def __str__( self ) -> str:
        """
        Name of the factory.
        """
        return self.name
    
    
    def __getitem__( self, item ) -> "MAnnotation":
        """
        Obtains an annotation.
        :param item:    Interior annotation
        """
        return self.create( item, None )
    
    
    def create( self, child: object, parameters: Optional[Sequence[object]] ) -> "MAnnotation":
        """
        Obtains an annotation.
        
        :param child:        Interior annotation, usually the type or another annotation, but can be anything
        :param parameters:   Special parameters on the annotation to retrieve
        :return: The annotation
        """
        parameters = array_helper.as_sequence( parameters, cast = list )
        
        key = tuple([child] + list( parameters ))
        
        try:
            result = self.children.get( key )
        except TypeError as ex:
            raise TypeError("Invalid annotation parameters: «{}» on «{}».".format(", ".join(str(x) for x in key), self)) from ex
        
        if result is None:
            result = self.annotation_type( MAnnotationArgs( self, child, parameters ) )
            self.children[key] = result
        
        return result
    
    
    def __contains__( self, item ) -> bool:
        """
        Returns if the specified annotation is a member of this factory.
        """
        return isinstance( item, MAnnotation ) and item.parent is self


class MAnnotationArgs:
    def __init__( self,
                  factory: Union[MAnnotationFactory, str] = None,
                  child: object = None,
                  parameters: Optional[Sequence[object]] = None ):
        """
        :param factory:     Factory this annotation was created by 
        :param child:       Sub-type of the annotation, generally a type of an MAnnotation, but can be anything. 
        :param parameters:  Parameters on this annotation. 
        """
        self.factory = factory
        self.child = child
        self.parameters = parameters


class MAnnotation:
    """
    Class for objects intended to be used as a function parameter annotations.
    
    ```
    FileName = MAnnotationFactory("FileName")[ str ]
    
    def print_file(file_name : FileName):
        print(open(file_name).read())
    ```
    
    ```
    NonZero = MAnnotationFactory("NonZero")
    
    def divide_int(a : int, b : NonZero[int]):
        return a // b
    ```
    
    ```
    def fn(a):
        a.extension = a.parameters[0]
    
    FileName = MAnnotationFactory("FileName", processing = fn)[ str ]
    
    def print_file(file_name : FileName[".txt"]):
        print(open(file_name).read())
        
    def main():
        f = input()
        
        if not f.endswith(print_file.__annotations__["file_name"].extension):
            return 1
            
        print_file(f)
    ```
    """
    
    
    def __init__( self, args: MAnnotationArgs ):
        """
        CONSTRUCTOR
        :param args:      Constructor arguments 
        """
        parameters = array_helper.as_sequence( args.parameters )
        
        self.factory = args.factory
        self.child = args.child
        self.parameters = parameters
        
        if not isinstance(args.child, type) and not isinstance(args.child, MAnnotation) and not isinstance(args.child, type(Union[int,str])) and not isinstance(args.child, tuple):
            raise TypeError("args.child should be a type or another MAnnotation, but it's a «{}» («{}»).".format(type(args.child), args.child))
        
        if self.factory.processing is not None:
            self.factory.processing( self )
    
    def __str__( self ) -> str:
        return "{}[{}]".format( self.factory, self.child, ", {}".format( self.parameters) if self.parameters else "" )
    
    
    def __getitem__( self, item ) -> "MAnnotation":
        """
        Obtains a further annotation with the specified parameters.
        The parameters must have been specified on the `parent`.
        
        :param item:    Parameter sequence 
        """
        if self.parameters:
            raise ValueError("This is already the parameterised instance, «{}», cannot parameterise again using «{}».".format(self, item))
        
        return self.factory.create( self.child, item )


class GenericStringMeta( MGenericMeta ):
    def __subclasscheck__( self, cls ):
        if cls is Any:
            return True
        if self.__parameters__ is None:
            return isinstance( cls, GenericStringMeta )
        elif isinstance( cls, GenericStringMeta ):
            return True
        elif isinstance( cls, GenericStringMeta ):
            if issubclass( cls, str ):
                return True
            return False
        else:
            return issubclass( cls, str )
    
    
    def __instancecheck__( self, obj ):
        print( "__instancecheck__ {}".format( obj ) )
        return self.__subclasscheck__( type( obj ) )


class GenericString( str, metaclass = GenericStringMeta ):
    """
    Something that is a string.
    
    This property acts as a hint to the UI, indicating the string's values are constrained.
    
    A "label" of the node or edge can be specified as a generic argument.
    Use "@" to reference the name of another function argument.
    
    
    GenericString["label"]("value")
        - OR -
    GenericString("value")
    """
    
    
    def __new__( cls: Type[T], *args, **kwargs ) -> T:
        # noinspection PyArgumentList,PyTypeChecker
        return cast( cls, str.__new__( cls, *args, **kwargs ) )
    
    
    # noinspection PyUnresolvedReferences
    @classmethod
    def type_label( cls ):
        if cls.__parameters__:
            return cls.__parameters__[0]
        else:
            return None


class NonGenericString( str ):
    """
    NonGenericString("value")
    
    This property acts as a hint to the UI, indicating the string's values are constrained.
    """
    
    
    def __new__( cls: Type[T], *args, **kwargs ) -> T:
        # noinspection PyArgumentList,PyTypeChecker
        return cast( cls, str.__new__( cls, *args, **kwargs ) )


class TypedList( MGeneric ):
    def get_list_type( self ):
        return self.__parameters__[0]
    
    
    def __init__( self, *args, **kwargs ):
        self.__list = list( *args, **kwargs )
    
    
    def __getitem__( self, item ):
        return self.__list[item]
    
    
    def __setitem__( self, key, value ):
        self.__check_instance( value )
        self.__list[key] = value
    
    
    def append( self, value ):
        self.__check_instance( value )
        self.__list.append( value )
    
    
    def __check_instance( self, value ):
        if not isinstance( value, self.__parameters__[0] ):
            raise TypeError( "Value «{}» of incorrect type «{}» added to list of «{}».".format( value, type( value ), self.get_list_type() ) )


class ByRef( Generic[T] ):
    """
    Pass value by reference.
    """
    
    
    def __init__( self, value: T ):
        self.value: T = value
