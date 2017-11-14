import inspect
from typing import List, Optional, Union, Callable, TypeVar, Type, Dict, cast, GenericMeta
from mhelper.generics_helper import MAnnotation, MAnnotationFactory
from mhelper.special_types import MOptional, MUnion


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
    def mannotation( self ) -> MAnnotation:
        """
        Returns the MAnnotation object, if this is an MAnnotation, otherwise raises an error.
        
        :except TypeError: Not an MAnnotation.
        """
        if not self.is_mannotation:
            raise TypeError( "«{}» is not an MAnnotation[T].".format( self ) )
        
        return cast( MAnnotation, self.value )
    
    
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
    def is_glist( self ) -> bool:
        """
        Is this a `List[T]`?
        
        (note: this does not include `list` or `List` with no `T`)
        """
        return isinstance(self.value, type) and issubclass(cast(type, self.value), List) and self.value is not list and hasattr( self.value, "__args__" )
    
    
    @property
    def glist_type( self ):
        """
        Gets the T in List[T]. Otherwise raises `TypeError`.
        """
        if not self.is_glist:
            raise TypeError( "«{}» is not a List[T].".format( self ) )
        
        # noinspection PyUnresolvedReferences
        return self.value.__args__[0]
    
    
    @property
    def is_union( self ) -> bool:
        """
        Is this a `Union[T, ...]`?
        Is this a `MUnion[T, ...]`?
        """
        return isinstance( self.value, _TUnion ) or self.is_mannotation_of( MUnion )
    
    
    def is_directly_below( self, upper_class: type ) -> bool:
        """
        Is `self.value` a sub-class of `lower_class`?
        """
        if not self.is_type:
            return False
            
        try:
            return issubclass( cast( type, self.value ), upper_class )
        except TypeError as ex:
            raise TypeError("Cannot determine if «{}» is directly below «{}» because `issubclass({}, {})` returned an error.".format(self, upper_class, self, upper_class)) from ex
    
    def is_directly_above( self, lower_class: type ) -> bool:
        """
        Is `lower_class` a sub-class of `self.value`?
        """
        if not self.is_type:
            return False
        
        if self.is_glist:
            # Special case for List[T]
            return issubclass(lower_class, list)
            
        try:
            return issubclass( lower_class, cast( type, self.value ) )
        except TypeError as ex:
            raise TypeError("Cannot determine if «{}» is directly above «{}» because `issubclass({}, {})` returned an error.".format(self, lower_class, lower_class, self)) from ex
    
    
    def get_directly_below( self, upper_class: type ) -> Optional[type]:
        """
        This is the same as `is_directly_below`, but returns the true `type` (`self.value`) if `True`.
        """
        if self.is_directly_below( upper_class ):
            return cast( type, self.value )
    
    
    def get_directly_above( self, lower_class: type ) -> Optional[type]:
        """
        This is the same as `is_directly_above`, but returns the true `type` (`self.value`) if `True`.
        """
        if self.is_directly_above( lower_class ):
            return cast( type, self.value )
    
    
    def is_indirectly_below( self, upper_class: type ) -> bool:
        """
        Is `self.value` a sub-class of `upper_class`, or an annotation enclosing a class that is a sub-class of `upper_class`? 
        """
        return self.get_indirectly_below( upper_class ) is not None
    
    
    def is_indirectly_above( self, lower_class: type ) -> bool:
        """
        Is `lower_class` a sub-class of `self.value`, or a sub-class of an annotation enclosed within `self.value`?
        """
        return self.get_indirectly_above( lower_class ) is not None
    
    
    def get_indirectly_above( self, lower_class: type ) -> Optional[type]:
        """
        This is the same as `is_indirectly_below`, but returns the true `type` that is above `lower_class`.
        """
        return self.__get_indirectly( lower_class, AnnotationInspector.is_directly_above )
    
    
    def get_indirectly_below( self, upper_class: type ) -> Optional[type]:
        """
        This is the same as `is_indirectly_above`, but returns the true `type` that iis below `upper_class`.
        """
        return self.__get_indirectly( upper_class, AnnotationInspector.is_directly_below )
    
    
    def __get_indirectly( self, query: type, predicate: "Callable[[AnnotationInspector, type],bool]" ) -> Optional[object]:
        """
        Checks inside all `Unions` and `MAnnotations` until the predicate matches, returning the type (`self.value`) when it does.
        """
        if predicate( self, query ):
            return self.value
        
        if self.is_union:
            for arg in self.union_args:
                arg_type = AnnotationInspector( arg ).__get_indirectly( query, predicate )
                
                if arg_type is not None:
                    return arg_type
        
        if self.is_mannotation:
            annotation_type = AnnotationInspector( self.mannotation_arg ).__get_indirectly( query, predicate )
            
            if annotation_type is not None:
                return annotation_type
        
        return None
    
    
    @property
    def union_args( self ) -> List[type]:
        """
        Returns the list of Union parameters `[...]`.
        """
        if not self.is_union:
            raise TypeError( "«{}» is not a Union[T].".format( self ) )
        
        # noinspection PyUnresolvedReferences
        if self.is_mannotation_of( MUnion ):
            return self.mannotation_arg
        else:
            return cast( _TUnion, self.value ).__args__
    
    
    @property
    def is_optional( self ) -> bool:
        """
        If a `Union[T, U]` where `None` in `T`, `U`.
        """
        if self.is_mannotation_of( MOptional ):
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
        if self.is_mannotation_of( MOptional ):
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
        if self.is_mannotation_of( MOptional ):
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
        return self.is_indirectly_above( type( value ) )


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
