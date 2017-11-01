import inspect
from typing import List, Optional, Union, Callable, TypeVar, Type, Dict, cast, Tuple
from mhelper.generics_helper import MAnnotation, MAnnotationFactory
from mhelper.special_types import MOptional


T = TypeVar( "T" )

_TUnion = type( Union[int, str] )


class AnnotationInspector:
    """
    Class to inspect PEP484 generics.
    """
    
    
    def __init__( self, annotation: object ):
        """
        CONSTRUCTOR
        :param annotation: `type` to inspect 
        """
        self.value = annotation
    
    
    def __str__( self ) -> str:
        """
        Returns the underlying type string
        """
        return str( self.value )
    
    
    @property
    def is_mannotation( self ):
        """
        Is this an instance of `MAnnotation`?
        """
        return isinstance( self.value, MAnnotation )
    
    
    def is_mannotation_of( self, parent: MAnnotationFactory ):
        """
        Is this an instance of `MAnnotation`, specifically a `specific_type` derivative?
        """
        if not self.is_mannotation:
            return False
        
        assert isinstance( self.value, MAnnotation )
        return self.value.factory is parent
    
    @property
    def mannotation(self) -> MAnnotation:
        """
        Returns the MAnnotation object, if this is an MAnnotation, otherwise raises an error.
        
        :except TypeError: Not an MAnnotation.
        """
        if not self.is_mannotation:
            raise TypeError( "«{}» is not an MAnnotation[T].".format( self ) )
        
        return cast(MAnnotation, self.value)
    
    @property
    def mannotation_arg( self ):
        """
        If this is an instance of `MAnnotation`, return the underlying type, otherwise, raise an error.
        """
        if not self.is_mannotation:
            raise TypeError( "«{}» is not an MAnnotation[T].".format( self ) )
        
        assert isinstance( self.value, MAnnotation )
        return self.value.child
    
    
    @property
    def is_list( self ) -> bool:
        """
        Is this a `List[T]`?
        
        (note: this does not include `list` or `List` with no `T`)
        """
        return self.is_direct_sub_class( List ) and self.value is not list and hasattr( self.value, "__args__" )
    
    
    @property
    def list_type( self ):
        """
        Gets the T in List[T]. Otherwise raises `TypeError`.
        """
        if not self.is_list:
            raise TypeError( "«{}» is not a List[T].".format( self ) )
        
        # noinspection PyUnresolvedReferences
        return self.value.__args__[0]
    
    
    @property
    def is_union( self ) -> bool:
        """
        Is this a `Union[T, ...]`?
        """
        return isinstance( self.value, _TUnion )
    
    
    def is_direct_sub_class( self, t ) -> bool:
        """
        Returns if this is a type, and a subclass of `t`.
        """
        # noinspection PyTypeChecker
        return self.is_type and issubclass( self.value, t )
    
    
    def get_viable_sub_class_type( self, t ) -> Optional[type]:
        """
        Returns, if t is a subclass of this, then the type in question.
        """
        if self.is_direct_sub_class( t ):
            return cast(type,self.value)
        
        if self.is_union:
            for arg in self.union_args:
                arg_type = AnnotationInspector( arg ).get_viable_sub_class_type( t )
                
                if arg_type is not None:
                    return arg_type
        
        if self.is_mannotation:
            annotation_type = AnnotationInspector( self.mannotation_arg ).get_viable_sub_class_type( t )
            
            if annotation_type is not None:
                return annotation_type
        
        return None
    
    def is_viable_sub_class( self, t ) -> bool:
        """
        Returns if t is a subclass of this.
        """
        return self.get_viable_sub_class_type( t ) is not None
    
    @property
    def union_args( self ) -> List[type]:
        """
        Returns the list of Union parameters `[...]`.
        """
        if not self.is_union:
            raise TypeError( "«{}» is not a Union[T].".format( self ) )
        
        # noinspection PyUnresolvedReferences
        return self.value.__args__
    
    
    @property
    def is_optional( self ) -> bool:
        """
        If a `Union[T, U]` where `None` in `T`, `U`.
        """
        if self.is_mannotation_of(MOptional):
            return True
        
        if not self.is_union:
            return False
        
        if len( self.union_args ) == 2 and None in self.union_args:
            return True
        
        return False
    
    
    @property
    def is_multi_optional( self ) -> bool:
        """
        If a `Union[...]` with `None` in `...`
        """
        if self.is_mannotation_of(MOptional):
            return True
        
        if not self.is_union:
            return False
        
        if None in self.union_args:
            return True
        
        return False
    
    
    @property
    def optional_types( self ) -> Optional[List[type]]:
        """
        Returns `...` in a `Union[None, ...]`, otherwise raises `TypeError`.
        """
        if self.is_mannotation_of(MOptional):
            return [self.mannotation_arg]
        
        if not self.is_union:
            raise TypeError( "«{}» is not a Union[T].".format( self ) )
        
        union_params = self.union_args
        
        if type( None ) not in union_params:
            raise TypeError( "«{}» is not a Union[...] with `None` in `...`.".format( self ) )
        
        union_params = list( self.union_args )
        union_params.remove( type( None ) )
        return union_params
    
    
    @property
    def optional_type( self ) -> Optional[type]:
        """
        Returns `T` in a `Union[T, U]` (i.e. an `Optional[T]`). Otherwise raises `TypeError`.
        """
        t = self.optional_types
        
        if len( t ) == 1:
            return t[0]
        else:
            raise TypeError( "«{}» is not a Union[T, None] (i.e. an Optional[T]).".format( self ) )
    
    
    @property
    def type_or_optional_type( self ) -> Optional[type]:
        """
        If this is an `Optional[T]`, returns `T`.
        If this is a `T`, returns `T`.
        Otherwise returns `None`.
        """
        if self.is_optional:
            return self.optional_type
        elif self.is_type:
            assert isinstance( self.value, type )
            return self.value
        else:
            return None
    
    
    @property
    def safe_type( self ) -> Optional[type]:
        """
        If this is a `T`, returns `T`, else returns `None`.
        """
        if self.is_type:
            assert isinstance( self.value, type )
            return self.value
        else:
            return None
    
    
    @property
    def is_type( self ):
        """
        Returns if my `type` is an actual `type`, not an annotation object like `Union`.
        """
        return isinstance( self.value, type )
    
    
    @property
    def name( self ):
        """
        Returns the type name
        """
        if not self.is_type:
            raise TypeError( "«{}» is not a <type>.".format( self ) )
        
        return self.value.__name__
    
    
    def is_type_or_optional_type_subclass( self, u: type ):
        """
        Returns if `type_or_optional_type` is a subclass `u`.
        """
        return issubclass( self.type_or_optional_type, u )
    
    
    def is_viable_instance( self, value ):
        """
        Returns `is_viable_subclass` on the value's type.
        """
        return self.is_viable_sub_class( type( value ) )


def as_delegate( x: Union[T, Callable[[], T]], t: Type[T] ) -> Callable[[], T]:
    """
    If `x` is a `t`, returns a lambda returning `x`, otherwise, assumes `x` is already a lambda and returns `x`.
    This is the opposite of `dedelegate`.
    """
    if isinstance( x, t ):
        return (lambda x: lambda: x)( x )
    else:
        return x


def defunction( x ):
    """
    If `x` is a function or a method, calls `x` and returns the result.
    Otherwise, returns `x`.
    """
    if inspect.isfunction( x ) or inspect.ismethod( x ):
        return x()
    else:
        return x


def dedelegate( x: Union[T, Callable[[], T]], t: Type[T] ) -> T:
    """
    If `x` is not a `t`, calls `x` and returns the result.
    Otherwise, returns `x`.
    This is the opposite of `as_delegate`.
    """
    if not isinstance( x, t ):
        x = x()
    
    return x


def public_dict( d: Dict[str, object] ) -> Dict[str, object]:
    """
    Yields the public key-value pairs.
    """
    r = { }
    
    for k, v in d.items():
        if not k.startswith( "_" ):
            r[k] = v
    
    return r
