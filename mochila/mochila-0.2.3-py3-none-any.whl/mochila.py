# -*- coding: utf-8 -*-
import collections
import random
import warnings

"""
Reflective API
==============

The main goal of the Mochila implementation is to support reflective APIs. In reflective APIs (for 
example the OMG's MOF) the collection is used to represent an object's attribute and the object needs to be aware
of changes in the collection. This is not possible with standard collections. For example::

    >>> class Project():
    ...     def __init__():
    ...         self.members = []
    
    >>> p = Project()
    >>> p.members.append("Albert")
    >>> p.members.append("Julian")
    >>> p.members.remove("Albert")

In this case, the Project is not aware of changes done to the collection. You could add an "addMember" or other methods
in order to have control over the contents, but it is not pythonic. Further, in reflective API's it also desirable that 
objects know when they have been added/removed to/from a collection. Thus, the collection should be able to use the
object's notification mechanism in order to inform these changes.

Currently the reflective API is the responsibility of the class/script using mochilas (e.g. using decorators to keep
track of methods that modify the collection). To facilitate this approach, the Mochila's API objective is to reduce the
number of methods that modify the Mochila so that the module that uses the Mochila has a small, clear set of methods 
that must be overridden/decorated. Thus, some of the methods may appear sub-optimal, i.e. reusing existing
methods rather than accessing the underlying native collections instead. 

In the future, the reflective API might be incorporated directly into the Mochila API.

For each of the Mochilas, the set of methods that perform modifications are:
Sequence
    __setitem__, __delitem__, insert
Set
    add, discard
OrderedSet
    __setitem__, __delitem__, insert, discard
Bag
    add, remove
MultiSet
    Is not part of the reflective collections

"""

__author__ = 'Horacio Hoyos Rodriguez'
__copyright__ = 'Copyright , Kinori Technologies'

SLICE_ALL = slice(None)

warnings.simplefilter('default', UserWarning)


def _is_iterable(obj):
    """
    Are we being asked to look up a list of things, instead of a single thing?
    We check for the `__iter__` attribute so that this can cover types that
    don't have to be known by this module, such as NumPy arrays.
    Strings, however, should be considered as atomic values to look up, not
    iterables. The same goes for tuples, since they are immutable and therefore
    valid entries.
    We don't need to check for the Python 2 `unicode` type, because it doesn't
    have an `__iter__` attribute anyway.
    """
    return hasattr(obj, '__iter__') and not isinstance(obj, str) and not isinstance(obj, tuple)


def _closure_decorate(func):
    def closure_wrapper(x):
        if _is_iterable(x):
            cl = map(func, x)
            return list(cl)
        else:
            return func(x)
    return closure_wrapper


def _closure(iterable, f):
    cl = map(f, iterable)
    result = Bag((Bag(x) for x in cl if x is not None))
    _closure_recursion(f, result)
    return result


def _closure_recursion(f, result):
    for sr in result:
        if sr:
            sr_cl = _closure(sr, f)
            sr.add_all(sr_cl)


class MochilaError(TypeError):
    """Thrown to indicate errors in the use of a Mochila operation."""
    pass


class Mochila:
    """
    Define common operations. This class is not meant to be instantiated.
    """

    # Declarative operations

    def aggregate(self, key, value):
        def key_value_gen(x):
            yield key(x)
            yield value(x)

        return dict(map(key_value_gen, self))

    def closure(self, f):
        f = _closure_decorate(f)
        cl = map(f, self)
        result = Bag([Bag([x]) if x is not None else Bag([]) for x in cl])
        _closure_recursion(f, result)
        return result

    def collect(self, f):
        return Bag(map(f, self))

    def exists(self, f):
        return any(map(f, self))

    def for_all(self, f):
        return all(map(f, self))

    def one(self, f):
        r = [x for x in self if f(x)]
        return len(r) == 1

    def reject(self, f):
        r = (x for x in self if not f(x))
        return self.__class__(r)

    def select(self, f):
        #r = (x for x in self if f(x))
        r = filter(f, self)
        return self.__class__(r)

    def select_one(self, f, default=None):
        for x in self:
            if f(x):
                return x
        return default

    def sort_by(self, f, reverse=None, inplace=False):
        if reverse is None:
            reverse = 0
        if inplace:
            if isinstance(self, Set) or isinstance(self, Bag) or isinstance(self, MultiSet):
                warnings.warn("You can not sort an unordered Mochila in-place. The operation will be ignored.",
                              UserWarning)
                return
            self.sort(f, reverse)
        else:
            return Sequence(sorted(self, key=f, reverse=reverse))

    # Core operations

    def _flatten(self):
        for x in self:
            if isinstance(x, Mochila):
                yield from x.flatten()
            elif not _is_iterable(x):
                yield x
            else:
                for x2 in x:
                    yield x2

    def add_all(self, iterable):
        if self is iterable:
            for x in iterable.copy():
                self.add(x)
        else:
            for v in iterable:
                self.add(v)

    def discard_all(self, iterable):
        if self is iterable:
            self.clear()
        else:
            for x in iterable:
                self.discard(x)

    # FIXME can specific collections provide better implementations? E.g. an empty set intersection
    def excludes_all(self, iterable):
        for x in iterable:
            if x in self:
                break
        else:
            return True
        return False

    def excluding(self, x):
        copy = self.copy()
        copy.remove(x)
        return copy

    def excluding_all(self, iterable):
        copy = self.copy()
        for x in iterable:
            copy.discard(x)
        return copy

    def flatten(self):
        return Bag(self._flatten())

    def includes_all(self, iterable):
        for x in iterable:
            if x not in self:
                break
        else:
            return True
        return False

    def including(self, x):
        copy = self.copy()
        copy.add(x)
        return copy

    def including_all(self, iterable):
        copy = self.copy()
        copy.add_all(iterable)
        return copy

    def remove_all(self, iterable):
        if self is iterable:
            self.clear()
        else:
            for x in iterable:
                self.remove(x)

    def as_bag(self):
        return Bag(self)

    def as_multiset(self):
        return MultiSet(self)

    def as_set(self):
        return Set(self)

    def as_sequence(self, key=None, reverse=None):
        l = sorted(self, key, reverse)
        return Sequence(l)

    def as_orderedset(self, key=None, reverse=None):
        if key is not None and reverse is not None:
            result = sorted(self, key=key, reverse=reverse)
        elif key is not None:
            result = sorted(self, key=key)
        elif reverse is not None:
            result = sorted(self, reverse=reverse)
        else:
            result = sorted(self)
        return OrderedSet(result)


class Sequence(collections.MutableSequence, Mochila):
    """
    A Sequence is an enumerated collection of items. The order in which the items appear in the collection matters
    and the same item can appear multiple times.

    A sequence behaves as the Python built-in *list* type. The main difference is that item access by index additionally
    supports an iterable as the index. In this case the result will be a Sequence of the items corresponding to those
    indices.

    >>> m = Sequence(['a','b','c'])                           # a new Sequence
    >>> m[1]
    'b'
    >>> m[[0,2]]
    ['a', 'c']

    """
    def __init__(self, iterable=()):
        """
        Sequences can be constructed using the type constructor `Sequence()` or `Sequence(iterable)`. The constructor
        builds a Sequence whose items are the same and in the same order as *iterable*‘s items. *iterable* may be
        either a sequence, a container that supports iteration, or an iterator object. For example, `Sequence('abc')`
        returns `['a', 'b', 'c']` and `Sequence((1, 2, 3))` returns `[1, 2, 3]`. If no argument is given, the
        constructor creates a new empty Sequence, [].

        Note that the default representation of a Sequence is the same as for a *list*.

        :param iterable: An iterable used to instantiate the Sequence
        """
        self._items = []
        self.extend(iterable)

    def __getitem__(self, key):
        """
        Get the item at a given key, called to implement the evaluation of `self[key]`.
        If `key` is a slice, you will get back that slice of items. If it's the slice [:], a copy of the Sequence is
        returned.
        If `key` is an iterable, you'll get the Sequence of items corresponding to those indices (this is similar to
        NumPy's "fancy indexing").

        :param key: Index or slice or list of the item(s) to get
        """
        if key == SLICE_ALL:
            return Sequence(self._items)
        elif hasattr(key, '__index__') or isinstance(key, slice):
            result = self._items[key]
            if isinstance(key, slice):
                if isinstance(result, list):
                    return Sequence(result)
            return result
        elif _is_iterable(key):
            return Sequence([self._items[i] for i in key])
        else:
            raise TypeError('Don\'t know how to key an Sequence by {!r}'.format(key))

    def __setitem__(self, index, value):
        return self._items.__setitem__(index, value)

    def __delitem__(self, index):
        return self._items.__delitem__(index)

    def __len__(self):
        return self._items.__len__()

    def __iter__(self):
        return self._items.__iter__()

    def __eq__(self, other):
        if self is other:
            return True
        if isinstance(other, self.__class__):
            return len(self) == len(other) and self._items == other._items
        return NotImplemented

    def __ne__(self, other):
        if self is other:
            return False
        if isinstance(other, self.__class__):
            if len(self) != len(other):
                return True
            else:
                return self._items != other._items
        return NotImplemented

    def __str__(self):
        return str(self._items)

    def __repr__(self):
        return repr(self._items)

    def add(self, item):
        return self.append(item)

    def copy(self):
        return Sequence(self._items)

    def extend(self, iterable):
        if self is iterable:
            for i in range(len(iterable)):
                self.append(iterable[i])
        else:
            for v in iterable:
                self.append(v)

    def index(self, value, start=0, stop=None):
        return super().index(value, start, stop)

    def insert(self, index, value):
        self._items.insert(index, value)

    def sort(self, key=None, reverse=False):
        self._items.sort(key=key, reverse=reverse)

    def discard(self, value, n_copies=1):
        for n in range(n_copies):
            try:
                i = self.index(value)
                del self[i]
            except ValueError:
                pass


class Set(collections.MutableSet, Mochila):
    """
    A Set is a collection of items. The order in which the items appear in the collection is irrelevant and the same
    item can appear only once in the collection. Items in the collection must be `hashable <https://docs.python.org/3.6/glossary.html#term-hashable>`_.

    A Set behaves as the Python built-in *set* type. The main difference is that the non-operator versions of
    the update(), intersection_update(), difference_update(), and symmetric_difference_update() are not supported.
    """

    def __init__(self, iterable=()):
        """
        Sets can be constructed using the type constructor `Set()` or `Set(iterable)`. The constructor builds a Set
        whose items are taken from *iterable*.  To represent sets of sets, the inner sets must be `frozenset <https://docs.python.org/3/library/stdtypes.html?highlight=list#frozenset>`_
        objects. If *iterable* is not specified, a new empty Set is returned.

        :param iterable: An iterable from which items are taken to build the Set.
        """
        self._items = set()
        self |= iterable

    def add(self, value):
        self._items.add(value)

    def discard(self, value):
        if value not in self:
            return
        self._items.discard(value)

    def __len__(self):
        return self._items.__len__()

    def __iter__(self):
        return self._items.__iter__()

    def __contains__(self, value):
        return self._items.__contains__(value)

    def __eq__(self, other):
        if self is other:
            return True
        return super().__eq__(other)

    def __ne__(self, other):
        if self is other:
            return False
        return not self == other

    def __str__(self):
        return str(self._items)

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, self._items)

    def copy(self):
        cp = Set(self._items)
        return cp


class OrderedSet(collections.MutableSet, collections.MutableSequence, Mochila):
    """
    An OrderedSet is an enumerated collection of items. The order in which the items appear in the collection matters
    and the same item can appear only once in the collection. Items in the collection must be `hashable <https://docs.python.org/3.6/glossary.html#term-hashable>`_.

    An OrderedSet behaves as the Python built-in *set* type. The main difference is that the non-operator versions of
    the update(), intersection_update(), difference_update(), and symmetric_difference_update() are not supported.

    Additionally, as for Sequences, item access by index additionally supports an iterable as the index. In this case
    the result will be a Sequence of the items corresponding to those indices.

    >>> m = OrderedSet('madagascar')
    >>> print(m)
    ['m', 'a', 'd', 'g', 's', 'c', 'r']
    >>> print(m[[0,2,5]])
    ['m', 'd', 'c']

    """
    #The OrderSet has O(1) search, O(n) insert, O(n) delete
    def __init__(self, iterable=None):
        """
        OrderedSets can be constructed using the type constructor `OrderedSet()` or `OrderedSet(iterable)`. The
        constructor builds an OrderedSet whose items are taken from *iterable*. To represent sets of sets, the inner
        sets must be `frozenset <https://docs.python.org/3/library/stdtypes.html?highlight=list#frozenset>`_ objects.
        If *iterable* is not specified, a new empty OrderedSet is returned.

        :param iterable: An iterable from which items are taken to build the OrderedSet.
        """
        self._items = []
        self._map = {}
        if iterable is not None:
            self |= iterable

    def __len__(self):
        return len(self._items)

    def __getitem__(self, key):
        """
        Get the item at a given key, called to implement the evaluation of `self[key]`.
        If `key` is a slice, you will get back that slice of items. If it's the slice [:], a copy of the object is
        returned. If `key` is an iterable, you'll get the OrderedSet of items corresponding to those indices (this is
        similar to NumPy's  "fancy indexing".).

        :param key: Index or slice or list of the item(s) to get
        :return: a single element (for index) or an OrderedSet of elements (for slice and list)
        """
        if key == SLICE_ALL:
            return self._from_iterable(self._items)
        elif hasattr(key, '__index__') or isinstance(key, slice):
            result = self._items[key]
            if isinstance(result, list):
                return self._from_iterable(result)
            else:
                return result
        elif _is_iterable(key):
            return self._from_iterable([self._items[i] for i in key])
        else:
            raise TypeError("Don't know how to key an OrderedSet by %r" % key)

    def __setitem__(self, index, value):
        """
        Set the item at a given index, called to implement assignment to `self[key]`. If the value is already in the
        set, it is unmodified.

        :param index: the index
        :param value: the new value
        :return: the old value at the index
        """
        if value not in self._map:
            old_value = self._items[index]
            self._items.__setitem__(index, value)
            self._map.pop(old_value)
            self._map[value] = index
        return

    def __delitem__(self, index):
        """
        Delete the element at the given index, called to implement deletion of `self[key]`.

        .. note::
            This method is O(n) because the implementation keeps the items and the indexes in separate structures.

        :param index: the index
        """
        value = self._items.pop(index)
        self._map.pop(value)
        for v in self._items[index:]:
            self._map[v] += 1
        return

    def __iter__(self):
        return iter(self._items)

    def __reversed__(self):
        return reversed(self._items)

    def __contains__(self, key):
        return key in self._map

    def __eq__(self, other):
        if self is other:
            return True
        if isinstance(other, self.__class__):
            return len(self) == len(other) and self.__le__(other)
        return NotImplemented

    def __ne__(self, other):
        if self is other:
            return False
        return not self == other

    def __str__(self):
        return str(self._items)

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, self._items)

    def add(self, item):
        super().append(item)

    def discard(self, key):
        if key in self:
            i = self._map[key]
            self._items.pop(i)
            self._map.pop(key)
            for k, v in self._map.items():
                if v >= i:
                    self._map[k] = v - 1

    def insert(self, index, x):
       if x not in self:
            self._items.insert(index, x)
            for k, v in self._map.items():
                if v >= index:
                    self._map[k] = v + 1
            self._map[x] = index

    def index(self, x, start=0, stop=None):
        """
        Return the index in the list of the item whose value is x. It is an error if there is no such item.
        If x is an iterable that is not a string, it returns a list of indices.
        Since items in a set are unique, the start and stop parameters are always ignored.

        :param x:
        :param start:
        :param stop:
        :return:
        """
        if _is_iterable(x):
            return [self.index(subkey) for subkey in x]
        try:
            return self._map[x]
        except KeyError as ex:
            raise ValueError from ex

    def copy(self):
        return OrderedSet(self)

    def pop(self, index=None):
        """
        If index is none, it behaves like set.pop, O(n)
        Else, it behaves like list pop.

        :param index:
        :return:
        """
        if index is not None:
            elem = self[index]
            self.discard(elem)
        else:
            elem = super().pop()
        return elem

    def sort(self, key=None, reverse=False):
        self._items.sort(key=key, reverse=reverse)
        for i, x in enumerate(self._items):
            self._map[x] = i

    # Enable if we want to enable pickle
    # def __getstate__(self):
    #     if len(self) == 0:
    #         # The state can't be an empty list.
    #         # We need to return a truthy value, or else __setstate__ won't be run.
    #         #
    #         # This could have been done more gracefully by always putting the state
    #         # in a tuple, but this way is backwards- and forwards- compatible with
    #         # previous versions of OrderedSet.
    #         return (None,)
    #     else:
    #         return list(self)
    #
    # def __setstate__(self, state):
    #     if state == (None,):
    #         self.__init__([])
    #     else:
    #         self.__init__(state)


class Bag(collections.Iterable, Mochila):
    """
    A Bag is a collection of objects. The order in which the appear in the collection is irrelevant and the same
    object can appear multiple times.

    A Bag behaves as the Python built-in *list* type, without the index access capabilities. Hence, a bag is the most
    basic implementation of an iterable.
    """
    def __init__(self, iterable=()):
        """
        Bags can be constructed using the type constructor `Bag()` or `Bag(iterable)`. The constructor builds a Bag
        whose items are taken from *iterable*. If *iterable* is not specified, a new empty Bag is returned.

        :param iterable: An iterable from which items are taken to build the Bag.
        """
        self._items = []
        self += iterable

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        order = random.sample(range(len(self._items)), k=len(self._items))
        for i in order:
            yield self._items[i]

    def __contains__(self, value):
        for v in self:
            if v is value or v == value:
                return True
        return False

    def __eq__(self, other):
        if self is other:
            return True
        if isinstance(other, self.__class__):
            if len(self) == len(other):
                unmatched = list(other)
                for element in self:
                    try:
                        unmatched.remove(element)
                    except ValueError:
                        return False
                return True
        return NotImplemented

    def __ne__(self, other):
        if self is other:
            return False
        if isinstance(other, self.__class__):
            if len(self) != len(other):
                return True
            else:
                unmatched = list(other)
                for element in self:
                    try:
                        unmatched.remove(element)
                    except ValueError:
                        return True
                return False
        return NotImplemented

    def __iadd__(self, iterable):
        if self is iterable:
            for i in range(len(iterable)):
                self.add(iterable[i])
        else:
            for v in iterable:
                self.add(v)
        return self

    def __str__(self):
        return str(self._items)

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, self._items)

    def add(self, value):
        """Add an element."""
        self._items.append(value)

    def count(self, value):
        """S.count(value) -> integer -- return number of occurrences of value"""
        return sum(1 for v in self if v == value)

    def clear(self):
        """S.clear() -> None -- remove all items from S"""
        try:
            while True:
                self.pop()
        except KeyError:
            pass

    def copy(self):
        """Create a copy of the Bag."""
        return Bag(self._items)

    def pop(self):
        """
        Pop a random item from the bag and return it. Raise KeyError if empty.
        :return:
        """
        #O(n) worst case remove first items, all need to be shifted"""
        it = iter(self)
        try:
            value = next(it)
        except StopIteration:
            raise KeyError
        self.remove(value)
        return value

    def remove(self, value):
        """
        Remove an occurrence of value. Raise ValueError if the value is not present.
        :param value:
        :return:
        """
        return self._items.remove(value)

    def discard(self, value):
        """Remove an element.  Do not raise an exception if absent."""
        try:
            self.remove(value)
        except ValueError:
            pass


class MultiSet(collections.MutableSet, Mochila):
    """
    A MultiSet is a collection of items. The order in which the items appear in the collection is irrelevant and the
    same item can appear multiple times. Items in the collection must be `hashable <https://docs.python.org/3.6/glossary.html#term-hashable>`_.
    A MultiSet is a generalization of the concept of a set that, unlike a set, allows multiple instances of the same
    element.

    """

    def __init__(*args, **kwds):
        """
        MultiSets can be constructed using the type constructor `MultiSet()` or from the count of elements from an
        iterable, or initialize the MultiSet from another mapping of elements to their counts (the counts must be
        numbers).

        >>> m = MultiSet()                           # a new, empty MultiSet
        >>> m = MultiSet('gallahad')                 # a new MultiSet from an iterable
        >>> m = MultiSet({'a': 4, 'b': 2})           # a new MultiSet from a mapping
        >>> m = MultiSet(a=4, b=2)                   # a new MultiSet from keyword args

        :param args:
        :param kwds:
        """
        if not args:
            raise TypeError("descriptor '__init__' of 'MultiSet' object needs an argument")
        self, *args = args
        self._items = collections.Counter(*args, **kwds)

    def __contains__(self, value):
        """
        O(n)
        :param value: 
        :return: 
        """
        return value in self._items

    def __len__(self):
        return sum(self._items.values())

    def __iter__(self):
        for i in self._items.elements():
            yield i

    def __getitem__(self, key):
        """
        Get the count for the given key, called to implement the evaluation of `self[key]`.
        If `key` is an iterable, you'll get the Sequence of counts corresponding to those keys (this is similar to
        NumPy's "fancy indexing").

        :param key: Index or list of the item(s) to get
        """
        if _is_iterable(key):
            if isinstance(key, frozenset):
                return self._items[key]
        return self._items[key]

    def __setitem__(self, index, value):
        """
        Set the count for a given key, called to implement the evaluation of `self[key] = value`.
        :param index:
        :param value:
        :return:
        """
        return self._items.__setitem__(index, value)

    def __delitem__(self, index):
        return self._items.__delitem__(index)

    def __missing__(self, key):
        'The count of elements not in the Counter is zero.'
        # Needed so that self[missing_item] does not raise KeyError
        return 0

    def __add__(self, other):
        if not isinstance(other, MultiSet):
            return NotImplemented
        return MultiSet(self._items.__add__(other._items))

    __radd__ = __add__

    def __iadd__(self, other):
        if not isinstance(other, MultiSet):
            return NotImplemented
        self._items.__iadd__(other._items)
        return self

    def __sub__(self, other):
        if not isinstance(other, MultiSet):
            return NotImplemented
        return MultiSet(self._items.__sub__(other._items))

    __rsub__ = __sub__

    def __isub__(self, other):
        if not isinstance(other, MultiSet):
            return NotImplemented
        self._items.__isub__(other._items)
        return self

    def __le__(self, other):
        if not isinstance(other, MultiSet):
            return NotImplemented
        if len(self) > len(other):
            return False
        for elem in self:
            if elem not in other:
                return False
            if self[elem] > other[elem]:
                return False
        return True

    def __lt__(self, other):
        if not isinstance(other, MultiSet):
            return NotImplemented
        return len(self) < len(other) and self.__le__(other)

    def __ge__(self, other):
        if not isinstance(other, MultiSet):
            return NotImplemented
        if len(self) < len(other):
            return False
        for elem in other:
            if elem not in self:
                return False
            if self[elem] < other[elem]:
                return False
        return True

    def __gt__(self, other):
        if not isinstance(other, MultiSet):
            return NotImplemented
        return len(self) > len(other) and self.__ge__(other)

    def __and__(self, other):
        if not isinstance(other, MultiSet):
            return NotImplemented
        return MultiSet(self._items & other._items)

    __rand__ = __and__

    def __or__(self, other):
        if not isinstance(other, MultiSet):
            return NotImplemented
        return MultiSet(self._items | other._items)

    __ror__ = __or__

    def __iand__(self, other):
        if not isinstance(other, MultiSet):
            return NotImplemented
        self._items &= other._items
        return self

    def __ior__(self, other):
        if not isinstance(other, MultiSet):
            return NotImplemented
        self._items |= other._items
        return self

    def __xor__(self, other):
        if not isinstance(other, MultiSet):
            return NotImplemented
        keep = self._items.keys() ^ other._items.keys()
        result = MultiSet({k: self._items[k] for k in keep if k in self._items})
        result._items.update({k: other._items[k] for k in keep if k in other._items})
        return result

    def __ixor__(self, other):
        if not isinstance(other, MultiSet):
            return NotImplemented
        keep = self._items.keys() ^ other._items.keys()
        self_pop = self._items.pop
        for k in other._items.keys():
            self_pop(k, None)
        self._items.update({k: other._items[k] for k in keep if k in other._items})
        return self

    # def __repr__(self):
    #     return 'MultiSet({})'.format(list(self.elements()))
    #
    # def __str__(self):
    #     format_str = '{}[{}]'.format
    #     return 'MultiSet({})'.format(', '.join(format_str(k, v) for k, v in self._items()))

    def add(self, value, n_copies=1):
        self._items[value] = self._items[value] + n_copies

    def copy(self):
        return MultiSet(self._items)

    def discard(self, value, n_copies=1):
        try:
            self._items[value] -= n_copies
            if self._items[value] <= 1:
                del self._items[value]
        except ValueError:
            pass    # discard doesn't raise an exception

    def most_common(self, n=None):
        """
        Return a list of the n most common elements and their counts from the most common to the least. If n is omitted
        or None, most_common() returns all elements in the MultiSet. Elements with equal counts are ordered arbitrarily.

        :return: A list of (item, count) tuples sorted by highest count number
        """
        return self._items.most_common(n)

    def tally(self):
        """
        Returns an iterator of the counts for each element in the MultiSet. The order of iteration is arbitrary.
        """
        for i, count in self._items.items():
            yield (i, count)

    def unique(self):
        """
        Returns the number of unique elements in the MultiSet.

        :return: The count of unique elements
        """
        return len(self.keys())

    def count(self, value):
        """
        Return the number of times the element is in the MultiSet. This method is syntactic sugar for MultiSet[value]

        :param value: the element in the MultiSet
        :return:
        """
        return self._items[value]

    def remove(self, value):
        if value in self:
            if self[value] == 1:
                del self[value]
            else:
                self[value] -= 1
        else:
            raise ValueError('{!r} not in MultiSet'.format(value))

    def __eq__(self, right):
        if not isinstance(right, MultiSet):
            raise TypeError(('Cannot compare MultiSet with object of type {!r}. Can only '
                             'compare MultiSet with MultiSet').format(type(right).__name__))
        else:
            return self._items.__eq__(right._items)

    def __ne__(self, right):
        return not self.__eq__(right)


