#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x2bd7a123

# Compiled with Coconut version 1.3.1-post_dev3 [Dead Parrot]

# Coconut Header: -------------------------------------------------------------

import sys as _coconut_sys
py_chr, py_filter, py_hex, py_input, py_int, py_map, py_object, py_oct, py_open, py_print, py_range, py_str, py_zip, py_filter, py_reversed, py_enumerate = chr, filter, hex, input, int, map, object, oct, open, print, range, str, zip, filter, reversed, enumerate
class _coconut:
    import collections, copy, functools, imp, itertools, operator, types, weakref
    import pickle
    OrderedDict = collections.OrderedDict
    if _coconut_sys.version_info < (3, 3):
        abc = collections
    else:
        import collections.abc as abc
    Exception, IndexError, KeyError, NameError, TypeError, ValueError, StopIteration, classmethod, dict, enumerate, filter, frozenset, getattr, hasattr, hash, id, int, isinstance, issubclass, iter, len, list, map, min, max, next, object, property, range, reversed, set, slice, str, sum, super, tuple, zip, repr = Exception, IndexError, KeyError, NameError, TypeError, ValueError, StopIteration, classmethod, dict, enumerate, filter, frozenset, getattr, hasattr, hash, id, int, isinstance, issubclass, iter, len, list, map, min, max, next, object, property, range, reversed, set, slice, str, sum, super, tuple, zip, repr
def _coconut_NamedTuple(name, fields):
    return _coconut.collections.namedtuple(name, [x for x, t in fields])
class MatchError(Exception):
    """Pattern-matching error. Has attributes .pattern and .value."""
    __slots__ = ("pattern", "value")
class _coconut_tail_call:
    __slots__ = ("func", "args", "kwargs")
    def __init__(self, func, *args, **kwargs):
        self.func, self.args, self.kwargs = func, args, kwargs
_coconut_tco_func_dict = {}
def _coconut_tco(func):
    @_coconut.functools.wraps(func)
    def tail_call_optimized_func(*args, **kwargs):
        call_func = func
        while True:
            wkref = _coconut_tco_func_dict.get(_coconut.id(call_func))
            if wkref is not None and wkref() is call_func:
                call_func = call_func._coconut_tco_func
            result = call_func(*args, **kwargs)  # pass --no-tco to clean up your traceback
            if not isinstance(result, _coconut_tail_call):
                return result
            call_func, args, kwargs = result.func, result.args, result.kwargs
    tail_call_optimized_func._coconut_tco_func = func
    _coconut_tco_func_dict[_coconut.id(tail_call_optimized_func)] = _coconut.weakref.ref(tail_call_optimized_func)
    return tail_call_optimized_func
def _coconut_igetitem(iterable, index):
    if isinstance(iterable, (_coconut_reversed, _coconut_map, _coconut.filter, _coconut.zip, _coconut_enumerate, _coconut_count, _coconut.abc.Sequence)):
        return iterable[index]
    if not _coconut.isinstance(index, _coconut.slice):
        if index < 0:
            return _coconut.collections.deque(iterable, maxlen=-index)[0]
        return _coconut.next(_coconut.itertools.islice(iterable, index, index + 1))
    if index.start is not None and index.start < 0 and (index.stop is None or index.stop < 0) and index.step is None:
        queue = _coconut.collections.deque(iterable, maxlen=-index.start)
        if index.stop is not None:
            queue = _coconut.tuple(queue)[:index.stop - index.start]
        return queue
    if (index.start is not None and index.start < 0) or (index.stop is not None and index.stop < 0) or (index.step is not None and index.step < 0):
        return _coconut.tuple(iterable)[index]
    return _coconut.itertools.islice(iterable, index.start, index.stop, index.step)
class _coconut_base_compose:
    __slots__ = ("func", "funcstars")
    def __init__(self, func, *funcstars):
        self.func = func
        self.funcstars = []
        for f, star in funcstars:
            if isinstance(f, _coconut_base_compose):
                self.funcstars.append((f.func, star))
                self.funcstars += f.funcstars
            else:
                self.funcstars.append((f, star))
    def __call__(self, *args, **kwargs):
        arg = self.func(*args, **kwargs)
        for f, star in self.funcstars:
            arg = f(*arg) if star else f(arg)
        return arg
    def __repr__(self):
        return _coconut.repr(self.func) + " " + " ".join(("..*> " if star else "..> ") + _coconut.repr(f) for f, star in self.funcstars)
    def __reduce__(self):
        return (self.__class__, (self.func,) + _coconut.tuple(self.funcstars))
def _coconut_forward_compose(func, *funcs): return _coconut_base_compose(func, *((f, False) for f in funcs))
def _coconut_back_compose(*funcs): return _coconut_forward_compose(*_coconut.reversed(funcs))
def _coconut_forward_star_compose(func, *funcs): return _coconut_base_compose(func, *((f, True) for f in funcs))
def _coconut_back_star_compose(*funcs): return _coconut_forward_star_compose(*_coconut.reversed(funcs))
def _coconut_pipe(x, f): return f(x)
def _coconut_star_pipe(xs, f): return f(*xs)
def _coconut_back_pipe(f, x): return f(x)
def _coconut_back_star_pipe(f, xs): return f(*xs)
def _coconut_bool_and(a, b): return a and b
def _coconut_bool_or(a, b): return a or b
def _coconut_none_coalesce(a, b): return a if a is not None else b
def _coconut_minus(a, *rest):
    if not rest:
        return -a
    for b in rest:
        a = a - b
    return a
@_coconut.functools.wraps(_coconut.itertools.tee)
def tee(iterable, n=2):
    if n >= 0 and _coconut.isinstance(iterable, (_coconut.tuple, _coconut.frozenset)):
        return (iterable,) * n
    if n > 0 and (_coconut.hasattr(iterable, "__copy__") or _coconut.isinstance(iterable, _coconut.abc.Sequence)):
        return (iterable,) + _coconut.tuple(_coconut.copy.copy(iterable) for _ in _coconut.range(n - 1))
    return _coconut.itertools.tee(iterable, n)
class reiterable:
    """Allows an iterator to be iterated over multiple times."""
    __slots__ = ("iter",)
    def __init__(self, iterable):
        self.iter = iterable
    def __iter__(self):
        self.iter, out = _coconut_tee(self.iter)
        return _coconut.iter(out)
    def __getitem__(self, index):
        return _coconut_igetitem(_coconut.iter(self), index)
    def __reversed__(self):
        return _coconut_reversed(_coconut.iter(self))
    def __len__(self):
        return _coconut.len(self.iter)
    def __repr__(self):
        return "reiterable(" + _coconut.repr(self.iter) + ")"
    def __reduce__(self):
        return (self.__class__, (self.iter,))
    def __copy__(self):
        return self.__class__(_coconut.copy.copy(self.iter))
    def __fmap__(self, func):
        return _coconut_map(func, self)
class scan:
    """Reduce func over iterable, yielding intermediate results."""
    __slots__ = ("func", "iter")
    def __init__(self, func, iterable):
        self.func, self.iter = func, iterable
    def __iter__(self):
        acc = empty_acc = _coconut.object()
        for item in self.iter:
            if acc is empty_acc:
                acc = item
            else:
                acc = self.func(acc, item)
            yield acc
    def __len__(self):
        return _coconut.len(self.iter)
    def __repr__(self):
        return "scan(" + _coconut.repr(self.iter) + ")"
    def __reduce__(self):
        return (self.__class__, (self.func, self.iter))
    def __copy__(self):
        return self.__class__(self.func, _coconut.copy.copy(self.iter))
    def __fmap__(self, func):
        return _coconut_map(func, self)
class reversed:
    __slots__ = ("_iter",)
    if hasattr(_coconut.map, "__doc__"):
        __doc__ = _coconut.reversed.__doc__
    def __new__(cls, iterable):
        if _coconut.isinstance(iterable, _coconut.range):
            return iterable[::-1]
        if not _coconut.hasattr(iterable, "__reversed__") or _coconut.isinstance(iterable, (_coconut.list, _coconut.tuple)):
            return _coconut.object.__new__(cls)
        return _coconut.reversed(iterable)
    def __init__(self, iterable):
        self._iter = iterable
    def __iter__(self):
        return _coconut.iter(_coconut.reversed(self._iter))
    def __getitem__(self, index):
        if _coconut.isinstance(index, _coconut.slice):
            return _coconut_igetitem(self._iter, _coconut.slice(-(index.start + 1) if index.start is not None else None, -(index.stop + 1) if index.stop else None, -(index.step if index.step is not None else 1)))
        return _coconut_igetitem(self._iter, -(index + 1))
    def __reversed__(self):
        return self._iter
    def __len__(self):
        return _coconut.len(self._iter)
    def __repr__(self):
        return "reversed(" + _coconut.repr(self._iter) + ")"
    def __hash__(self):
        return -_coconut.hash(self._iter)
    def __reduce__(self):
        return (self.__class__, (self._iter,))
    def __copy__(self):
        return self.__class__(_coconut.copy.copy(self._iter))
    def __eq__(self, other):
        return isinstance(other, self.__class__) and self._iter == other._iter
    def __contains__(self, elem):
        return elem in self._iter
    def count(self, elem):
        """Count the number of times elem appears in the reversed iterator."""
        return self._iter.count(elem)
    def index(self, elem):
        """Find the index of elem in the reversed iterator."""
        return _coconut.len(self._iter) - self._iter.index(elem) - 1
    def __fmap__(self, func):
        return self.__class__(_coconut_map(func, self._iter))
class map(_coconut.map):
    __slots__ = ("_func", "_iters")
    if hasattr(_coconut.map, "__doc__"):
        __doc__ = _coconut.map.__doc__
    def __new__(cls, function, *iterables):
        new_map = _coconut.map.__new__(cls, function, *iterables)
        new_map._func, new_map._iters = function, iterables
        return new_map
    def __getitem__(self, index):
        if _coconut.isinstance(index, _coconut.slice):
            return self.__class__(self._func, *(_coconut_igetitem(i, index) for i in self._iters))
        return self._func(*(_coconut_igetitem(i, index) for i in self._iters))
    def __reversed__(self):
        return self.__class__(self._func, *(_coconut_reversed(i) for i in self._iters))
    def __len__(self):
        return _coconut.min(_coconut.len(i) for i in self._iters)
    def __repr__(self):
        return "map(" + _coconut.repr(self._func) + ", " + ", ".join((_coconut.repr(i) for i in self._iters)) + ")"
    def __reduce__(self):
        return (self.__class__, (self._func,) + self._iters)
    def __reduce_ex__(self, _):
        return self.__reduce__()
    def __copy__(self):
        return self.__class__(self._func, *_coconut.map(_coconut.copy.copy, self._iters))
    def __fmap__(self, func):
        return self.__class__(_coconut_forward_compose(self._func, func), *self._iters)
class parallel_map(map):
    """Multi-process implementation of map using concurrent.futures.
    Requires arguments to be pickleable."""
    __slots__ = ()
    def __iter__(self):
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor() as executor:
            return _coconut.iter(_coconut.tuple(executor.map(self._func, *self._iters)))
    def __repr__(self):
        return "parallel_" + _coconut_map.__repr__(self)
class concurrent_map(map):
    """Multi-thread implementation of map using concurrent.futures."""
    __slots__ = ()
    def __iter__(self):
        from concurrent.futures import ThreadPoolExecutor
        from multiprocessing import cpu_count  # cpu_count() * 5 is the default Python 3.5 thread count
        with ThreadPoolExecutor(cpu_count() * 5) as executor:
            return _coconut.iter(_coconut.tuple(executor.map(self._func, *self._iters)))
    def __repr__(self):
        return "concurrent_" + _coconut_map.__repr__(self)
class filter(_coconut.filter):
    __slots__ = ("_func", "_iter")
    if hasattr(_coconut.filter, "__doc__"):
        __doc__ = _coconut.filter.__doc__
    def __new__(cls, function, iterable):
        new_filter = _coconut.filter.__new__(cls, function, iterable)
        new_filter._func, new_filter._iter = function, iterable
        return new_filter
    def __reversed__(self):
        return self.__class__(self._func, _coconut_reversed(self._iter))
    def __repr__(self):
        return "filter(" + _coconut.repr(self._func) + ", " + _coconut.repr(self._iter) + ")"
    def __reduce__(self):
        return (self.__class__, (self._func, self._iter))
    def __reduce_ex__(self, _):
        return self.__reduce__()
    def __copy__(self):
        return self.__class__(self._func, _coconut.copy.copy(self._iter))
    def __fmap__(self, func):
        return _coconut_map(func, self)
class zip(_coconut.zip):
    __slots__ = ("_iters",)
    if hasattr(_coconut.zip, "__doc__"):
        __doc__ = _coconut.zip.__doc__
    def __new__(cls, *iterables):
        new_zip = _coconut.zip.__new__(cls, *iterables)
        new_zip._iters = iterables
        return new_zip
    def __getitem__(self, index):
        if _coconut.isinstance(index, _coconut.slice):
            return self.__class__(*(_coconut_igetitem(i, index) for i in self._iters))
        return _coconut.tuple(_coconut_igetitem(i, index) for i in self._iters)
    def __reversed__(self):
        return self.__class__(*(_coconut_reversed(i) for i in self._iters))
    def __len__(self):
        return _coconut.min(_coconut.len(i) for i in self._iters)
    def __repr__(self):
        return "zip(" + ", ".join((_coconut.repr(i) for i in self._iters)) + ")"
    def __reduce__(self):
        return (self.__class__, self._iters)
    def __reduce_ex__(self, _):
        return self.__reduce__()
    def __copy__(self):
        return self.__class__(*_coconut.map(_coconut.copy.copy, self._iters))
    def __fmap__(self, func):
        return _coconut_map(func, self)
class enumerate(_coconut.enumerate):
    __slots__ = ("_iter", "_start")
    if hasattr(_coconut.enumerate, "__doc__"):
        __doc__ = _coconut.enumerate.__doc__
    def __new__(cls, iterable, start=0):
        new_enumerate = _coconut.enumerate.__new__(cls, iterable, start)
        new_enumerate._iter, new_enumerate._start = iterable, start
        return new_enumerate
    def __getitem__(self, index):
        if _coconut.isinstance(index, _coconut.slice):
            return self.__class__(_coconut_igetitem(self._iter, index), self._start + (0 if index.start is None else index.start if index.start >= 0 else len(self._iter) + index.start))
        return (self._start + index, _coconut_igetitem(self._iter, index))
    def __len__(self):
        return _coconut.len(self._iter)
    def __repr__(self):
        return "enumerate(" + _coconut.repr(self._iter) + ", " + _coconut.repr(self._start) + ")"
    def __reduce__(self):
        return (self.__class__, (self._iter, self._start))
    def __reduce_ex__(self, _):
        return self.__reduce__()
    def __copy__(self):
        return self.__class__(_coconut.copy.copy(self._iter), self._start)
    def __fmap__(self, func):
        return _coconut_map(func, self)
class count:
    """count(start, step) returns an infinite iterator starting at start and increasing by step."""
    __slots__ = ("start", "step")
    def __init__(self, start=0, step=1):
        self.start, self.step = start, step
    def __iter__(self):
        while True:
            yield self.start
            self.start += self.step
    def __contains__(self, elem):
        return elem >= self.start and (elem - self.start) % self.step == 0
    def __getitem__(self, index):
        if _coconut.isinstance(index, _coconut.slice) and (index.start is None or index.start >= 0) and (index.stop is None or index.stop >= 0):
            if index.stop is None:
                return self.__class__(self.start + (index.start if index.start is not None else 0), self.step * (index.step if index.step is not None else 1))
            if _coconut.isinstance(self.start, _coconut.int) and _coconut.isinstance(self.step, _coconut.int):
                return _coconut.range(self.start + self.step * (index.start if index.start is not None else 0), self.start + self.step * index.stop, self.step * (index.step if index.step is not None else 1))
            return _coconut_map(self.__getitem__, _coconut.range(index.start if index.start is not None else 0, index.stop, index.step if index.step is not None else 1))
        if index >= 0:
            return self.start + self.step * index
        raise _coconut.IndexError("count indices must be positive")
    def count(self, elem):
        """Count the number of times elem appears in the count."""
        return int(elem in self)
    def index(self, elem):
        """Find the index of elem in the count."""
        if elem not in self:
            raise _coconut.ValueError(_coconut.repr(elem) + " is not in count")
        return (elem - self.start) // self.step
    def __repr__(self):
        return "count(" + _coconut.str(self.start) + ", " + _coconut.str(self.step) + ")"
    def __hash__(self):
        return _coconut.hash((self.start, self.step))
    def __reduce__(self):
        return (self.__class__, (self.start, self.step))
    def __copy__(self):
        return self.__class__(self.start, self.step)
    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.start == other.start and self.step == other.step
    def __fmap__(self, func):
        return _coconut_map(func, self)
class groupsof:
    """groupsof(n, iterable) splits iterable into groups of size n.
    If the length of the iterable is not divisible by n, the last group may be of size < n."""
    __slots__ = ("group_size", "iter")
    def __init__(self, n, iterable):
        self.iter = iterable
        try:
            self.group_size = _coconut.int(n)
        except _coconut.ValueError:
            raise _coconut.TypeError("group size must be an int; not %r" % (n,))
        if self.group_size <= 0:
            raise _coconut.ValueError("group size must be > 0; not %s" % (self.group_size,))
    def __iter__(self):
        loop, iterator = True, _coconut.iter(self.iter)
        while loop:
            group = []
            for _ in _coconut.range(self.group_size):
                try:
                    group.append(_coconut.next(iterator))
                except _coconut.StopIteration:
                    loop = False
                    break
            if group:
                yield _coconut.tuple(group)
    def __len__(self):
        return _coconut.len(self.iter)
    def __repr__(self):
        return "groupsof(%r)" % (_coconut.repr(self.iter),)
    def __reduce__(self):
        return (self.__class__, (self.group_size, self.iter))
    def __copy__(self):
        return self.__class__(self.group_size, _coconut.copy.copy(self.iter))
    def __fmap__(self, func):
        return _coconut_map(func, self)
def recursive_iterator(func):
    """Decorator that optimizes a function for iterator recursion."""
    tee_store, backup_tee_store = {}, []
    @_coconut.functools.wraps(func)
    def recursive_iterator_func(*args, **kwargs):
        key, use_backup = (args, _coconut.frozenset(kwargs)), False
        try:
            hash(key)
        except _coconut.Exception:
            try:
                key = _coconut.pickle.dumps(key, -1)
            except _coconut.Exception:
                use_backup = True
        if use_backup:
            for i, (k, v) in _coconut.enumerate(backup_tee_store):
                if k == key:
                    to_tee, store_pos = v, i
                    break
            else:  # no break
                to_tee, store_pos = func(*args, **kwargs), None
            to_store, to_return = _coconut_tee(to_tee)
            if store_pos is None:
                backup_tee_store.append([key, to_store])
            else:
                backup_tee_store[store_pos][1] = to_store
        else:
            tee_store[key], to_return = _coconut_tee(tee_store.get(key) or func(*args, **kwargs))
        return to_return
    return recursive_iterator_func
def addpattern(base_func):
    """Decorator to add a new case to a pattern-matching function,
    where the new case is checked last."""
    def pattern_adder(func):
        @_coconut_tco
        @_coconut.functools.wraps(func)
        def add_pattern_func(*args, **kwargs):
            try:
                return base_func(*args, **kwargs)
            except _coconut_MatchError:
                return _coconut_tail_call(func, *args, **kwargs)
        return add_pattern_func
    return pattern_adder
def prepattern(base_func):
    """DEPRECATED: Use addpattern instead."""
    def pattern_prepender(func):
        return addpattern(func)(base_func)
    return pattern_prepender
class _coconut_partial:
    __slots__ = ("func", "_argdict", "_arglen", "_stargs", "keywords")
    if hasattr(_coconut.functools.partial, "__doc__"):
        __doc__ = _coconut.functools.partial.__doc__
    def __init__(self, func, argdict, arglen, *args, **kwargs):
        self.func, self._argdict, self._arglen, self._stargs, self.keywords = func, argdict, arglen, args, kwargs
    def __reduce__(self):
        return (self.__class__, (self.func, self._argdict, self._arglen) + self._stargs, self.keywords)
    def __setstate__(self, keywords):
        self.keywords = keywords
    @property
    def args(self):
        return _coconut.tuple(self._argdict.get(i) for i in _coconut.range(self._arglen)) + self._stargs
    def __call__(self, *args, **kwargs):
        callargs = []
        argind = 0
        for i in _coconut.range(self._arglen):
            if i in self._argdict:
                callargs.append(self._argdict[i])
            elif argind >= _coconut.len(args):
                raise _coconut.TypeError("expected at least " + _coconut.str(self._arglen - _coconut.len(self._argdict)) + " argument(s) to " + _coconut.repr(self))
            else:
                callargs.append(args[argind])
                argind += 1
        callargs += self._stargs
        callargs += args[argind:]
        kwargs.update(self.keywords)
        return self.func(*callargs, **kwargs)
    def __repr__(self):
        args = []
        for i in _coconut.range(self._arglen):
            if i in self._argdict:
                args.append(_coconut.repr(self._argdict[i]))
            else:
                args.append("?")
        for arg in self._stargs:
            args.append(_coconut.repr(arg))
        return _coconut.repr(self.func) + "$(" + ", ".join(args) + ")"
def makedata(data_type, *args, **kwargs):
    """Call the original constructor of the given data type or class with the given arguments."""
    if _coconut.hasattr(data_type, "_make") and (_coconut.issubclass(data_type, _coconut.tuple) or _coconut.isinstance(data_type, _coconut.tuple)):
        return data_type._make(args, **kwargs)
    return _coconut.super(data_type, data_type).__new__(data_type, *args, **kwargs)
def datamaker(data_type):
    """DEPRECATED: Use makedata instead."""
    return _coconut.functools.partial(makedata, data_type)
def consume(iterable, keep_last=0):
    """consume(iterable, keep_last) fully exhausts iterable and return the last keep_last elements."""
    return _coconut.collections.deque(iterable, maxlen=keep_last)  # fastest way to exhaust an iterator
class starmap(_coconut.itertools.starmap):
    __slots__ = ("_func", "_iter")
    if hasattr(_coconut.itertools.starmap, "__doc__"):
        __doc__ = _coconut.itertools.starmap.__doc__
    def __new__(cls, function, iterable):
        new_map = _coconut.itertools.starmap.__new__(cls, function, iterable)
        new_map._func, new_map._iter = function, iterable
        return new_map
    def __getitem__(self, index):
        if _coconut.isinstance(index, _coconut.slice):
            return self.__class__(self._func, _coconut_igetitem(self._iter, index))
        return self._func(*_coconut_igetitem(self._iter, index))
    def __reversed__(self):
        return self.__class__(self._func, *_coconut_reversed(self._iter))
    def __len__(self):
        return _coconut.len(self._iter)
    def __repr__(self):
        return "starmap(" + _coconut.repr(self._func) + ", " + _coconut.repr(self._iter) + ")"
    def __reduce__(self):
        return (self.__class__, (self._func, self._iter))
    def __reduce_ex__(self, _):
        return self.__reduce__()
    def __copy__(self):
        return self.__class__(self._func, _coconut.copy.copy(self._iter))
    def __fmap__(self, func):
        return self.__class__(_coconut_forward_compose(self._func, func), self._iter)
def fmap(func, obj):
    """fmap(func, obj) creates a copy of obj with func applied to its contents.
    Override by defining .__fmap__(func)."""
    if _coconut.hasattr(obj, "__fmap__"):
        return obj.__fmap__(func)
    args = _coconut_starmap(func, obj.items()) if _coconut.isinstance(obj, _coconut.abc.Mapping) else _coconut_map(func, obj)
    if _coconut.isinstance(obj, _coconut.tuple) and _coconut.hasattr(obj, "_make"):
        return obj._make(args)
    if _coconut.isinstance(obj, (_coconut.map, _coconut.range, _coconut.abc.Iterator)):
        return args
    if _coconut.isinstance(obj, _coconut.str):
        return "".join(args)
    return obj.__class__(args)
_coconut_MatchError, _coconut_count, _coconut_enumerate, _coconut_reversed, _coconut_map, _coconut_starmap, _coconut_tee, _coconut_zip, reduce, takewhile, dropwhile = MatchError, count, enumerate, reversed, map, starmap, tee, zip, _coconut.functools.reduce, _coconut.itertools.takewhile, _coconut.itertools.dropwhile

# Compiled Coconut: -----------------------------------------------------------

# Standard modules
import bz2  # line 2
import codecs  # line 2
import collections  # line 2
import difflib  # line 2
import fnmatch  # line 2
import hashlib  # line 2
import io  # line 2
import json  # line 2
import logging  # line 2
import mimetypes  # line 2
import os  # line 2
import shutil  # line 2
sys = _coconut_sys  # line 2
import time  # line 2
try:  # line 3
    from typing import Any  # only required for mypy  # line 4
    from typing import Dict  # only required for mypy  # line 4
    from typing import FrozenSet  # only required for mypy  # line 4
    from typing import IO  # only required for mypy  # line 4
    from typing import List  # only required for mypy  # line 4
    from typing import Set  # only required for mypy  # line 4
    from typing import Tuple  # only required for mypy  # line 4
    from typing import Type  # only required for mypy  # line 4
    from typing import TypeVar  # only required for mypy  # line 4
    from typing import Union  # only required for mypy  # line 4
    Number = Union[int, float]  # line 5
except:  # Python 2  # line 6
    pass  # Python 2  # line 6
try:  # created and used by setup.py  # line 7
    from sos import version  # created and used by setup.py  # line 7
except:  # Python 2 logic  # line 8
    import version  # Python 2 logic  # line 8

# External dependencies
try:  # optional dependency  # line 11
    import configr  # optional dependency  # line 11
except:  # declare as undefined  # line 12
    configr = None  # declare as undefined  # line 12
#from enforce import runtime_validation  # https://github.com/RussBaz/enforce  TODO doesn't work for "data" types
#@runtime_validation
UTF8 = "utf_8"  # early used constant  # line 15
try:  # line 16
    import chardet  # https://github.com/chardet/chardet  # line 17
    def detect(binary: 'bytes') -> 'str':  # line 18
        return chardet.detect(binary)["encoding"]  # line 18
except:  # Python 2 workaround  # line 19
    def detect(binary: 'bytes') -> 'str':  # Guess the encoding  # line 20
        try:  # Guess the encoding  # line 20
            binary.decode(UTF8)  # Guess the encoding  # line 20
            return UTF8  # line 21
        except UnicodeError:  # line 22
            pass  # line 22
        try:  # line 23
            binary.decode("utf_16")  # line 23
            return "utf_16"  # line 23
        except UnicodeError:  # line 24
            pass  # line 24
        try:  # line 25
            binary.decode("cp1252")  # line 25
            return "cp1252"  # line 25
        except UnicodeError:  # line 26
            pass  # line 26
        return "ascii"  # this code will never be reached, as above is an 8-bit charset that always matches  # line 27


class BranchInfo(_coconut_NamedTuple("BranchInfo", [("number", 'int'), ("ctime", 'int'), ("name", '_coconut.typing.Optional[str]'), ("insync", 'bool'), ("tracked", 'List[str]')])):  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 30
    __slots__ = ()  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 30
    __ne__ = _coconut.object.__ne__  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 30
    def __new__(_cls, number, ctime, name=None, insync=False, tracked=[]):  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 30
        return _coconut.tuple.__new__(_cls, (number, ctime, name, insync, tracked))  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 30
# tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place
class CommitInfo(_coconut_NamedTuple("CommitInfo", [("number", 'int'), ("ctime", 'int'), ("message", '_coconut.typing.Optional[str]')])):  # line 31
    __slots__ = ()  # line 31
    __ne__ = _coconut.object.__ne__  # line 31
    def __new__(_cls, number, ctime, message=None):  # line 31
        return _coconut.tuple.__new__(_cls, (number, ctime, message))  # line 31

class PathInfo(_coconut_NamedTuple("PathInfo", [("namehash", 'str'), ("size", '_coconut.typing.Optional[int]'), ("mtime", 'int'), ("hash", 'str')])):  # size == None means deleted in this revision  # line 32
    __slots__ = ()  # size == None means deleted in this revision  # line 32
    __ne__ = _coconut.object.__ne__  # size == None means deleted in this revision  # line 32
class ChangeSet(_coconut_NamedTuple("ChangeSet", [("additions", 'Dict[str, PathInfo]'), ("deletions", 'Dict[str, PathInfo]'), ("modifications", 'Dict[str, PathInfo]')])):  # avoid default assignment of {} as it leads to runtime errors (contains data on init for unknown reason)  # line 33
    __slots__ = ()  # avoid default assignment of {} as it leads to runtime errors (contains data on init for unknown reason)  # line 33
    __ne__ = _coconut.object.__ne__  # avoid default assignment of {} as it leads to runtime errors (contains data on init for unknown reason)  # line 33
class Range(_coconut_NamedTuple("Range", [("tipe", 'int'), ("indexes", '_coconut.typing.Sequence[int]')])):  # MergeBlockType[1,2,4], line number, length  # line 34
    __slots__ = ()  # MergeBlockType[1,2,4], line number, length  # line 34
    __ne__ = _coconut.object.__ne__  # MergeBlockType[1,2,4], line number, length  # line 34
class MergeBlock(_coconut_NamedTuple("MergeBlock", [("tipe", 'int'), ("lines", '_coconut.typing.Sequence[str]'), ("line", 'int'), ("replaces", '_coconut.typing.Optional[MergeBlock]'), ("changes", '_coconut.typing.Optional[Range]')])):  # line 35
    __slots__ = ()  # line 35
    __ne__ = _coconut.object.__ne__  # line 35
    def __new__(_cls, tipe, lines, line, replaces=None, changes=None):  # line 35
        return _coconut.tuple.__new__(_cls, (tipe, lines, line, replaces, changes))  # line 35


class ConflictResolution:  # prefer their changes, prefer my changes, ask user for each change, go to next deeper level (e.g. from files to lines, characters)  # line 37
    THEIRS, MINE, ASK, NEXT = range(4)  # prefer their changes, prefer my changes, ask user for each change, go to next deeper level (e.g. from files to lines, characters)  # line 37
class MergeOperation:  # insert remote changes into current, remove remote deletions from current, do both (replicate remote state) TODO handle inline-operations separate?  # line 38
    INSERT, REMOVE, BOTH = 1, 2, 3  # insert remote changes into current, remove remote deletions from current, do both (replicate remote state) TODO handle inline-operations separate?  # line 38
class MergeBlockType:  # modify = intra-line changes  # line 39
    KEEP, INSERT, REMOVE, REPLACE, MODIFY, MOVE = range(6)  # modify = intra-line changes  # line 39

class Accessor(dict):  # line 41
    ''' Dictionary with attribute access. Writing only supported via dictionary access. '''  # line 42
    def __init__(_, mapping) -> 'None':  # line 43
        dict.__init__(_, mapping)  # line 43
    @_coconut_tco  # line 44
    def __getattribute__(_, name: 'str') -> 'List[str]':  # line 44
        try:  # line 45
            return _[name]  # line 45
        except:  # line 46
            return _coconut_tail_call(dict.__getattribute__, _, name)  # line 46

# Constants
APPNAME = "Subversion Offline Solution  V.%s  (C) Arne Bachmann" % version.__release_version__  # type: str  # line 49
CONFIGURABLE_FLAGS = ["strict", "track", "picky", "compress"]  # line 50
CONFIGURABLE_LISTS = ["texttype", "bintype", "ignores", "ignoreDirs", "ignoresWhitelist", "ignoreDirsWhitelist"]  # line 51
TRUTH_VALUES = ["true", "yes", "on", "1", "enable", "enabled"]  # all lower-case normalized  # line 52
metaFolder = ".sos"  # type: str  # line 53
metaFile = ".meta"  # type: str  # line 54
bufSize = 1 << 20  # type: int  # 1 MiB  # line 55
vcsFolders = {".svn": "svn", ".git": "git", ".bzr": "bzr", ".hg": "hg", ".fslckout": " fossil", ".CVS": "cvs"}  # type: Dict[str, str]  # line 56
vcsBranches = {"svn": "trunk", "git": "master", "bzr": "trunk", "hg": "default", "fossil": None, "cvs": None}  # type: Dict[str, _coconut.typing.Optional[str]]  # line 57
defaults = Accessor({"strict": False, "track": False, "picky": False, "compress": True, "texttype": [], "bintype": [], "ignoreDirs": [".*", "__pycache__"], "ignoreDirsWhitelist": [], "ignores": ["__coconut__.py", "*.bak", "*.py[cdo]", "*.class", ".fslckout"], "ignoresWhitelist": []})  # type: Accessor  # line 58

def Exit(message: 'str'="") -> 'None':  # line 60
    print(message, file=sys.stderr)  # line 60
    sys.exit(1)  # line 60

@_coconut_tco  # dynamic Python2/3. don't simplify, eval must be inside function for unknown reason  # line 62
def user_input(msg: 'str') -> 'str':  # dynamic Python2/3. don't simplify, eval must be inside function for unknown reason  # line 62
    return _coconut_tail_call(eval("input" if sys.version_info.major >= 3 else "raw_input"), msg)  # dynamic Python2/3. don't simplify, eval must be inside function for unknown reason  # line 62

try:  # line 64
    Splittable = TypeVar("Splittable", str, bytes)  # line 64
except:  # Python 2  # line 65
    pass  # Python 2  # line 65
def safeSplit(s: 'Splittable', d: '_coconut.typing.Optional[Splittable]'=None) -> '_coconut.typing.Sequence[Splittable]':  # line 66
    return s.split(("\n" if isinstance(s, str) else b"\n") if d is None else d) if len(s) > 0 else []  # line 66

@_coconut_tco  # line 68
def sjoin(*s: 'Tuple[Any]') -> 'str':  # line 68
    return _coconut_tail_call(" ".join, [str(e) for e in s if e != ''])  # line 68

@_coconut_tco  # line 70
def hashStr(datas: 'str') -> 'str':  # line 70
    return _coconut_tail_call(hashlib.sha256(datas.encode(UTF8)).hexdigest)  # line 70

@_coconut_tco  # line 72
def hashFile(path: 'str', compress: 'bool', saveTo: '_coconut.typing.Optional[str]'=None) -> 'str':  # line 72
    ''' Calculate hash of file contents. '''  # line 73
    hash = hashlib.sha256()  # line 74
    to = openIt(saveTo, "w", compress) if saveTo else None  # line 75
    with open(path, "rb") as fd:  # line 76
        while True:  # line 77
            buffer = fd.read(bufSize)  # line 78
            hash.update(buffer)  # line 79
            if to:  # line 80
                to.write(buffer)  # line 80
            if len(buffer) < bufSize:  # line 81
                break  # line 81
        if to:  # line 82
            to.close()  # line 82
    return _coconut_tail_call(hash.hexdigest)  # line 83

def firstOfMap(map: 'Dict[str, Any]', params: '_coconut.typing.Sequence[str]', default: 'Any'=None) -> 'Any':  # line 85
    ''' Utility. '''  # line 86
    for k, v in map.items():  # line 87
        if k in params:  # line 88
            return v  # line 88
    return default  # line 89

def loadConfig() -> 'Union[configr.Configr, Accessor]':  # Simplifies loading config from file system or returning the defaults  # line 91
    config = None  # type: Union[configr.Configr, Accessor]  # line 92
    if not configr:  # this only applies for the case that configr is not available, thus no settings will be persisted anyway  # line 93
        return defaults  # this only applies for the case that configr is not available, thus no settings will be persisted anyway  # line 93
    config = configr.Configr("sos", defaults=defaults)  # defaults are used if key is not configured, but won't be saved  # line 94
    f, g = config.loadSettings()  # line 95
    if f is None:  # line 96
        debug("Encountered a problem while loading the user configuration: %r" % g)  # line 96
    return config  # line 97

@_coconut_tco  # line 99
def strftime(timestamp: '_coconut.typing.Optional[int]'=None) -> 'str':  # line 99
    return _coconut_tail_call(time.strftime, "%Y-%m-%d %H:%M:%S", time.localtime(timestamp / 1000. if timestamp is not None else None))  # line 99

def isglob(f: 'str') -> 'bool':  # line 101
    return '*' in f or '?' in f  # line 101

def diffPathSets(last: 'Dict[str, PathInfo]', diff: 'Dict[str, PathInfo]') -> 'ChangeSet':  # line 103
    ''' Computes a changeset between in-memory and on-disk file lists.
      Additions contains PathInfo for entries in diff
      Deletions contains PathInfo for entries not anymore in diff
      Modifications contains PathInfo for entries changed from last to diff (new state)
  '''  # line 108
    changes = ChangeSet({}, {}, {})  # type: ChangeSet  # line 109
    for path, pinfo in last.items():  # line 110
        if path not in diff:  # now change  changes.deletions[path] = pinfo; continue  # line 111
            continue  # now change  changes.deletions[path] = pinfo; continue  # line 111
        vs = diff[path]  # reference to potentially changed path set  # line 112
        if vs.size is None:  # marked for deletion  # line 113
            changes.deletions[path] = pinfo  # marked for deletion  # line 113
            continue  # marked for deletion  # line 113
        if pinfo.size == None:  # re-added  # line 114
            changes.additions[path] = pinfo  # re-added  # line 114
            continue  # re-added  # line 114
        if pinfo.size != vs.size or pinfo.mtime != vs.mtime or pinfo.hash != vs.hash:  # not need to make hash comparison optional here  # line 115
            changes.modifications[path] = vs  # not need to make hash comparison optional here  # line 115
    for path, pinfo in diff.items():  # added loop  # line 116
        if path not in last:  # line 117
            changes.additions[path] = pinfo  # line 117
    assert not any([path in changes.deletions for path in changes.additions])  # invariant checks  # line 118
    assert not any([path in changes.additions for path in changes.deletions])  # line 119
    return changes  # line 120

try:  # line 122
    DataType = TypeVar("DataType", MergeBlock, BranchInfo)  # line 122
except:  # Python 2  # line 123
    pass  # Python 2  # line 123
@_coconut_tco  # line 124
def dataCopy(_tipe: 'Type[DataType]', _old: 'DataType', *_args, **_kwargs) -> 'DataType':  # line 124
    r = _old._asdict()  # line 124
    r.update(**_kwargs)  # line 124
    return _coconut_tail_call(makedata, _tipe, *(list(_args) + [r[field] for field in _old._fields]))  # line 124

@_coconut_tco  # line 126
def getIntraLineMarkers(line: 'str') -> 'Range':  # line 126
    ''' Return (type, [affected indices]) of "? "-line diff markers ("? " suffix must be removed). '''  # line 127
    if "^" in line:  # line 128
        return _coconut_tail_call(Range, MergeBlockType.MODIFY, [i for i, c in enumerate(line) if c == "^"])  # line 128
    if "+" in line:  # line 129
        return _coconut_tail_call(Range, MergeBlockType.INSERT, [i for i, c in enumerate(line) if c == "+"])  # line 129
    if "-" in line:  # line 130
        return _coconut_tail_call(Range, MergeBlockType.REMOVE, [i for i, c in enumerate(line) if c == "-"])  # line 130
    return _coconut_tail_call(Range, MergeBlockType.KEEP, [])  # line 131

def detectAndLoad(filename: '_coconut.typing.Optional[str]'=None, content: '_coconut.typing.Optional[bytes]'=None) -> 'Tuple[str, bytes, _coconut.typing.Sequence[str]]':  # line 133
    encoding = None  # type: str  # line 133
    eol = None  # type: bytes  # line 133
    lines = []  # type: _coconut.typing.Sequence[str]  # line 134
    if filename is not None:  # line 135
        with open(filename, "rb") as fd:  # line 136
            content = fd.read()  # line 136
    encoding = (lambda _coconut_none_coalesce_item: sys.getdefaultencoding() if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(detect(content))  # line 137
    eol = eoldet(content)  # line 138
    if filename is not None:  # line 139
        with codecs.open(filename, encoding=encoding) as fd:  # line 140
            lines = safeSplit(fd.read(), (b"\n" if eol is None else eol).decode(encoding))  # line 140
    elif content is not None:  # line 141
        lines = safeSplit(content.decode(encoding), (b"\n" if eol is None else eol).decode(encoding))  # line 142
    else:  # line 143
        return (sys.getdefaultencoding(), b"\n", [])  # line 143
    return (encoding, eol, lines)  # line 144

def openIt(file: 'str', mode: 'str', compress: 'bool') -> 'IO':  # line 146
    ''' Open abstraction for both compressed and plain files. '''  # line 147
    return bz2.BZ2File(file, mode) if compress else open(file, mode + "b")  # line 148

def eoldet(file: 'bytes') -> '_coconut.typing.Optional[bytes]':  # line 150
    ''' Determine EOL style from a binary string. '''  # line 151
    lf = file.count(b"\n")  # type: int  # line 152
    cr = file.count(b"\r")  # type: int  # line 153
    crlf = file.count(b"\r\n")  # type: int  # line 154
    if crlf > 0:  # DOS/Windows/Symbian etc.  # line 155
        if lf != crlf or cr != crlf:  # line 156
            warn("Inconsistent CR/NL count. Mixed EOL style detected, may cause problems during merge")  # line 157
        return b"\r\n"  # line 158
    if lf != 0 and cr != 0:  # line 159
        warn("Inconsistent CR/NL count. Mixed EOL style detected, may cause problems during merge")  # line 160
    if lf > cr:  # Linux/Unix  # line 161
        return b"\n"  # Linux/Unix  # line 161
    if cr > lf:  # older 8-bit machines  # line 162
        return b"\r"  # older 8-bit machines  # line 162
    return None  # no new line contained, cannot determine  # line 163

def usage() -> 'None':  # line 165
    ''' Print helpful usage information. '''  # line 166
    print(APPNAME + """
Usage: sos <command> [<argument>] [<option1>, ...]        For command "offline" and when in offline mode
       sos <underlying vcs command and arguments>         Unless working in offline mode

  Available commands:
    offline [<name>] [--track/--picky]                    Start working offline, creating a default branch
    online                                                Finish working offline

    branch  [<name>] [--last] [--stay]                    Create a new branch from file tree and switch to it
    switch  [<branch>][/<revision>] [--meta]              Continue work on another branch
    update  [<branch>][/<revision>]                       Integrate work from another branch TODO add many merge and conflict resolution options
    delete  [<branch>]                                    Remove branch entirely

    commit  [<message>]                                   Create a new revision from current state file tree
    changes [<branch>][/<revision>]                       List changed paths vs. last or specified revision
    diff    [<branch>][/<revision>]                       List changes vs. last or specified revision
    add     [<filename or glob pattern>]
    rm      [<filename or glob pattern>]

    ls                                                    List file tree and mark changes and tracking status
    status                                                List branches and display repository status
    log                                                   List commits of current branch
    config  [set/unset/show/add/rm] [<param>] [<value>]   Configure user-global defaults.
                                                          Flags (1/0, on/off, true/false, yes/no):
                                                            strict, track, picky, compress
                                                          Lists (semicolon-separated):
                                                            texttype, bintype, ignores, ignoreDirs, ignoresWhitelist, ignoreDirsWhitelist
                                                          Supported texts:
                                                            defaultbranch (dynamic default per discovered VCS)
    help                                                  Show this usage information

  Arguments:
    <name>                      Optional branch name
    <message>                   Optional commit message
    <branch/revision>           Revision string. Branch is optional and may be a label or index
                                Revision is an optional integer and may be negative to reference from the latest commits
    <filename or glob pattern>  Path or glob pattern to track or untrack

  Options:
    --force                     Executes potentially harmful operations
                                  for offline: ignore being already offline, start from scratch (same as online --force; offline)
                                  for online: ignore uncommitted branches
                                  for commit, switch, update, add: ignore uncommitted changes before executing command
    --strict                    Perform full content comparison, don't rely only on file size and timestamp
                                  for offline: persist strict mode
                                  for changes, diff, commit, switch, update, delete: perform operation in strict mode
    --meta                      When switching, only switch file tracking patterns for current branch, don't update any files
    --last                      When branching, use last revision, not current file tree, but keep file tree unchanged
    --stay                      When branching, don't switch to new branch, continue on current one
    --track                     When going offline, setup SVN-style mode: users add/remove tracking patterns per branch
    --picky                     When going offline, setup Git-style mode: users pick files for each operation
    --sos                       When executing SOS not being offline, pass arguments to SOS instead (e.g. sos --sos config set key value.)
    --log                       Enable internals logger
    --verbose                   Enable debugging output""")  # line 220

@_coconut_tco  # line 222
def merge(file: '_coconut.typing.Optional[bytes]'=None, into: '_coconut.typing.Optional[bytes]'=None, filename: '_coconut.typing.Optional[str]'=None, intoname: '_coconut.typing.Optional[str]'=None, mergeOperation=MergeOperation.BOTH, conflictResolution=ConflictResolution.ASK) -> 'bytes':  # line 222
    ''' Merges binary text contents 'file' into file 'into', returning merged result. '''  # line 223
    encoding = None  # type: str  # line 224
    othr = None  # type: _coconut.typing.Sequence[str]  # line 224
    othreol = None  # type: _coconut.typing.Optional[bytes]  # line 224
    curr = None  # type: _coconut.typing.Sequence[str]  # line 224
    curreol = None  # type: _coconut.typing.Optional[bytes]  # line 224
    differ = difflib.Differ()  # line 225
    try:  # load files line-wise and normalize line endings (keep the one of the current file) TODO document  # line 226
        encoding, othreol, othr = detectAndLoad(filename=filename, content=file)  # line 227
        encoding, curreol, curr = detectAndLoad(filename=intoname, content=into)  # line 228
    except Exception as E:  # line 229
        Exit("Cannot merge '%s' into '%s': %r" % (filename, intoname, E))  # line 229
    if None not in [othreol, curreol] and othreol != curreol:  # line 230
        warn("Differing EOL-styles detected during merge. Using current file's style for merge output")  # line 230
    output = list(differ.compare(othr, curr))  # type: List[str]  # from generator expression  # line 231
    debug("Diff output: " + "".join([o.replace("\n", "\\n") for o in output]))  # line 232
    blocks = []  # type: List[MergeBlock]  # merged result in blocks  # line 233
    tmp = []  # type: List[str]  # block lines  # line 234
    last = " "  # line 235
    for no, line in enumerate(output + ["X"]):  # EOF marker  # line 236
        if line[0] == last:  # continue filling consecutive block  # line 237
            tmp.append(line[2:])  # continue filling consecutive block  # line 237
            continue  # continue filling consecutive block  # line 237
        if line == "X":  # EOF marker - perform action for remaining block  # line 238
            if len(tmp) == 0:  # nothing left to do  # line 239
                break  # nothing left to do  # line 239
        if last == " ":  # block is same in both files  # line 240
            blocks.append(MergeBlock(MergeBlockType.KEEP, [line for line in tmp], line=no - len(tmp)))  # line 241
        elif last == "-":  # may be a deletion or replacement, store for later  # line 242
            blocks.append(MergeBlock(MergeBlockType.REMOVE, [line for line in tmp], line=no - len(tmp)))  # line 243
        elif last == "+":  # may be insertion or replacement  # line 244
            blocks.append(MergeBlock(MergeBlockType.INSERT, [line for line in tmp], line=no - len(tmp)))  # line 245
            if len(blocks) >= 2 and len(blocks[-1].lines) == len(blocks[-2].lines):  # replaces previously removed section entirely if any  # line 246
                if len(blocks[-1].lines) >= 2 or (blocks[-1].changes is None and blocks[-2].changes is None):  # full block or no intra-line comment  # line 247
                    blocks[-2] = MergeBlock(MergeBlockType.REPLACE, blocks[-1].lines, line=no - len(tmp), replaces=blocks[-2])  # remember replaced stuff  # line 248
                else:  # may have intra-line modifications  # line 249
                    blocks[-2] = MergeBlock(MergeBlockType.MODIFY, blocks[-1].lines, line=no - len(tmp), replaces=blocks[-2], changes=blocks[-1].changes)  # line 250
                blocks.pop()  # remove TOS  # line 251
        elif last == "?":  # intra-line change comment  # line 252
            ilm = getIntraLineMarkers(tmp[0])  # tipe is one of MergeBlockType 1, 2, 4. # "? " line includes a trailing \n for some reason  # line 253
            blocks[-1] = dataCopy(MergeBlock, blocks[-1], tipe=MergeBlockType.MODIFY, changes=ilm)  # update to MODIFY, otherwise may be REPLACE instead  # line 254
        last = line[0]  # line 255
        tmp[:] = [line[2:]]  # line 256
    debug("Diff blocks: " + repr(blocks))  # line 257
    output = []  # line 258
    for block in blocks:  # line 259
        if block.tipe == MergeBlockType.KEEP:  # line 260
            output.extend(block.lines)  # line 261
        elif block.tipe == MergeBlockType.INSERT and not (mergeOperation & MergeOperation.REMOVE):  # line 262
            output.extend(block.lines)  # line 263
        elif block.tipe == MergeBlockType.REPLACE:  # complete block replacement  # line 264
            if mergeOperation & MergeOperation.INSERT:  # replaced stuff TODO allow insertion BEFORE and alternatively AFTER?  # line 265
                output.extend(block.replaces.lines)  # replaced stuff TODO allow insertion BEFORE and alternatively AFTER?  # line 265
            if not (mergeOperation & MergeBlockType.REMOVE):  # if remove, don't add replaced lines, otherwise do  # line 266
                output.extend(block.lines)  # if remove, don't add replaced lines, otherwise do  # line 266
        elif block.tipe == MergeBlockType.REMOVE and mergeOperation & MergeOperation.INSERT:  # line 267
            output.extend(block.lines)  # line 268
        elif block.tipe == MergeBlockType.MODIFY:  # line 269
            if block.changes is not None and block.changes.tipe == MergeBlockType.INSERT:  # cannot be REMOVE, because it's always "-" then "+"  # line 270
                output.extend(block.lines if mergeOperation & MergeOperation.INSERT else block.replaces.lines)  # TODO logic?  # line 271
            elif block.replaces.changes is not None and block.replaces.changes.tipe == MergeBlockType.REMOVE:  # line 272
                output.extend(block.lines if mergeOperation & MergeOperation.REMOVE else block.replaces.lines)  # line 273
            elif block.changes is not None and block.changes.tipe == MergeBlockType.MODIFY:  # always both sides modified, but may differ in markers  # line 274
                if conflictResolution == ConflictResolution.THEIRS:  # line 275
                    output.extend(block.replaces.lines)  # line 276
                elif conflictResolution == ConflictResolution.MINE:  # line 277
                    output.extend(block.lines)  # line 278
                elif conflictResolution == ConflictResolution.ASK:  # line 279
                    print("THR " + "\nTHR ".join(block.replaces.lines))  # line 280
                    print("MIN " + "\nMIN ".join(block.lines))  # line 281
                    reso = {"i": ConflictResolution.MINE, "t": ConflictResolution.THEIRS, "m": ConflictResolution.NEXT, "u": None}.get(user_input(" Resolve: *M[I]ne, [T]heirs, [M]erge, [U]ser defined: ").strip().lower(), ConflictResolution.MINE)  # type: _coconut.typing.Optional[int]  # line 282
                    debug("User selected %d" % reso)  # line 283
                    _coconut_match_check = False  # line 284
                    _coconut_match_to = reso  # line 284
                    if _coconut_match_to is None:  # line 284
                        _coconut_match_check = True  # line 284
                    if _coconut_match_check:  # line 284
                        warn("Manual input not implemented yet")  # TODO allow multi-line input (CTRL+D?)  # line 285
                    _coconut_match_check = False  # line 286
                    _coconut_match_to = reso  # line 286
                    if _coconut_match_to == ConflictResolution.MINE:  # line 286
                        _coconut_match_check = True  # line 286
                    if _coconut_match_check:  # line 286
                        debug("Using mine")  # line 287
                        output.extend(block.lines)  # line 288
                    _coconut_match_check = False  # line 289
                    _coconut_match_to = reso  # line 289
                    if _coconut_match_to == ConflictResolution.THEIRS:  # line 289
                        _coconut_match_check = True  # line 289
                    if _coconut_match_check:  # line 289
                        debug("Using theirs")  # line 290
                        output.extend(block.replaces.lines)  # line 291
                    _coconut_match_check = False  # line 292
                    _coconut_match_to = reso  # line 292
                    if _coconut_match_to == ConflictResolution.NEXT:  # line 292
                        _coconut_match_check = True  # line 292
                    if _coconut_match_check:  # line 292
                        warn("Intra-line merge not implemented yet, skipping line(s)")  # line 293
                        output.extend(block.replaces.lines)  # line 294
            else:  # e.g. contains a deletion, but user was asking for insert only??  # line 295
                warn("Investigate this case")  # line 296
                output.extend(block.lines)  # default or not .replaces?  # line 297
    debug("Merge output: " + "; ".join(output))  # line 298
    nl = b"\n" if othreol is None else othreol if curreol is None else curreol  # type: bytes  # line 299
    return _coconut_tail_call(nl.join, [line.encode(encoding) for line in output])  # line 300
# TODO handle check for more/less lines in found -/+ blocks to find common section and splitting prefix/suffix out


class Counter:  # line 304
    def __init__(_, initial: 'Number'=0) -> 'None':  # line 305
        _.value = initial  # type: Number  # line 305
    def inc(_, by=1) -> 'Number':  # line 306
        _.value += by  # line 306
        return _.value  # line 306
    def inc_old(_, by=1) -> 'Number':  # line 307
        old = _.value  # line 307
        _.value += by  # line 307
        return old  # line 307

class Logger:  # line 309
    ''' Logger that supports many items. '''  # line 310
    def __init__(_, log):  # line 311
        _._log = log  # line 311
    def debug(_, *s):  # line 312
        _._log.debug(sjoin(*s))  # line 312
    def info(_, *s):  # line 313
        _._log.info(sjoin(*s))  # line 313
    def warn(_, *s):  # line 314
        _._log.warning(sjoin(*s))  # line 314
    def error(_, *s):  # line 315
        _._log.error(sjoin(*s))  # line 315


# Main data class
class Metadata:  # line 319
    ''' This class doesn't represent the entire repository state in memory,
      but serves as a container for different repo operations,
      using only parts of its attributes at any point in time. Use with care.
  '''  # line 323

    def __init__(_, path: 'str') -> 'None':  # line 325
        ''' Create empty container object for various repository operations. '''  # line 326
        _.c = loadConfig()  # line 327
        _.root = path  # type: str  # line 328
        _.branches = {}  # type: Dict[int, BranchInfo]  # branch number zero represents the initial state at branching  # line 329
        _.commits = {}  # type: Dict[int, CommitInfo]  # consecutive numbers per branch, starting at 0  # line 330
        _.paths = {}  # type: Dict[str, PathInfo]  # utf-8 encoded relative, normalized file system paths  # line 331
        _.track = _.c.track  # type: bool  # track files in the repository (tracked patterns are stored for each branch separately)  # line 332
        _.picky = _.c.picky  # type: bool  # pick files on each operation  # line 333
        _.strict = _.c.strict  # type: bool  # be always strict (regarding file contents comparsion)  # line 334
        _.compress = _.c.compress  # type: bool  # these flags are stored per branch, therefor not part of the (default) configuration  # line 335
        _.branch = None  # type: _coconut.typing.Optional[int]  # current branch number  # line 336
        _.commit = None  # type: _coconut.typing.Optional[int]  # current revision number  # line 337

    def isTextType(_, filename: 'str') -> 'bool':  # line 339
        return (((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(mimetypes.guess_type(filename)[0])).startswith("text/") or any([fnmatch.fnmatch(filename, pattern) for pattern in _.c.texttype])) and not any([fnmatch.fnmatch(filename, pattern) for pattern in _.c.bintype])  # line 339

    def listChanges(_, changes: 'ChangeSet', diffmode: 'bool'=False, textglobs: '_coconut.typing.Sequence[str]'=[]) -> 'None':  # line 341
        ''' In diffmode, don't list modified files, because the diff is displayed elsewhere. '''  # line 342
        if len(changes.additions) > 0:  # line 343
            print("ADD " + "\nADD ".join((a for a in sorted(changes.additions.keys()))))  # line 343
        if len(changes.deletions) > 0:  # line 344
            print("DEL " + "\nDEL ".join((d for d in sorted(changes.deletions.keys()))))  # line 344
        if len(changes.modifications) > 0:  # only list binary files  # line 345
            print("MOD " + "\nMOD ".join(sorted((k for k in changes.modifications.keys() if not _.isTextType(k) or not diffmode))))  # only list binary files  # line 345

    def loadBranches(_) -> 'None':  # line 347
        ''' Load list of branches and current branch info from metadata file. '''  # line 348
        try:  # fails if not yet created (on initial branch/commit)  # line 349
            branches = None  # type: List[Tuple]  # line 350
            with codecs.open(os.path.join(_.root, metaFolder, metaFile), "r", encoding=UTF8) as fd:  # line 351
                flags, branches = json.load(fd)  # line 352
            _.branch = flags["branch"]  # line 353
            _.track = flags["track"]  # line 354
            _.picky = flags["picky"]  # line 355
            _.strict = flags["strict"]  # line 356
            _.branches = {i.number: i for i in (BranchInfo(*item) for item in branches)}  # re-create type info  # line 357
        except Exception as E:  # if not found, create metadata folder  # line 358
            try:  # line 359
                os.makedirs(os.path.join(_.root, metaFolder))  # line 359
                _.branches = {}  # line 359
            except Exception as F:  # line 360
                Exit("Error: Couldn't read branches metadata, but branches folder seems to already exist. %r %r" % (E, F))  # line 360

    def saveBranches(_) -> 'None':  # line 362
        ''' Save list of branches and current branch info to metadata file. '''  # line 363
        with codecs.open(os.path.join(_.root, metaFolder, metaFile), "w", encoding=UTF8) as fd:  # line 364
            json.dump(({"branch": _.branch, "track": _.track, "picky": _.picky, "strict": _.strict, "compress": _.compress}, list(_.branches.values())), fd, ensure_ascii=False)  # line 365

    def getBranchByName(_, name: 'Union[str, int]') -> '_coconut.typing.Optional[int]':  # line 367
        ''' Convenience accessor for named branches. '''  # line 368
        if isinstance(name, int):  # if type(name) is int: return name  # line 369
            return name  # if type(name) is int: return name  # line 369
        try:  # attempt to parse integer string  # line 370
            return int(name)  # attempt to parse integer string  # line 370
        except ValueError:  # line 371
            pass  # line 371
        found = [number for number, branch in _.branches.items() if name == branch.name]  # line 372
        return found[0] if found else None  # line 373

    def loadBranch(_, branch: 'int') -> 'None':  # line 375
        ''' Load all commit information from a branch meta data file. '''  # line 376
        with codecs.open(os.path.join(_.root, metaFolder, "b%d" % branch, metaFile), "r", encoding=UTF8) as fd:  # line 377
            commits = json.load(fd)  # type: List[List[Any]]  # list of CommitInfo that needs to be unmarshalled into value types  # line 378
        _.commits = {i.number: i for i in (CommitInfo(*item) for item in commits)}  # re-create type info  # line 379
        _.branch = branch  # line 380

    def saveBranch(_, branch: 'int') -> 'None':  # line 382
        ''' Save all commit information to a branch meta data file. '''  # line 383
        with codecs.open(os.path.join(_.root, metaFolder, "b%d" % branch, metaFile), "w", encoding=UTF8) as fd:  # line 384
            json.dump(list(_.commits.values()), fd, ensure_ascii=False)  # line 385

    def duplicateBranch(_, branch: 'int', name: '_coconut.typing.Optional[str]') -> 'None':  # line 387
        ''' Create branch from an existing branch/revision. WARN: Caller must have loaded branches information.
        branch: target branch (should not exist yet)
        name: optional name of new branch
        _.branch: current branch
    '''  # line 392
        debug("Duplicating branch '%s' to '%d'..." % ((lambda _coconut_none_coalesce_item: "b%d" % _.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(_.branches[_.branch].name), branch))  # line 393
        tracked = [t for t in _.branches[_.branch].tracked]  # copy  # line 394
        os.makedirs(os.path.join(_.root, metaFolder, "b%d" % branch, "r0"))  # line 395
        _.loadBranch(_.branch)  # line 396
        revision = max(_.commits)  # type: int  # line 397
        _.computeSequentialPathSet(_.branch, revision)  # full set of files in revision to _.paths  # line 398
        for path, pinfo in _.paths.items():  # line 399
            _.copyVersionedFile(_.branch, revision, branch, 0, pinfo)  # line 400
        _.commits = {0: CommitInfo(0, int(time.time() * 1000), "Branched from '%s'" % ((lambda _coconut_none_coalesce_item: "b%d" % _.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(_.branches[_.branch].name)))}  # store initial commit  # line 401
        _.saveBranch(branch)  # save branch meta data to branch folder  # line 402
        _.saveCommit(branch, 0)  # save commit meta data to revision folder  # line 403
        _.branches[branch] = BranchInfo(branch, _.commits[0].ctime, name, _.branches[_.branch].insync, tracked)  # save branch info, before storing repo state at caller  # line 404

    def createBranch(_, branch: 'int', name: '_coconut.typing.Optional[str]'=None, initialMessage: '_coconut.typing.Optional[str]'=None):  # line 406
        ''' Create a new branch from current file tree. This clears all known commits and modifies the file system.
        branch: target branch (should not exist yet)
        name: optional name of new branch
        _.branch: current branch, must exist already
    '''  # line 411
        simpleMode = not (_.track or _.picky)  # line 412
        tracked = [t for t in _.branches[_.branch].tracked] if _.track and len(_.branches) > 0 else []  # in case of initial branch creation  # line 413
        debug((lambda _coconut_none_coalesce_item: "b%d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)("Creating branch '%s'..." % name))  # line 414
        _.paths = {}  # type: Dict[str, PathInfo]  # line 415
        if simpleMode:  # line 416
            changes = _.findChanges(branch, 0)  # type: ChangeSet  # creates revision folder and versioned files  # line 417
            _.listChanges(changes)  # line 418
            _.paths.update(changes.additions.items())  # line 419
        else:  # tracking or picky mode  # line 420
            os.makedirs(os.path.join(_.root, metaFolder, "b%d" % branch, "r0"))  # line 421
            if _.branch is not None:  # not immediately after "offline" - copy files from current branch  # line 422
                _.loadBranch(_.branch)  # line 423
                revision = max(_.commits)  # type: int  # TODO what if last switch was to an earlier revision? no persisting of last checkout  # line 424
                _.computeSequentialPathSet(_.branch, revision)  # full set of files in revision to _.paths  # line 425
                for path, pinfo in _.paths.items():  # line 426
                    _.copyVersionedFile(_.branch, revision, branch, 0, pinfo)  # line 427
        ts = int(time.time() * 1000)  # line 428
        _.commits = {0: CommitInfo(0, ts, "Branched on %s" % strftime(ts) if initialMessage is None else initialMessage)}  # store initial commit for new branch  # line 429
        _.saveBranch(branch)  # save branch meta data (revisions) to branch folder  # line 430
        _.saveCommit(branch, 0)  # save commit meta data to revision folder  # line 431
        _.branches[branch] = BranchInfo(branch, _.commits[0].ctime, name, _.branches[_.branch].insync if len(_.branches) > 0 else False, tracked)  # save branch info, in case it is needed  # line 432

    def removeBranch(_, branch: 'int') -> 'BranchInfo':  # line 434
        ''' Entirely remove a branch and all its revisions from the file system. '''  # line 435
        shutil.rmtree(os.path.join(_.root, metaFolder, "b%d" % branch))  # line 436
        binfo = _.branches[branch]  # line 437
        del _.branches[branch]  # line 438
        _.branch = max(_.branches)  # line 439
        _.saveBranches()  # line 440
        _.commits.clear()  # line 441
        return binfo  # line 442

    def loadCommit(_, branch: 'int', revision: 'int') -> 'None':  # line 444
        ''' Load all file information from a commit meta data. '''  # line 445
        with codecs.open(os.path.join(_.root, metaFolder, "b%d" % branch, "r%d" % revision, metaFile), "r", encoding=UTF8) as fd:  # line 446
            _.paths = json.load(fd)  # line 447
        _.paths = {path: PathInfo(*item) for path, item in _.paths.items()}  # re-create type info  # line 448
        _.branch = branch  # line 449

    def saveCommit(_, branch: 'int', revision: 'int'):  # line 451
        ''' Save all file information to a commit meta data file. '''  # line 452
        target = os.path.join(_.root, metaFolder, "b%d" % branch, "r%d" % revision)  # line 453
        try:  # line 454
            os.makedirs(target)  # line 454
        except:  # line 455
            pass  # line 455
        with codecs.open(os.path.join(target, metaFile), "w", encoding=UTF8) as fd:  # line 456
            json.dump(_.paths, fd, ensure_ascii=False)  # line 457

    def findChanges(_, branch: '_coconut.typing.Optional[int]'=None, revision: '_coconut.typing.Optional[int]'=None, checkContent: 'bool'=False, inverse: 'bool'=False, considerOnly: '_coconut.typing.Optional[FrozenSet[str]]'=None) -> 'ChangeSet':  # line 459
        ''' Find changes on the file system vs. in-memory paths (which should reflect the latest commit state).
        Only if both branch and revision are *not* None, write modified/added files to the specified revision folder (thus creating a new revision)
        The function returns the state of file tree *differences*, unless "inverse" is True -> then return original data
        checkContent: also computes file content hashes
        inverse: retain original state (size, mtime, hash) instead of updated one
        considerOnly: set of tracking patterns. For update operation, union of other and current branch
    '''  # line 466
        write = branch is not None and revision is not None  # line 467
        if write:  # line 468
            os.makedirs(os.path.join(_.root, metaFolder, "b%d" % branch, "r%d" % revision))  # line 468
        changes = ChangeSet({}, {}, {})  # type: ChangeSet  # line 469
        for path, dirnames, filenames in os.walk(_.root):  # line 470
            dirnames[:] = [f for f in dirnames if len([n for n in _.c.ignoreDirs if fnmatch.fnmatch(f, n)]) == 0 or len([p for p in _.c.ignoreDirsWhitelist if fnmatch.fnmatch(f, p)]) > 0]  # line 471
            filenames[:] = [f for f in filenames if len([n for n in _.c.ignores if fnmatch.fnmatch(f, n)]) == 0 or len([p for p in _.c.ignoresWhitelist if fnmatch.fnmatch(f, p)]) > 0]  # line 472
            dirnames.sort()  # line 473
            filenames.sort()  # line 473
            relpath = os.path.relpath(path, _.root).replace(os.sep, "/")  # line 474
            for file in (filenames if considerOnly is None else list(reduce(lambda last, pattern: last | set(fnmatch.filter(filenames, os.path.basename(pattern))), (p for p in considerOnly if os.path.dirname(p) == relpath), _coconut.set()))):  # if m.track or m.picky: only files that match any path-relevant tracking patterns  # line 475
                filename = relpath + "/" + file  # line 476
                filepath = os.path.join(path, file)  # line 477
                stat = os.stat(filepath)  # line 478
                size, mtime = stat.st_size, int(stat.st_mtime * 1000)  # line 479
                if filename not in _.paths:  # detected file not present (or untracked) in other branch  # line 480
                    namehash = hashStr(filename)  # line 481
                    changes.additions[filename] = PathInfo(namehash, size, mtime, hashFile(filepath, _.compress, saveTo=os.path.join(_.root, metaFolder, "b%d" % branch, "r%d" % revision, namehash) if write else None) if size > 0 else None)  # line 482
                    continue  # line 483
                last = _.paths[filename]  # filename is known  # line 484
                if last.size is None:  # was removed before but is now added back - does not apply for tracking mode (which never marks files for removal in the history)  # line 485
                    changes.additions[filename] = PathInfo(last.namehash, size, mtime, hashFile(filepath, _.compress, saveTo=os.path.join(_.root, metaFolder, "b%d" % branch, "r%d" % revision, last.namehash) if write else None) if size > 0 else None)  # line 486
                    continue  # line 486
                elif size != last.size or mtime != last.mtime or (checkContent and hashFile(filepath, _.compress) == last.hash):  # detected a modification  # line 487
                    changes.modifications[filename] = PathInfo(last.namehash, last.size if inverse else size, last.mtime if inverse else mtime, last.hash if inverse else hashFile(filepath, _.compress, saveTo=os.path.join(_.root, metaFolder, "b%d" % branch, "r%d" % revision, last.namehash) if write else None) if (last.size if inverse else size) > 0 else None)  # line 488
# Detect deletions. Files no longer being tracked should not be found here
            for folderPath in (p for p, pinfo in _.paths.items() if p[:p.rindex("/")] == relpath and pinfo.size is not None):  # only versioned (and tracked) files that match currently visited folder. TODO don't check for removal just added entries  # line 490
                if folderPath[len(relpath) + 1:] not in filenames:  # filename no longer in file tree TODO use basename and dirname instead of slicing?  # line 491
                    changes.deletions[folderPath] = _.paths[folderPath]  # filename no longer in file tree TODO use basename and dirname instead of slicing?  # line 491
        return changes  # line 492

    def integrateChangeset(_, changes: 'ChangeSet', clear=False) -> 'None':  # line 494
        ''' In-memory update from a changeset, marking deleted files with size=None. Use clear = True to start on an empty path set. '''  # line 495
        if clear:  # line 496
            _.paths.clear()  # line 496
        else:  # line 497
            rm = [p for p, info in _.paths.items() if info.size is None]  # remove files deleted in earlier change sets (revisions)  # line 498
            for old in rm:  # remove previously removed entries completely  # line 499
                del _.paths[old]  # remove previously removed entries completely  # line 499
        for d, info in changes.deletions.items():  # mark now removed entries as deleted  # line 500
            _.paths[d] = PathInfo(info.namehash, None, info.mtime, None)  # mark now removed entries as deleted  # line 500
        _.paths.update(changes.additions)  # line 501
        _.paths.update(changes.modifications)  # line 502

    def computeSequentialPathSet(_, branch: 'int', revision: 'int') -> 'None':  # line 504
        ''' In-memory computation of current list of valid PathInfo entries for specified branch and until specified revision (inclusively) by traversing revision on the file system. '''  # line 505
        _.loadCommit(branch, 0)  # load initial paths  # line 506
        n = Metadata(_.root)  # type: Metadata  # next changes  # line 507
        for revision in range(1, revision + 1):  # line 508
            n.loadCommit(branch, revision)  # line 509
            changes = diffPathSets(_.paths, n.paths)  # type: ChangeSet  # line 510
            _.integrateChangeset(changes)  # line 511

    def parseRevisionString(_, argument: 'str') -> 'Tuple[_coconut.typing.Optional[int], _coconut.typing.Optional[int]]':  # line 513
        ''' Commit identifiers can be str or int for branch, and int for revision.
        Revision identifiers can be negative, with -1 being last commit.
    '''  # line 516
        if argument is None:  # no branch/revision specified  # line 517
            return (_.branch, -1)  # no branch/revision specified  # line 517
        argument = argument.strip()  # line 518
        if argument.startswith("/"):  # current branch  # line 519
            return (_.branch, int(argument[1:]))  # current branch  # line 519
        if argument.endswith("/"):  # line 520
            try:  # line 521
                return (_.getBranchByName(argument[:-1]), -1)  # line 521
            except ValueError:  # line 522
                Exit("Unknown branch label")  # line 522
        if "/" in argument:  # line 523
            b, r = argument.split("/")[:2]  # line 524
            try:  # line 525
                return (_.getBranchByName(b), int(r))  # line 525
            except ValueError:  # line 526
                Exit("Unknown branch label or wrong number format")  # line 526
        branch = _.getBranchByName(argument)  # type: int  # returns number if given (revision) integer  # line 527
        if branch not in _.branches:  # line 528
            branch = None  # line 528
        try:  # either branch name/number or reverse/absolute revision number  # line 529
            return (_.branch if branch is None else branch, int(argument) if branch is None else -1)  # either branch name/number or reverse/absolute revision number  # line 529
        except:  # line 530
            Exit("Unknown branch label or wrong number format")  # line 530
        return (None, None)  # should never be reached TODO raise exception instead?  # line 531

    def copyVersionedFile(_, branch: 'int', revision: 'int', tobranch: 'int', torevision: 'int', pinfo: 'PathInfo') -> 'None':  # line 533
        ''' Copy versioned file to other branch/revision. '''  # line 534
        target = os.path.join(_.root, metaFolder, "b%d" % tobranch, "r%d" % torevision, pinfo.namehash)  # type: str  # line 535
        while True:  # line 536
            source = os.path.join(_.root, metaFolder, "b%d" % branch, "r%d" % revision, pinfo.namehash)  # type: str  # line 537
            if os.path.exists(source):  # line 538
                break  # line 538
            revision -= 1  # line 539
            if revision < 0:  # should never happen  # line 540
                Exit("Cannot copy file '%s' from 'b%d/r%d' to 'b%d/r%d" % (pinfo.namehash, branch, revision, tobranch, torevision))  # should never happen  # line 540
        shutil.copy2(source, target)  # line 541

    def readOrCopyVersionedFile(_, branch: 'int', revision: 'int', namehash: 'str', toFile: '_coconut.typing.Optional[str]'=None) -> '_coconut.typing.Optional[bytes]':  # line 543
        ''' Return file contents, or copy contents into file path provided. '''  # line 544
        source = os.path.join(_.root, metaFolder, "b%d" % branch, "r%d" % revision, namehash)  # type: str  # line 545
        try:  # line 546
            with openIt(source, "r", _.compress) as fd:  # line 547
                if toFile is None:  # read bytes into memory and return  # line 548
                    return fd.read()  # read bytes into memory and return  # line 548
                with open(toFile, "wb") as to:  # line 549
                    while True:  # line 550
                        buffer = fd.read(bufSize)  # line 551
                        to.write(buffer)  # line 552
                        if len(buffer) < bufSize:  # line 553
                            break  # line 553
                    return None  # line 554
        except Exception as E:  # line 555
            warn("Cannot read versioned file: %r (%d/%d/%s)" % (E, branch, revision, namehash))  # line 555
        return None  # line 556

    def restoreFile(_, relpath: '_coconut.typing.Optional[str]', branch: 'int', revision: 'int', pinfo: 'PathInfo') -> '_coconut.typing.Optional[bytes]':  # line 558
        ''' Recreate file for given revision, or return contents if path is None. '''  # line 559
        if relpath is None:  # just return contents as split decoded lines  # line 560
            return _.readOrCopyVersionedFile(branch, revision, pinfo.namehash) if pinfo.size > 0 else b''  # just return contents as split decoded lines  # line 560
        target = os.path.join(_.root, relpath.replace("/", os.sep))  # type: str  # line 561
        if pinfo.size == 0:  # line 562
            with open(target, "wb"):  # line 563
                pass  # line 563
            try:  # update access/modification timestamps on file system  # line 564
                os.utime(target, (-1, pinfo.mtime / 1000.))  # update access/modification timestamps on file system  # line 564
            except Exception as E:  # line 565
                error("Cannot update file's timestamp after restoration '%r'" % E)  # line 565
            return None  # line 566
        while True:  # find latest revision that contained the file physically  # line 567
            source = os.path.join(_.root, metaFolder, "b%d" % branch, "r%d" % revision, pinfo.namehash)  # type: str  # line 568
            if os.path.exists(source):  # line 569
                break  # line 569
            revision -= 1  # line 570
            if revision < 0:  # line 571
                Exit("Cannot restore file '%s' from specified branch '%d'" % (pinfo.namehash, branch))  # line 571
# Restore file by copying buffer-wise
        with openIt(source, "r", _.compress) as fd, open(target, "wb") as to:  # using Coconut's Enhanced Parenthetical Continuation  # line 573
            while True:  # line 574
                buffer = fd.read(bufSize)  # line 575
                to.write(buffer)  # line 576
                if len(buffer) < bufSize:  # line 577
                    break  # line 577
        try:  # update access/modification timestamps on file system  # line 578
            os.utime(target, (-1, pinfo.mtime / 1000.))  # update access/modification timestamps on file system  # line 578
        except Exception as E:  # line 579
            error("Cannot update file's timestamp after restoration '%r'" % E)  # line 579
        return None  # line 580

    def getTrackingPatterns(_, branch: '_coconut.typing.Optional[int]'=None) -> 'FrozenSet[str]':  # line 582
        ''' Returns list of tracking patterns for provided branch or current branch. '''  # line 583
        return _coconut.frozenset() if not _.track and not _.picky else frozenset(_.branches[_.branch if branch is None else branch].tracked)  # line 584


# Main client operations
def offline(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]) -> 'None':  # line 588
    ''' Initial command to start working offline. '''  # line 589
    if '--force' not in options and os.path.exists(metaFolder):  # line 590
        Exit("Repository folder is either already offline or older branches and commits were left over. Use 'sos online' or continue working offline")  # line 591
    m = Metadata(os.getcwd())  # type: Metadata  # line 592
    if '--picky' in options or m.c["picky"]:  # Git-like  # line 593
        m.picky = True  # Git-like  # line 593
    elif '--track' in options or m.c["track"]:  # Svn-like  # line 594
        m.track = True  # Svn-like  # line 594
    if '--strict' in options or m.c["strict"]:  # always hash contents  # line 595
        m.strict = True  # always hash contents  # line 595
    debug("Preparing offline repository...")  # line 596
    m.createBranch(0, str(m.c["defaultbranch"]) if argument is None else argument, initialMessage="Offline repository created on %s" % strftime())  # main branch's name may be None (e.g. for fossil)  # line 597
    m.branch = 0  # line 598
    m.saveBranches()  # no change immediately after going offline, going back online won't issue a warning  # line 599
    info("Offline repository prepared. Use 'sos online' to finish offline work")  # line 600

def online(options: '_coconut.typing.Sequence[str]'=[]) -> 'None':  # line 602
    ''' Finish working offline. '''  # line 603
    force = '--force' in options  # type: bool  # line 604
    if not force:  # line 605
        m = Metadata(os.getcwd())  # line 606
        m.loadBranches()  # line 607
        if any([not b.insync for b in m.branches.values()]) and not force:  # line 608
            Exit("There are still unsynchronized branches.\nUse 'log' to list them. Commit them to your VCS one by one with 'sos commit' and 'sos switch' before leaving offline mode. Use 'online --force' to erase all aggregated offline revisions.")  # line 608
    try:  # line 609
        shutil.rmtree(metaFolder)  # line 609
        info("Left offline modus. Continue work with your online VCS.")  # line 609
    except Exception as E:  # line 610
        Exit("Error removing offline repository: %r" % E)  # line 610

def branch(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]) -> 'None':  # line 612
    ''' Create a new branch (from file tree or last revision) and (by default) continue working on it. '''  # line 613
    last = '--last' in options  # type: bool  # use last revision for branching, not current file tree  # line 614
    stay = '--stay' in options  # type: bool  # continue on current branch after branching  # line 615
    force = '--force' in options  # type: bool  # branch even with local modifications  # line 616
    m = Metadata(os.getcwd())  # type: Metadata  # line 617
    m.loadBranches()  # line 618
    if argument and m.getBranchByName(argument) is not None:  # create a named branch  # line 619
        Exit("Branch '%s' already exists. Cannot proceed" % argument)  # create a named branch  # line 619
    branch = max(m.branches.keys()) + 1  # next branch's key  # line 620
    debug("Branching to %sbranch b%d%s%s..." % ("unnamed " if argument is None else "", branch, " '%s'" % argument if argument else "", " from last revision" if last else ""))  # line 621
    if last:  # line 622
        m.duplicateBranch(branch, argument)  # branch from branch's last revision  # line 623
    else:  # from file tree state  # line 624
        m.createBranch(branch, argument)  # branch from current file tree  # line 625
    if not stay:  # line 626
        m.branch = branch  # line 627
        m.saveBranches()  # line 628
    info("%s new %sbranch b%d%s" % ("Continue work after branching" if stay else "Switched to", "unnamed " if argument is None else "", branch, " '%s'" % argument if argument else ""))  # line 629

def changes(argument: 'str'=None, options: '_coconut.typing.Sequence[str]'=[]) -> 'ChangeSet':  # line 631
    ''' Show changes of file tree vs. (last or specified) revision on current or specified branch. '''  # line 632
    m = Metadata(os.getcwd())  # type: Metadata  # line 633
    m.loadBranches()  # knows current branch  # line 634
    strict = '--strict' in options or m.strict  # type: bool  # line 635
    branch, revision = m.parseRevisionString(argument)  # line 636
    if branch not in m.branches:  # line 637
        Exit("Unknown branch")  # line 637
    m.loadBranch(branch)  # knows commits  # line 638
    revision = revision if revision >= 0 else len(m.commits) + revision  # type: int  # negative indexing  # line 639
    if revision < 0 or revision > max(m.commits):  # line 640
        Exit("Unknown revision r%d" % revision)  # line 640
    debug("Checking file tree vs. commit '%s/r%d'..." % ((lambda _coconut_none_coalesce_item: "b%d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 641
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision  # line 642
    changes = m.findChanges(checkContent=strict, considerOnly=None if not m.track else m.getTrackingPatterns() | m.getTrackingPatterns(branch))  # type: ChangeSet  # line 643
    m.listChanges(changes)  # line 644
    return changes  # line 645

def diff(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]) -> 'None':  # line 647
    ''' Show text file differences of file tree vs. (last or specified) revision on current or specified branch. '''  # line 648
    m = Metadata(os.getcwd())  # type: Metadata  # line 649
    m.loadBranches()  # knows current branch  # line 650
    strict = '--strict' in options or m.strict  # type: bool  # line 651
    branch, revision = m.parseRevisionString(argument)  # line 652
    if branch not in m.branches:  # line 653
        Exit("Unknown branch")  # line 653
    m.loadBranch(branch)  # knows commits  # line 654
    revision = revision if revision >= 0 else len(m.commits) + revision  # type: int  # negative indexing  # line 655
    if revision < 0 or revision > max(m.commits):  # line 656
        Exit("Unknown revision r%d" % revision)  # line 656
    debug("Diffing file tree vs. commit '%s/r%d'..." % ((lambda _coconut_none_coalesce_item: "b%d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 657
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision  # line 658
    changes = m.findChanges(checkContent=strict, inverse=True, considerOnly=None if not m.track else m.getTrackingPatterns() | m.getTrackingPatterns(branch))  # type: ChangeSet  # line 659
    info("File changes:")  # line 660
    m.listChanges(changes, diffmode=True)  # only list modified binary files  # line 661

    info("Text file modifications:")  # TODO only text files, not binary  # line 663
    differ = difflib.Differ()  # line 664
    for path, pinfo in changes.modifications.items():  # only consider modified files TODO also show A/D here?  # line 665
        print("\nDIF " + path)  # line 666
        content = None  # type: _coconut.typing.Optional[bytes]  # line 667
        othr = None  # type: _coconut.typing.Sequence[str]  # line 667
        curr = None  # type: _coconut.typing.Sequence[str]  # line 667
        if pinfo.size == 0:  # line 668
            content = b""  # line 668
        else:  # line 669
            content = m.restoreFile(None, branch, revision, pinfo)  # line 669
            assert content is not None  # line 669
        abspath = os.path.join(m.root, path.replace("/", os.sep))  # line 670
        encoding, othreol, othr = detectAndLoad(content=content)  # line 671
        encoding, curreol, curr = detectAndLoad(filename=abspath)  # line 672
        currcount, othrcount = Counter(), Counter()  # TODO shows empty new line although none in file. also counting is messed up  # line 673
        last = ""  # line 674
        for no, line in enumerate(differ.compare(othr, curr)):  # line 675
            if line[0] == " ":  # no change in line  # line 676
                continue  # no change in line  # line 676
            print("%04d/%04d %s" % (no + othrcount.inc(-1 if line[0] == "+" or (line[0] == "?" and last == "+") else 0), no + currcount.inc(-1 if line[0] == "-" or (line[0] == "?" and last == "-") else 0), line))  # TODO counting this is definitely wrong and also lists \n as new diff lines. Could reuse block detection from merge instead  # line 677
            last = line[0]  # line 678

def commit(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]) -> 'None':  # line 680
    ''' Create new revision from file tree changes vs. last commit. '''  # line 681
    changes = None  # type: ChangeSet  # line 682
    m, branch, revision, changes, strict, force, trackingPatterns = stopOnChanges(None, options, commit=True)  # special flag creates new revision for detected changes, but abort if no changes  # line 683
    debug((lambda _coconut_none_coalesce_item: "b%d" % m.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)("Committing changes to branch '%s'..." % m.branches[m.branch].name))  # line 684
    m.integrateChangeset(changes, clear=True)  # update pathset to changeset only  # line 685
    m.saveCommit(m.branch, revision)  # revision has already been incremented  # line 686
    m.commits[revision] = CommitInfo(revision, int(time.time() * 1000), argument)  # comment can be None  # line 687
    m.saveBranch(m.branch)  # line 688
    if m.picky:  # line 689
        m.loadBranches()  # TODO is this necessary?  # line 690
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], tracked=[])  # remove tracked patterns after commit in picky mode  # line 691
        m.saveBranches()  # line 692
    info("Created new revision r%d%s (+%d/-%d/~%d)" % (revision, ((" '%s'" % argument) if argument is not None else ""), len(changes.additions), len(changes.deletions), len(changes.modifications)))  # line 693

def status() -> 'None':  # line 695
    ''' Show branches and current repository state. '''  # line 696
    m = Metadata(os.getcwd())  # type: Metadata  # line 697
    m.loadBranches()  # knows current branch  # line 698
    current = m.branch  # type: int  # line 699
    info("Offline repository status:")  # line 700
    sl = max([len((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(b.name)) for b in m.branches.values()])  # type: int  # line 701
    for branch in sorted(m.branches.values(), key=lambda b: b.number):  # line 702
        m.loadBranch(branch.number)  # knows commit history  # line 703
        print("  %s b%d%s @%s (%s) with %d commits%s" % ("*" if current == branch.number else " ", branch.number, ((" %%%ds" % (sl + 2)) % ("'%s'" % branch.name)) if branch.name else "", strftime(branch.ctime), "in sync" if branch.insync else "dirty", len(m.commits), ". Last comment: '%s'" % m.commits[max(m.commits)].message if m.commits[max(m.commits)].message else ""))  # line 704
    if m.track or m.picky and len(m.branches[m.branch].tracked) > 0:  # line 705
        info("\nTracked file patterns:")  # line 706
        print("\n  | " + "\n  | ".join((path for path in m.branches[m.branch].tracked)))  # line 707

def stopOnChanges(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[], check: 'bool'=True, commit: 'bool'=False) -> 'Tuple[Metadata, _coconut.typing.Optional[int], int, ChangeSet, bool, bool, FrozenSet[str]]':  # line 709
    ''' Common behavior for switch, update, delete, commit.
      check: stop program on detected change
      commit: don't stop on changes, because that's what we need in the operation
      Returns (Metadata, (current or target) branch, revision, set of changes vs. last commit on current branch, strict, force flags. '''  # line 713
    m = Metadata(os.getcwd())  # type: Metadata  # line 714
    m.loadBranches()  # knows current branch  # line 715
    trackingPatterns = m.getTrackingPatterns()  # type: FrozenSet[str]  # SVN-like mode  # line 716
    force = '--force' in options  # type: bool  # line 717
    strict = '--strict' in options or m.strict  # type: bool  # line 718
    if argument is not None:  # line 719
        branch, revision = m.parseRevisionString(argument)  # for early abort  # line 720
        if branch is None:  # line 721
            Exit("Branch '%s' doesn't exist. Cannot proceed" % argument)  # line 721
    m.loadBranch(m.branch)  # knows last commits of *current* branch  # line 722

# Determine current changes
    m.computeSequentialPathSet(m.branch, max(m.commits))  # load all commits up to specified revision  # line 725
    changes = m.findChanges(checkContent=strict, considerOnly=None if not m.track and not m.picky else trackingPatterns) if not commit else m.findChanges(m.branch, max(m.commits) + 1, checkContent=strict, considerOnly=None if not m.track and not m.picky else trackingPatterns)  # type: ChangeSet  # line 726
    if (changes.additions or changes.deletions or changes.modifications) and not force:  # and check?  # line 727
        m.listChanges(changes)  # line 728
        if check and not commit:  # line 729
            Exit("File tree contains changes. Use --force to proceed")  # line 729
    elif commit and not force:  #  and not check  # line 730
        Exit("Nothing to commit. Aborting")  #  and not check  # line 730

    if argument is not None:  # branch/revision specified  # line 732
        m.loadBranch(branch)  # knows commits of target branch  # line 733
        revision = revision if revision >= 0 else len(m.commits) + revision  # negative indexing  # line 734
        if revision < 0 or revision > max(m.commits):  # line 735
            Exit("Unknown revision r%d" % revision)  # line 735
        return (m, branch, revision, changes, strict, force, m.getTrackingPatterns(branch))  # line 736
    return (m, m.branch, max(m.commits) + (1 if commit else 0), changes, strict, force, trackingPatterns)  # line 737

def switch(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]) -> 'None':  # line 739
    ''' Continue work on another branch, replacing file tree changes. '''  # line 740
    changes = None  # type: ChangeSet  # line 741
    m, branch, revision, changes, strict, force, trackingPatterns = stopOnChanges(argument, options)  # line 742
    debug("Switching to branch %sb%d/r%d..." % ("'%s' " % m.branches[branch].name if m.branches[branch].name else "", branch, revision))  # line 743

# Determine file changes from other branch to current file tree
    if '--meta' in options:  # only switch meta data  # line 746
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], tracked=m.branches[branch].tracked)  # line 747
    else:  # full file switch  # line 748
        m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision for target branch into memory  # line 749
        changes = m.findChanges(checkContent=strict, inverse=True, considerOnly=None if not m.track else trackingPatterns | m.getTrackingPatterns(branch))  # determine difference of other branch vs. file tree (forced or in sync with current branch; "addition" means exists now and should be removed)  # line 750
        if not (changes.additions or changes.deletions or changes.modifications):  # line 751
            info("No changes to current file tree")  # line 752
        else:  # integration required  # line 753
            for path, pinfo in changes.deletions.items():  # line 754
                m.restoreFile(path, branch, revision, pinfo)  # is deleted in current file tree: restore from branch to reach target  # line 755
                debug("ADD " + path)  # line 756
            for path, pinfo in changes.additions.items():  # line 757
                os.unlink(os.path.join(m.root, path.replace("/", os.sep)))  # is added in current file tree: remove from branch to reach target  # line 758
                debug("DEL " + path)  # line 759
            for path, pinfo in changes.modifications.items():  # line 760
                m.restoreFile(path, branch, revision, pinfo)  # is modified in current file tree: restore from branch to reach target  # line 761
                debug("MOD " + path)  # line 762
    m.branch = branch  # line 763
    m.saveBranches()  # store switched path info  # line 764
    info("Switched to branch %sb%d/r%d" % ("'%s' " % (m.branches[branch].name if m.branches[branch].name else ""), branch, revision))  # line 765

def update(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]) -> 'None':  # line 767
    ''' Load and integrate a specified other branch/revision into current life file tree.
      In tracking mode, this also updates the set of tracked patterns.
      User options for merge operation: --add (don't remove), --rm (don't insert), --add-lines/--rm-lines (inside each file)
      User options for conflict resolution: --theirs/--mine/--ask
  '''  # line 772
    mrg = firstOfMap({"--add": MergeOperation.INSERT, "--rm": MergeOperation.REMOVE}, options, MergeOperation.BOTH)  # type: int  # default operation is replicate remove state for non-conflicting cases (insertions/deletions)  # line 773
    res = firstOfMap({'--theirs': ConflictResolution.THEIRS, '--mine': ConflictResolution.MINE}, options, ConflictResolution.NEXT)  # type: int  # NEXT means deeper level  # line 774
    mrgline = firstOfMap({'--add-lines': MergeOperation.INSERT, '--rm-lines': MergeOperation.REMOVE}, options, mrg)  # type: int  # default operation for modified files is same as for files  # line 775
    resline = firstOfMap({'--theirs-lines': ConflictResolution.THEIRS, '--mine-lines': ConflictResolution.MINE}, options, ConflictResolution.ASK)  # type: int  # line 776
    m = Metadata(os.getcwd())  # type: Metadata  # TODO same is called inside stop on changes - could return both current and designated branch instead  # line 777
    m.loadBranches()  # line 778
    changes = None  # type: ChangeSet  # line 778
    currentBranch = m.branch  # type: _coconut.typing.Optional[int]  # line 779
    m, branch, revision, changes, strict, force, trackingPatterns = stopOnChanges(argument, options, check=False)  # don't check for current changes, only parse arguments  # line 780
    debug("Integrating changes from '%s/r%d' into file tree..." % ((lambda _coconut_none_coalesce_item: "b%d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 781

# Determine file changes from other branch over current file tree
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision for branch to integrate  # line 784
    trackingUnion = trackingPatterns | m.getTrackingPatterns(branch)  # type: FrozenSet[str]  # line 785
    changes = m.findChanges(checkContent=strict, inverse=True, considerOnly=None if not m.track else trackingUnion)  # type: ChangeSet  # determine difference of other branch vs. file tree. "addition" means exists now but not in other, and should be removed unless in tracking mode  # line 786
    if not (mrg & MergeOperation.INSERT and changes.additions or (mrg & MergeOperation.REMOVE and changes.deletions) or changes.modifications):  # line 787
        if trackingUnion == trackingPatterns:  # nothing added  # line 788
            info("No file changes detected, but tracking patterns were merged (run 'sos switch /-1 --meta' to undo)")  # TODO write test to see if this works  # line 789
        else:  # line 790
            info("Nothing to update")  # but write back updated branch info below  # line 791
    else:  # integration required  # line 792
        for path, pinfo in changes.deletions.items():  # deletions mark files not present in current file tree -> needs additon  # line 793
            if mrg & MergeOperation.INSERT:  # deleted in current file tree: restore from branch to reach target  # line 794
                m.restoreFile(path, branch, revision, pinfo)  # deleted in current file tree: restore from branch to reach target  # line 794
            print("ADD " + path if mrg & MergeOperation.INSERT else "(A) " + path)  # line 795
        for path, pinfo in changes.additions.items():  # line 796
            if m.track or m.picky:  # because untracked files of other branch cannot be detected (which is good)  # line 797
                Exit("This should never happen")  # because untracked files of other branch cannot be detected (which is good)  # line 797
            if mrg & MergeOperation.REMOVE:  # line 798
                os.unlink(m.root + os.sep + path.replace("/", os.sep))  # line 798
            print("DEL " if mrg & MergeOperation.REMOVE else "(D) " + path)  # not contained in other branch, but maybe kept  # line 799
        for path, pinfo in changes.modifications.items():  # line 800
            into = os.path.join(m.root, path.replace("/", os.sep))  # type: str  # line 801
            binary = not m.isTextType(path)  # line 802
            if res & ConflictResolution.ASK or binary:  # line 803
                print(("MOD " if not binary else "BIN ") + path)  # line 804
                reso = {"i": ConflictResolution.MINE, "t": ConflictResolution.THEIRS, "m": ConflictResolution.NEXT}.get(user_input(" Resolve: *M[I]ne, [T]heirs, [M]erge: (I)").strip().lower(), ConflictResolution.MINE)  # line 805
                debug("User selected %d" % reso)  # line 806
            else:  # line 807
                reso = res  # line 807
            if reso & ConflictResolution.THEIRS:  # line 808
                m.readOrCopyVersionedFile(branch, revision, pinfo.namehash, into)  # blockwise copy of contents  # line 809
                print("THR " + path)  # line 810
            elif reso & ConflictResolution.MINE:  # line 811
                print("MNE " + path)  # nothing to do! same as skip  # line 812
            else:  # NEXT: line-based merge  # line 813
                file = m.readOrCopyVersionedFile(branch, revision, pinfo.namehash) if pinfo.size > 0 else b''  # type: str  # parse lines TODO decode etc.  # line 814
                if file is not None:  # if None, error message was already logged  # line 815
                    contents = merge(filename=file, intoname=into, mergeOperation=mrgline, conflictResolution=resline)  # type: bytes  # line 816
                    with open(path, "wb") as fd:  # TODO write to temp file first  # line 817
                        fd.write(contents)  # TODO write to temp file first  # line 817
    info("Integrated changes from '%s/r%d' into file tree" % ((lambda _coconut_none_coalesce_item: "b%d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 818
    m.branches[currentBranch] = dataCopy(BranchInfo, m.branches[currentBranch], insync=False, tracked=list(trackingUnion))  # TODO really? it's a change that cannot be undone easily by the user  # line 819
    m.branch = currentBranch  # need to restore setting before saving TODO operate on different objects instead  # line 820
    m.saveBranches()  # line 821

def delete(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]) -> 'None':  # line 823
    ''' Remove a branch entirely. '''  # line 824
    m, branch, revision, changes, strict, force, trackingPatterns = stopOnChanges(argument, options)  # line 825
    if len(m.branches) == 1:  # line 826
        Exit("Cannot remove the only remaining branch. Use 'sos online' to leave offline mode")  # line 826
    debug("Removing branch %d%s..." % (branch, " '%s'" % m.branches[branch].name if m.branches[branch].name else ""))  # line 827
    binfo = m.removeBranch(branch)  # need to keep a reference to removed entry for output below  # line 828
    info("Branch b%d%s removed" % (branch, " '%s'" % binfo.name if binfo.name else ""))  # line 829

def add(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]) -> 'None':  # line 831
    ''' Add a tracked files pattern to current branch's tracked files. '''  # line 832
    force = '--force' in options  # type: bool  # line 833
    m = Metadata(os.getcwd())  # type: Metadata  # line 834
    m.loadBranches()  # line 835
    if not m.track and not m.picky:  # line 836
        Exit("Repository is in simple mode. Needs 'offline --track' or 'offline --picky' instead")  # line 836
    relpath = os.path.relpath(os.path.dirname(os.path.abspath(argument)), m.root)  # for tracking list  # line 837
    pattern = os.path.join(relpath, os.path.basename(argument)).replace(os.sep, "/")  # line 838
    if pattern in m.branches[m.branch].tracked:  # line 839
        Exit("%s '%s' already tracked" % ("Glob" if isglob(pattern) else "File", pattern))  # line 840
    if not force and len(fnmatch.filter(os.listdir(os.path.abspath(relpath)), os.path.basename(pattern.replace("/", os.sep)))) == 0:  # doesn't match any current file  # line 841
        Exit("Pattern doesn't match any file in specified folder. Use --force to add it anyway")  # line 842
    m.branches[m.branch].tracked.append(pattern)  # line 843
    m.saveBranches()  # line 844
    info("Added tracking pattern '%s' for folder '%s'" % (os.path.basename(pattern.replace("/", os.sep)), os.path.abspath(relpath)))  # line 845

def rm(argument: 'str') -> 'None':  # line 847
    ''' Remove a tracked files pattern from current branch's tracked files. '''  # line 848
    m = Metadata(os.getcwd())  # type: Metadata  # line 849
    m.loadBranches()  # line 850
    if not m.track and not m.picky:  # line 851
        Exit("Repository is in simple mode. Needs 'offline --track' or 'offline --picky' instead")  # line 851
    relpath = os.path.relpath(os.path.dirname(os.path.abspath(argument)), m.root)  # type: str  # line 852
    pattern = os.path.join(relpath, os.path.basename(argument)).replace(os.sep, "/")  # type: str  # line 853
    if pattern not in m.branches[m.branch].tracked:  # line 854
        suggestion = _coconut.set()  # type: Set[str]  # line 855
        for pat in m.branches[m.branch].tracked:  # line 856
            if fnmatch.fnmatch(pattern, pat):  # line 857
                suggestion.add(pat)  # line 857
        if suggestion:  # line 858
            print("Do you mean any of the following tracked globs? '%s'" % (", ".join(sorted(suggestion))))  # line 858
        Exit("Tracked pattern '%s' not found" % pattern)  # line 859
    m.branches[m.branch].tracked.remove(pattern)  # line 860
    m.saveBranches()  # line 861
    info("Removed tracking pattern '%s' for folder '%s'" % (os.path.basename(pattern.replace("/", os.sep)), os.path.abspath(relpath)))  # line 862

def ls(argument: '_coconut.typing.Optional[str]'=None) -> 'None':  # line 864
    ''' List specified directory, augmenting with repository metadata. '''  # line 865
    cwd = os.getcwd() if argument is None else argument  # type: str  # line 866
    m = Metadata(cwd)  # type: Metadata  # line 867
    m.loadBranches()  # line 868
    relpath = os.path.relpath(cwd, m.root).replace(os.sep, "/")  # type: str  # line 869
    files = list(sorted((entry for entry in os.listdir(cwd) if os.path.isfile(entry))))  # type: List[str]  # line 870
    trackingPatterns = m.getTrackingPatterns() if m.track or m.picky else _coconut.frozenset()  # type: FrozenSet[str]  # for current branch  # line 871
    for file in files:  # line 872
        ignore = None  # type: _coconut.typing.Optional[str]  # line 873
        for ig in m.c.ignores:  # line 874
            if fnmatch.fnmatch(file, ig):  # remember first match TODO document this  # line 875
                ignore = ig  # remember first match TODO document this  # line 875
                break  # remember first match TODO document this  # line 875
        if ig:  # line 876
            for wl in m.c.ignoresWhitelist:  # line 877
                if fnmatch.fnmatch(file, wl):  # found a white list entry for ignored file, undo ignoring it  # line 878
                    ignore = None  # found a white list entry for ignored file, undo ignoring it  # line 878
                    break  # found a white list entry for ignored file, undo ignoring it  # line 878
        if ignore is None:  # line 879
            matches = []  # type: List[str]  # line 880
            for pattern in (p for p in trackingPatterns if os.path.dirname(p) == relpath):  # only patterns matching current folder  # line 881
                if fnmatch.fnmatch(file, os.path.basename(pattern)):  # TODO or only file basename?  # line 882
                    matches.append(pattern)  # TODO or only file basename?  # line 882
        print("%s %s%s" % ("IGN" if ignore is not None else ("TRK" if len(matches) > 0 else "   "), file, ' by "%s"' % ignore if ignore is not None else (" by " + ";".join(['"%s"' % match for match in matches]) if len(matches) > 0 else "")))  # line 883

def log() -> 'None':  # line 885
    ''' List previous commits on current branch. '''  # TODO --verbose for changesets  # line 886
    m = Metadata(os.getcwd())  # type: Metadata  # line 887
    m.loadBranches()  # knows current branch  # line 888
    m.loadBranch(m.branch)  # knows commit history  # line 889
    info((lambda _coconut_none_coalesce_item: "r%d" % m.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)("Offline commit history of branch '%s':" % m.branches[m.branch].name))  # TODO also retain "from branch/revision" on branching?  # line 890
    nl = len("%d" % max(m.commits))  # determine space needed for revision  # line 891
    for commit in sorted(m.commits.values(), key=lambda co: co.number):  # line 892
        print("  %s r%s @%s: %s" % ("*" if commit.number == max(m.commits) else " ", ("%%%ds" % nl) % commit.number, strftime(commit.ctime), (lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(commit.message)))  # line 893
# TODO list number of files and binary/text

def config(argument, options) -> 'None':  # line 896
    if argument not in ["set", "unset", "show", "add", "rm"]:  # line 897
        Exit("Unknown config command")  # line 897
    if not configr:  # line 898
        Exit("Cannot execute config command. 'configr' module not installed")  # line 898
    c = loadConfig()  # line 899
    if argument == "set":  # line 900
        if len(options) < 2:  # line 901
            Exit("No key nor value specified")  # line 901
        if options[0] not in (["defaultbranch"] + CONFIGURABLE_FLAGS + CONFIGURABLE_LISTS):  # line 902
            Exit("Unsupported key %r" % options[0])  # line 902
        c[options[0]] = options[1].lower() in TRUTH_VALUES if options[0] in CONFIGURABLE_FLAGS else (options[1].strip() if options[0] not in CONFIGURABLE_LISTS else [options[0]])  # TODO sanitize texts?  # line 903
        f, g = c.saveSettings()  # line 904
        if f is None:  # line 905
            error("Error saving user configuration: %r" % g)  # line 905
    elif argument == "unset":  # line 906
        if len(options) < 1:  # line 907
            Exit("No key specified")  # line 907
        if options[0] not in c.keys():  # line 908
            Exit("Unsupported key")  # line 908
        try:  # line 909
            del c[options[0]]  # line 910
            f, g = c.saveSettings()  # line 911
            if f is None:  # line 912
                error("Error saving user configuration: %r" % g)  # line 912
        except Exception as E:  # line 913
            Exit("Unknown key specified: %r (%r)" % (options[0], E))  # line 913
    elif argument == "add":  # line 914
        if len(options) < 2:  # line 915
            Exit("No key nor value specified")  # line 915
        if options[0] not in CONFIGURABLE_LISTS:  # line 916
            Exit("Unsupported key for add %r" % options[0])  # line 916
        if options[0] not in c.keys():  # add list  # line 917
            c[options[0]] = [options[1]]  # add list  # line 917
        elif options[1] in c[options[0]]:  # line 918
            Exit("Value already contained")  # line 918
        c[options[0]].append(options[1])  # line 919
        f, g = c.saveSettings()  # line 920
        if f is None:  # line 921
            error("Error saving user configuration: %r" % g)  # line 921
    elif argument == "rm":  # line 922
        if len(options) < 2:  # line 923
            Exit("No key nor value specified")  # line 923
        if options[0] not in c.keys():  # line 924
            Exit("Unknown key specified: %r" % options[0])  # line 924
        del c[options[0]][options[0]]  # line 925
        f, g = c.saveSettings()  # line 926
        if f is None:  # line 927
            error("Error saving user configuration: %r" % g)  # line 927
    else:  # Show  # line 928
        for k, v in sorted(c.items()):  # line 929
            print("%s => %s" % (k, v))  # line 929

def parse(root: 'str'):  # line 931
    ''' Main operation. '''  # line 932
    debug("Parsing command-line arguments...")  # line 933
    command = sys.argv[1].strip() if len(sys.argv) > 1 else ""  # line 934
    argument = sys.argv[2].strip() if len(sys.argv) > 2 else None  # line 935
    options = sys.argv[3:] if command == "config" else [c for c in sys.argv[2:] if c.startswith("--")]  # consider second parameter for no-arg command, otherwise from third on  # line 936
    debug("Processing command %r with argument '%s' and options %r." % ("" if command is None else command, "" if argument is None else argument, options))  # line 937
    if command == "offline":  # line 938
        offline(argument, options)  # line 938
    elif command == "online":  # line 939
        online(options)  # line 939
    elif command == "branch":  # line 940
        branch(argument, options)  # line 940
    elif command == "changes":  # line 941
        changes(argument, options)  # line 941
    elif command == "diff":  # line 942
        diff(argument, options)  # line 942
    elif command == "status":  # line 943
        status()  # line 943
    elif command == "commit":  # line 944
        commit(argument, options)  # line 944
    elif command == "switch":  # line 945
        switch(argument, options)  # line 945
    elif command == "update":  # line 946
        update(argument, options)  # line 946
    elif command == "delete":  # line 947
        delete(argument, options)  # line 947
    elif command == "add":  # line 948
        add(argument, options)  # line 948
    elif command == "rm":  # line 949
        rm(argument)  # line 949
    elif command == 'ls':  # line 950
        ls(argument)  # line 950
    elif command == "log":  # line 951
        log()  # line 951
    elif command == 'config':  # line 952
        config(argument, options)  # line 952
    elif command == "help":  # line 953
        usage()  # line 953
    else:  # line 954
        Exit("Unknown command '%s'" % command)  # line 954
    sys.exit(0)  # line 955

def findSosVcsBase() -> 'Tuple[_coconut.typing.Optional[str], _coconut.typing.Optional[str], _coconut.typing.Optional[str]]':  # line 957
    ''' Attempts to find sos and legacy VCS base folders. '''  # line 958
    debug("Detecting root folders...")  # line 959
    path = os.getcwd()  # type: str  # start in current folder, check parent until found or stopped  # line 960
    vcs = (None, None)  # type: Tuple[_coconut.typing.Optional[str], _coconut.typing.Optional[str]]  # line 961
    while not os.path.exists(os.path.join(path, metaFolder)):  # line 962
        contents = set(os.listdir(path))  # line 963
        vcss = [executable for folder, executable in vcsFolders.items() if folder in contents]  # type: _coconut.typing.Sequence[str]  # determine VCS type  # line 964
        choice = None  # type: _coconut.typing.Optional[str]  # line 965
        if len(vcss) > 1:  # line 966
            choice = "svn" if "svn" in vcss else vcss[0]  # line 967
            warn("Detected more than one parallel VCS checkouts %r. Falling back to '%s'" % (vcss, choice))  # line 968
        elif len(vcss) > 0:  # line 969
            choice = vcss[0]  # line 969
        if not vcs[0] and choice:  # memorize current repo root  # line 970
            vcs = (path, choice)  # memorize current repo root  # line 970
        new = os.path.dirname(path)  # get parent path  # line 971
        if new == path:  # avoid infinite loop  # line 972
            break  # avoid infinite loop  # line 972
        path = new  # line 973
    if os.path.exists(os.path.join(path, metaFolder)):  # found something  # line 974
        if vcs[0]:  # already detected vcs base and command  # line 975
            return (path, vcs[0], vcs[1])  # already detected vcs base and command  # line 975
        sos = path  # line 976
        while True:  # continue search for VCS base  # line 977
            new = os.path.dirname(path)  # get parent path  # line 978
            if new == path:  # no VCS folder found  # line 979
                return (sos, None, None)  # no VCS folder found  # line 979
            path = new  # line 980
            contents = set(os.listdir(path))  # line 981
            vcss = [executable for folder, executable in vcsFolders.items() if folder in contents]  # determine VCS type  # line 982
            choice = None  # line 983
            if len(vcss) > 1:  # line 984
                choice = "svn" if "svn" in vcss else vcss[0]  # line 985
                warn("Detected more than one parallel VCS checkouts %r. Falling back to '%s'" % (vcss, choice))  # line 986
            elif len(vcss) > 0:  # line 987
                choice = vcss[0]  # line 987
            if choice:  # line 988
                return (sos, path, choice)  # line 988
    return (None, vcs[0], vcs[1])  # line 989

def main():  # line 991
    if '--help' in sys.argv or len(sys.argv) < 2:  # line 992
        usage()  # line 992
        Exit()  # line 992
    command = sys.argv[1] if len(sys.argv) > 1 else None  # type: _coconut.typing.Optional[str]  # line 993
    root, vcs, cmd = findSosVcsBase()  # root is None if no .sos folder exists up the folder tree (still working online); vcs is checkout/repo root folder; cmd is the VCS base command  # line 994
    debug("Found root folders for SOS/VCS: %s/%s" % ("" if root is None else root, "" if vcs is None else vcs))  # line 995
    defaults["defaultbranch"] = vcsBranches.get(cmd, "trunk")  # sets dynamic default with SVN fallback  # line 996
    if sos or root is not None or ("" if command is None else command) == "offline":  # in offline mode or just going offline TODO what about git config?  # line 997
        os.chdir(os.getcwd() if command == "offline" else os.getcwd() if root is None else root)  # since all operatiosn use os.getcwd() and we save one argument to each function  # line 998
        parse(root)  # line 999
    else:  # online mode - delegate to VCS  # line 1000
        info("SOS: Running '%s %s'" % (cmd, " ".join(sys.argv[1:])))  # line 1001
        import subprocess  # only requuired in this section  # line 1002
        process = subprocess.Popen([cmd] + sys.argv[1:], shell=False, stdin=subprocess.PIPE, stdout=sys.stdout, stderr=sys.stderr)  # line 1003
        inp = ""  # type: str  # line 1004
        while True:  # line 1005
            so, se = process.communicate(input=inp)  # line 1006
            if process.returncode is not None:  # line 1007
                break  # line 1007
            inp = sys.stdin.read()  # line 1008
        if sys.argv[1] == "commit" and process.returncode == 0:  # successful commit - assume now in sync again (but leave meta data folder with potential other feature branches behind until "online")  # line 1009
            if root is None:  # line 1010
                Exit("Cannot determine VCS root folder: Unable to mark repository as synchronized and will show a warning when leaving offline mode")  # line 1010
            m = Metadata(root)  # line 1011
            m.loadBranches()  # read repo  # line 1012
            m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], insync=True)  # mark as committed  # line 1013
            m.saveBranches()  # line 1014


if __name__ == '__main__':  # line 1017
    level = logging.DEBUG if os.environ.get("DEBUG", "False").lower() == "true" or '--verbose' in sys.argv or '-v' in sys.argv else logging.INFO  # line 1018
    logging.basicConfig(level=level, stream=sys.stderr if '--log' in sys.argv else sys.stdout, format=("%(asctime)-23s %(levelname)-8s %(name)s:%(lineno)d | %(message)s" if '--log' in sys.argv else "%(message)s"))  # line 1019
    sos = '--sos' in sys.argv  # line 1020
    for option in (o for o in ['--log', '--verbose', '-v', '--sos'] if o in sys.argv):  # clean up program arguments  # line 1021
        sys.argv.remove(option)  # clean up program arguments  # line 1021

logger = Logger(logging.getLogger(__name__))  # line 1023
debug, info, warn, error = logger.debug, logger.info, logger.warn, logger.error  # line 1023

if __name__ == '__main__':  # line 1025
    main()  # line 1025
