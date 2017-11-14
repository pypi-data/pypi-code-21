"""
Helper functions for arrays, lists, iterable, etc.
"""

import warnings
from typing import List, Optional, Iterator, Tuple, Dict, Iterable, Union, TypeVar, Callable, cast


T = TypeVar( "T" )
U = TypeVar( "U" )


def list_type( the_list ) -> type:
    """
    Determines the type of elements in a list

    Errors if the list doesn't contain any elements, or if the elements are of varying type

    :param the_list: List to check
    :return: Type of elements in the list
    """
    
    t = None
    
    for e in the_list:
        et = type( e )
        
        if t is None:
            t = et
        elif t is not et:
            raise ValueError( "Calling list_type on a list with at least two types ({0} and {1})".format( t, et ) )
    
    if t is None:
        raise ValueError( "Calling list_type on a list with no elements." )
    
    return t


def dict_to_list( v: dict ) -> List[str]:
    """
    Converts a string dictionary to a string list where each element is "x = y"
    """
    
    r = []
    
    for k, v in v.items():
        r.append( "{}={}".format( k, v ) )
    
    return r


def decomplex( item: Union[Optional[object], List[Optional[object]]] ) -> Optional[object]:
    """
    Converts items in arrays to single items
    """
    
    # noinspection PyBroadException
    try:
        if len( item ) == 1 and item[0] is not item:
            return decomplex( item[0] )
    except:
        pass
    
    return item


def as_sequence( contents: Union[T, List[T], Tuple[T]], elemental_none = False, cast = None, accept = (list, tuple) ) -> Union[List[T], Tuple[T]]:
    """
    The contents, as a tuple or list, if they are a tuple or list
    Or the sole item in a tuple
    
    Note: only `tuple` and `list` are handled, other `iterable`s are still placed in a tuple because we cannot know their nature.
    
    :param contents:        List contents
    :param elemental_none:  Doesn't treat `None` as an empty list
    :param cast:            Casts the result to this list type, if it isn't already 
    :param accept:          Types to accept
    :return: The result, as a list
    """
    if not elemental_none and contents is None:
        contents = tuple()
    elif not any( isinstance( contents, x ) for x in accept ):
        contents = contents,
    
    if cast is not None and not isinstance( contents, cast ):
        contents = cast( contents )
    
    return contents


def as_iter( contents: Union[T, List[T], Tuple[T]] ) -> Tuple[T]:
    """
    DEPRECATED
    """
    warnings.warn( "as_iter is deprecated, use `as_sequence`.", DeprecationWarning )
    return as_sequence( contents, elemental_none = True )


def as_tuple( contents: Union[T, List[T], Tuple[T]] ) -> Tuple[T]:
    """
    DEPRECATED
    """
    warnings.warn( "as_tuple is deprecated, use `as_sequence`.", DeprecationWarning )
    return as_sequence( contents, elemental_none = True, cast = tuple )


def as_list( contents: Union[T, List[T], Tuple[T]] ) -> List[T]:
    """
    DEPRECATED
    """
    warnings.warn( "as_list is deprecated, use `as_iter`.", DeprecationWarning )
    return as_sequence( contents, elemental_none = True, cast = list )


def backwards_range( count ):
    """
    A range, going backwards.
    """
    return range( count - 1, -1, -1 )


# !has test case
def create_index_lookup( source: Iterable[T] ) -> Dict[T, int]:
    """
    Creates a lookup table (`dict`) that allows the index of elements in `the_list` to be found.
    """
    result = { }
    result.update( (v, i) for i, v in enumerate( source ) )
    
    return result


def deinterleave_as_two( source: Iterable[T] ) -> Tuple[List[T], List[T]]:
    """
    Deinterleaves a source list, returns two new lists
    """
    dest_a = []
    dest_b = []
    iterator = iter( source )
    
    for a in iterator:
        dest_a.append( a )
        dest_b.append( next( iterator ) )
    
    return dest_a, dest_b


def deinterleave_as_iterator( source: Iterable[T] ) -> Iterator[Tuple[T, T]]:
    """
    Deinterleaves a source list, returns an iterator over tuples
    """
    iterator = iter( source )
    
    for a in iterator:
        yield a, next( iterator )


def deinterleave_as_list( source: Iterable[T] ) -> List[Tuple[T, T]]:
    """
    Deinterleaves a source list "A,B,A,B,...", returns a list of tuples "A, B"
    """
    dest_a = []
    iterator = iter( source )
    
    for a in iterator:
        dest_a.append( (a, next( iterator )) )
    
    return dest_a


def deinterleave_as_dict( source ) -> Dict[object, Optional[object]]:
    """
    Deinterleaves a source list "K,V,K,V,...", returns a dictionary "D" of "V = D[K]"
    """
    return dict( deinterleave_as_iterator( source ) )


def has_any( sequence: Iterable ) -> bool:
    """
    Returns if the sequence contains _any_ elements (i.e. non-zero length).
    """
    for _ in sequence:
        return True
    
    return False


def iterate_all( root, fn = None ) -> Iterator[Optional[object]]:
    """
    Iterates all items and descendants
    :param root: Where to start 
    :param fn: How to get the children 
    :return: Iterator over items and all descendants 
    """
    if fn is None:
        fn = lambda x: x
    
    for x in fn( root ):
        yield x
        yield from iterate_all( x, fn )


def ensure_capacity( array, index, value = None ):
    if len( array ) <= index:
        needed = index + 1 - len( array )
        array += [value] * needed


def index_of_first( array, elements ) -> Optional[int]:
    for e in elements:
        for i, x in enumerate( array ):
            if x == e:
                return i
    
    return None


class Indexer:
    """
    Provides a name to index and index to name lookup table.
    
    Note that `Indexer` has no indexer - be specific, use:
        `Indexer.name`
        `Indexer.index`
    """
    
    
    def __init__( self, iterator: Iterable[object] = None ):
        """
        CONSTRUCTOR
        Allows initialisation from existing entries
        """
        self.indexes = { }  # names to indices
        self.names = []  # indices to names
        
        if iterator is not None:
            for name in iterator:
                self.add( name )
    
    
    def add( self, name: object ):
        """
        Adds a new name with a new index.
        """
        index = self.indexes.get( name )
        
        if index is not None:
            return index
        
        index = len( self )
        
        self.indexes[name] = index
        self.names.append( name )
        
        return index
    
    
    def __len__( self ) -> int:
        """
        OVERRIDE
        Obtains the number of names
        """
        return len( self.names )
    
    
    def index( self, name: object ) -> int:
        """
        Obtains the index of the specified name.
        """
        return self.indexes[name]
    
    
    def name( self, index: int ):
        """
        Obtains the name at the specified index.
        """
        return self.names[index]


def first( array: Iterable[T] ) -> Optional[T]:
    for item in array:
        return item
    
    return None


def first_or_nothing( array ) -> Optional[object]:
    warnings.warn( "deprecated", DeprecationWarning )
    return only_first( array )


def only_first( array: Iterable[T] ) -> Optional[T]:
    """
    Returns the first element of the array, or Nothing if the length is non-1.
    :param array: 
    :return: 
    """
    it = iter( array )
    
    try:
        first = next( it )
    except StopIteration:
        return None
    
    try:
        next( it )
        return None
    except StopIteration:
        return first


def lagged_iterate( sequence: Iterable[Optional[T]] ) -> Iterator[Tuple[Optional[T], Optional[T]]]:
    """
    Iterates over all adjacent pairs in the sequence, (0,1),(1,2),(2,3),(...,...),(n-1,n)
    """
    has_any = False
    previous = None
    
    for current in sequence:
        if has_any:
            yield previous, current
        
        has_any = True
        previous = current


def triangular_comparison( sequence: List[Optional[T]] ) -> Iterator[Tuple[Optional[T], Optional[T]]]:
    for index, alpha in enumerate( sequence ):
        for beta in sequence[index + 1:]:
            yield alpha, beta


class Single:
    def __init__( self, value = 0 ):
        self.value = value
    
    
    def next( self ):
        self.value += 1
        return self.value


def sort_two( a: T, b: U ) -> Tuple[T, U]:
    if a > b:
        return b, a
    else:
        return a, b


def sort_two_by_key( a: T, b: U, ka, kb ) -> Tuple[T, U]:
    if ka > kb:
        return b, a
    else:
        return a, b


def ordered_insert( list: List[T], item: T, key: Callable[[T], object] ):
    """
    Inserts the `item` into the `list` that has been sorted by `key`.
    """
    import bisect
    list.insert( bisect.bisect_left( [key( x ) for x in list], key( item ) ), item )


def average( list ) -> float:
    """
    Returns the mean average.
    """
    return sum( list ) / len( list )


def count( list ):
    try:
        return len( list )
    except:
        return sum( 1 for _ in list )


def when_last( i ):
    f = True
    l = None
    
    for x in i:
        if not f:
            yield l, False
        else:
            f = False
        
        l = x
    
    yield l, True


def make_dict( **kwargs ):
    return kwargs
