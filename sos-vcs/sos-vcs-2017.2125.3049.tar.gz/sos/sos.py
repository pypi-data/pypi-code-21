#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x846c0008

# Compiled with Coconut version 1.3.1-post_dev8 [Dead Parrot]

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
except:  # typing not available (e.g. Python 2)  # line 6
    pass  # typing not available (e.g. Python 2)  # line 6
from sos import version  # line 7

# External dependencies
try:  # optional dependency  # line 10
    import configr  # optional dependency  # line 10
except:  # declare as undefined  # line 11
    configr = None  # declare as undefined  # line 11
#from enforce import runtime_validation  # https://github.com/RussBaz/enforce  TODO doesn't work for "data" types
UTF8 = "utf_8"  # early used constant, not defined in standard library  # line 13
try:  # line 14
    import chardet  # https://github.com/chardet/chardet  # line 15
    def detect(binary: 'bytes') -> 'str':  # line 16
        return chardet.detect(binary)["encoding"]  # line 16
except:  # Python 2 workaround  # line 17
    def detect(binary: 'bytes') -> 'str':  # Guess the encoding  # line 18
        try:  # line 19
            binary.decode(UTF8)  # line 19
            return UTF8  # line 19
        except UnicodeError:  # line 20
            pass  # line 20
        try:  # line 21
            binary.decode("utf_16")  # line 21
            return "utf_16"  # line 21
        except UnicodeError:  # line 22
            pass  # line 22
        try:  # line 23
            binary.decode("cp1252")  # line 23
            return "cp1252"  # line 23
        except UnicodeError:  # line 24
            pass  # line 24
        return "ascii"  # this code will never be reached, as above is an 8-bit charset that always matches  # line 25


class BranchInfo(_coconut_NamedTuple("BranchInfo", [("number", 'int'), ("ctime", 'int'), ("name", '_coconut.typing.Optional[str]'), ("insync", 'bool'), ("tracked", 'List[str]')])):  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 28
    __slots__ = ()  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 28
    __ne__ = _coconut.object.__ne__  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 28
    def __new__(_cls, number, ctime, name=None, insync=False, tracked=[]):  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 28
        return _coconut.tuple.__new__(_cls, (number, ctime, name, insync, tracked))  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 28
# tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place
class CommitInfo(_coconut_NamedTuple("CommitInfo", [("number", 'int'), ("ctime", 'int'), ("message", '_coconut.typing.Optional[str]')])):  # line 29
    __slots__ = ()  # line 29
    __ne__ = _coconut.object.__ne__  # line 29
    def __new__(_cls, number, ctime, message=None):  # line 29
        return _coconut.tuple.__new__(_cls, (number, ctime, message))  # line 29

class PathInfo(_coconut_NamedTuple("PathInfo", [("namehash", 'str'), ("size", '_coconut.typing.Optional[int]'), ("mtime", 'int'), ("hash", 'str')])):  # size == None means deleted in this revision  # line 30
    __slots__ = ()  # size == None means deleted in this revision  # line 30
    __ne__ = _coconut.object.__ne__  # size == None means deleted in this revision  # line 30
class ChangeSet(_coconut_NamedTuple("ChangeSet", [("additions", 'Dict[str, PathInfo]'), ("deletions", 'Dict[str, PathInfo]'), ("modifications", 'Dict[str, PathInfo]')])):  # avoid default assignment of {} as it leads to runtime errors (contains data on init for unknown reason)  # line 31
    __slots__ = ()  # avoid default assignment of {} as it leads to runtime errors (contains data on init for unknown reason)  # line 31
    __ne__ = _coconut.object.__ne__  # avoid default assignment of {} as it leads to runtime errors (contains data on init for unknown reason)  # line 31
class Range(_coconut_NamedTuple("Range", [("tipe", 'int'), ("indexes", '_coconut.typing.Sequence[int]')])):  # MergeBlockType[1,2,4], line number, length  # line 32
    __slots__ = ()  # MergeBlockType[1,2,4], line number, length  # line 32
    __ne__ = _coconut.object.__ne__  # MergeBlockType[1,2,4], line number, length  # line 32
class MergeBlock(_coconut_NamedTuple("MergeBlock", [("tipe", 'int'), ("lines", '_coconut.typing.Sequence[str]'), ("line", 'int'), ("replaces", '_coconut.typing.Optional[MergeBlock]'), ("changes", '_coconut.typing.Optional[Range]')])):  # line 33
    __slots__ = ()  # line 33
    __ne__ = _coconut.object.__ne__  # line 33
    def __new__(_cls, tipe, lines, line, replaces=None, changes=None):  # line 33
        return _coconut.tuple.__new__(_cls, (tipe, lines, line, replaces, changes))  # line 33


class ConflictResolution:  # prefer their changes, prefer my changes, ask user for each change, go to next deeper level (e.g. from files to lines, characters)  # line 35
    THEIRS, MINE, ASK, NEXT = range(4)  # prefer their changes, prefer my changes, ask user for each change, go to next deeper level (e.g. from files to lines, characters)  # line 35
class MergeOperation:  # insert remote changes into current, remove remote deletions from current, do both (replicate remote state) TODO handle inline-operations separate?  # line 36
    INSERT, REMOVE, BOTH = 1, 2, 3  # insert remote changes into current, remove remote deletions from current, do both (replicate remote state) TODO handle inline-operations separate?  # line 36
class MergeBlockType:  # modify = intra-line changes  # line 37
    KEEP, INSERT, REMOVE, REPLACE, MODIFY, MOVE = range(6)  # modify = intra-line changes  # line 37

class Accessor(dict):  # line 39
    ''' Dictionary with attribute access. Writing only supported via dictionary access. '''  # line 40
    def __init__(_, mapping) -> 'None':  # line 41
        dict.__init__(_, mapping)  # line 41
    @_coconut_tco  # line 42
    def __getattribute__(_, name: 'str') -> 'List[str]':  # line 42
        try:  # line 43
            return _[name]  # line 43
        except:  # line 44
            return _coconut_tail_call(dict.__getattribute__, _, name)  # line 44

# Constants
APPNAME = "Subversion Offline Solution  V%s  (C) Arne Bachmann" % version.__release_version__  # type: str  # line 47
CONFIGURABLE_FLAGS = ["strict", "track", "picky", "compress"]  # line 48
CONFIGURABLE_LISTS = ["texttype", "bintype", "ignores", "ignoreDirs", "ignoresWhitelist", "ignoreDirsWhitelist"]  # line 49
TRUTH_VALUES = ["true", "yes", "on", "1", "enable", "enabled"]  # all lower-case normalized  # line 50
PROGRESS_MARKER = ["|", "/", "-", "\\"]  # line 51
metaFolder = ".sos"  # type: str  # line 52
metaFile = ".meta"  # type: str  # line 53
bufSize = 1 << 20  # type: int  # 1 MiB  # line 54
vcsFolders = {".svn": "svn", ".git": "git", ".bzr": "bzr", ".hg": "hg", ".fslckout": " fossil", ".CVS": "cvs"}  # type: Dict[str, str]  # line 55
vcsBranches = {"svn": "trunk", "git": "master", "bzr": "trunk", "hg": "default", "fossil": None, "cvs": None}  # type: Dict[str, _coconut.typing.Optional[str]]  # line 56
defaults = Accessor({"strict": False, "track": False, "picky": False, "compress": True, "texttype": [], "bintype": [], "ignoreDirs": [".*", "__pycache__"], "ignoreDirsWhitelist": [], "ignores": ["__coconut__.py", "*.bak", "*.py[cdo]", "*.class", ".fslckout"], "ignoresWhitelist": []})  # type: Accessor  # line 57

def Exit(message: 'str'="") -> 'None':  # line 59
    print(message, file=sys.stderr)  # line 59
    sys.exit(1)  # line 59

@_coconut_tco  # dynamic Python2/3. don't simplify, eval must be inside function for unknown reason  # line 61
def user_input(msg: 'str') -> 'str':  # dynamic Python2/3. don't simplify, eval must be inside function for unknown reason  # line 61
    return _coconut_tail_call(eval("input" if sys.version_info.major >= 3 else "raw_input"), msg)  # dynamic Python2/3. don't simplify, eval must be inside function for unknown reason  # line 61

try:  # line 63
    Splittable = TypeVar("Splittable", str, bytes)  # line 63
except:  # Python 2  # line 64
    pass  # Python 2  # line 64
def safeSplit(s: 'Splittable', d: '_coconut.typing.Optional[Splittable]'=None) -> '_coconut.typing.Sequence[Splittable]':  # line 65
    return s.split(("\n" if isinstance(s, str) else b"\n") if d is None else d) if len(s) > 0 else []  # line 65

def ajoin(sep: 'str', seq: '_coconut.typing.Sequence[str]', nl="") -> 'str':  # line 67
    return sep + (sep + nl).join(seq)  # line 67
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
    encoding = None  # type: str  # line 134
    eol = None  # type: bytes  # line 134
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
            warn("Inconsistent CR/NL count. Mixed EOL style detected, may cause problems during merge")  # line 156
        return b"\r\n"  # line 157
    if lf != 0 and cr != 0:  # line 158
        warn("Inconsistent CR/NL count. Mixed EOL style detected, may cause problems during merge")  # line 158
    if lf > cr:  # Linux/Unix  # line 159
        return b"\n"  # Linux/Unix  # line 159
    if cr > lf:  # older 8-bit machines  # line 160
        return b"\r"  # older 8-bit machines  # line 160
    return None  # no new line contained, cannot determine  # line 161

def usage() -> 'None':  # line 163
    print("""/// {appname}

Usage: {cmd} <command> [<argument>] [<option1>, ...]        For command "offline" and when in offline mode
       {cmd} <underlying vcs command and arguments>         Unless working in offline mode

  Available commands:
    offline [<name>]                                      Start working offline, creating a branch (named <name>)
      --track                                               Setup SVN-style mode: users add/remove tracking patterns per branch
      --picky                                               Setup Git-style mode: users pick files for each operation
    online                                                Finish working offline

    branch  [<name>] [--last] [--stay]                    Create a new branch from current file tree and switch to it
      --last                                                Use last revision, not current file tree, but keep file tree unchanged
      --stay                                                Don't switch to new branch, continue on current one
    switch  [<branch>][/<revision>] [--meta]              Continue work on another branch
      --meta                                                Only switch file tracking patterns for current branch, don't update any files
    update  [<branch>][/<revision>]                       Integrate work from another branch TODO add many merge and conflict resolution options
    delete  [<branch>]                                    Remove (current) branch entirely

    commit  [<message>]                                   Create a new revision from current state file tree, with an optional commit message
    changes [<branch>][/<revision>]                       List changed paths vs. last or specified revision
    diff    [<branch>][/<revision>]                       List changes vs. last or specified revision
    add     [<filename or glob pattern>]                  Add a tracking pattern to current branch (path/filename or glob pattern)
    rm      [<filename or glob pattern>]                  Remove a tracking pattern. Only useful after "offline --track" or "offline --picky"

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
    help, --help                                          Show this usage information

  Arguments:
    <branch/revision>           Revision string. Branch is optional and may be a label or index
                                Revision is an optional integer and may be negative to reference from the latest commits (-1 is most recent revision)

  Common options:
    --force                     Executes potentially harmful operations
                                  for offline: ignore being already offline, start from scratch (same as online --force; offline)
                                  for online: ignore uncommitted branches
                                  for commit, switch, update, add: ignore uncommitted changes before executing command
    --strict                    Perform full content comparison, don't rely only on file size and timestamp
                                  for offline: persist strict mode in repository
                                  for changes, diff, commit, switch, update, delete: perform operation in strict mode
    --{cmd}                       When executing {CMD} not being offline, pass arguments to {CMD} instead (e.g. {cmd} --{cmd} config set key value.)
    --log                       Enable internals logger
    --verbose                   Enable debugging output""".format(appname=APPNAME, cmd="sos", CMD="SOS"))  # line 215

@_coconut_tco  # line 217
def merge(file: '_coconut.typing.Optional[bytes]'=None, into: '_coconut.typing.Optional[bytes]'=None, filename: '_coconut.typing.Optional[str]'=None, intoname: '_coconut.typing.Optional[str]'=None, mergeOperation=MergeOperation.BOTH, conflictResolution=ConflictResolution.ASK) -> 'bytes':  # line 217
    ''' Merges binary text contents 'file' into file 'into', returning merged result. '''  # line 218
    encoding = None  # type: str  # line 219
    othr = None  # type: _coconut.typing.Sequence[str]  # line 219
    othreol = None  # type: _coconut.typing.Optional[bytes]  # line 219
    curr = None  # type: _coconut.typing.Sequence[str]  # line 219
    curreol = None  # type: _coconut.typing.Optional[bytes]  # line 219
    differ = difflib.Differ()  # line 220
    try:  # load files line-wise and normalize line endings (keep the one of the current file) TODO document  # line 221
        encoding, othreol, othr = detectAndLoad(filename=filename, content=file)  # line 222
        encoding, curreol, curr = detectAndLoad(filename=intoname, content=into)  # line 223
    except Exception as E:  # line 224
        Exit("Cannot merge '%s' into '%s': %r" % (filename, intoname, E))  # line 224
    if None not in [othreol, curreol] and othreol != curreol:  # line 225
        warn("Differing EOL-styles detected during merge. Using current file's style for merge output")  # line 225
    output = list(differ.compare(othr, curr))  # type: List[str]  # from generator expression  # line 226
    debug("Diff output: " + "".join([o.replace("\n", "\\n") for o in output]))  # line 227
    blocks = []  # type: List[MergeBlock]  # merged result in blocks  # line 228
    tmp = []  # type: List[str]  # block lines  # line 229
    last = " "  # line 230
    for no, line in enumerate(output + ["X"]):  # EOF marker  # line 231
        if line[0] == last:  # continue filling consecutive block  # line 232
            tmp.append(line[2:])  # continue filling consecutive block  # line 232
            continue  # continue filling consecutive block  # line 232
        if line == "X":  # EOF marker - perform action for remaining block  # line 233
            if len(tmp) == 0:  # nothing left to do  # line 234
                break  # nothing left to do  # line 234
        if last == " ":  # block is same in both files  # line 235
            blocks.append(MergeBlock(MergeBlockType.KEEP, [line for line in tmp], line=no - len(tmp)))  # line 236
        elif last == "-":  # may be a deletion or replacement, store for later  # line 237
            blocks.append(MergeBlock(MergeBlockType.REMOVE, [line for line in tmp], line=no - len(tmp)))  # line 238
        elif last == "+":  # may be insertion or replacement  # line 239
            blocks.append(MergeBlock(MergeBlockType.INSERT, [line for line in tmp], line=no - len(tmp)))  # line 240
            if len(blocks) >= 2 and len(blocks[-1].lines) == len(blocks[-2].lines):  # replaces previously removed section entirely if any  # line 241
                if len(blocks[-1].lines) >= 2 or (blocks[-1].changes is None and blocks[-2].changes is None):  # full block or no intra-line comment  # line 242
                    blocks[-2] = MergeBlock(MergeBlockType.REPLACE, blocks[-1].lines, line=no - len(tmp), replaces=blocks[-2])  # remember replaced stuff  # line 243
                else:  # may have intra-line modifications  # line 244
                    blocks[-2] = MergeBlock(MergeBlockType.MODIFY, blocks[-1].lines, line=no - len(tmp), replaces=blocks[-2], changes=blocks[-1].changes)  # line 245
                blocks.pop()  # remove TOS  # line 246
        elif last == "?":  # intra-line change comment  # line 247
            ilm = getIntraLineMarkers(tmp[0])  # tipe is one of MergeBlockType 1, 2, 4. # "? " line includes a trailing \n for some reason  # line 248
            blocks[-1] = dataCopy(MergeBlock, blocks[-1], tipe=MergeBlockType.MODIFY, changes=ilm)  # update to MODIFY, otherwise may be REPLACE instead  # line 249
        last = line[0]  # line 250
        tmp[:] = [line[2:]]  # line 251
    debug("Diff blocks: " + repr(blocks))  # line 252
    output = []  # line 253
    for block in blocks:  # line 254
        if block.tipe == MergeBlockType.KEEP:  # line 255
            output.extend(block.lines)  # line 256
        elif block.tipe == MergeBlockType.INSERT and not (mergeOperation & MergeOperation.REMOVE):  # line 257
            output.extend(block.lines)  # line 258
        elif block.tipe == MergeBlockType.REPLACE:  # complete block replacement  # line 259
            if mergeOperation & MergeOperation.INSERT:  # replaced stuff TODO allow insertion BEFORE and alternatively AFTER?  # line 260
                output.extend(block.replaces.lines)  # replaced stuff TODO allow insertion BEFORE and alternatively AFTER?  # line 260
            if not (mergeOperation & MergeBlockType.REMOVE):  # if remove, don't add replaced lines, otherwise do  # line 261
                output.extend(block.lines)  # if remove, don't add replaced lines, otherwise do  # line 261
        elif block.tipe == MergeBlockType.REMOVE and mergeOperation & MergeOperation.INSERT:  # line 262
            output.extend(block.lines)  # line 263
        elif block.tipe == MergeBlockType.MODIFY:  # line 264
            if block.changes is not None and block.changes.tipe == MergeBlockType.INSERT:  # cannot be REMOVE, because it's always "-" then "+"  # line 265
                output.extend(block.lines if mergeOperation & MergeOperation.INSERT else block.replaces.lines)  # TODO logic?  # line 266
            elif block.replaces.changes is not None and block.replaces.changes.tipe == MergeBlockType.REMOVE:  # line 267
                output.extend(block.lines if mergeOperation & MergeOperation.REMOVE else block.replaces.lines)  # line 268
            elif block.changes is not None and block.changes.tipe == MergeBlockType.MODIFY:  # always both sides modified, but may differ in markers  # line 269
                if conflictResolution == ConflictResolution.THEIRS:  # line 270
                    output.extend(block.replaces.lines)  # line 271
                elif conflictResolution == ConflictResolution.MINE:  # line 272
                    output.extend(block.lines)  # line 273
                elif conflictResolution == ConflictResolution.ASK:  # line 274
                    print(ajoin("THR ", block.replaces.lines, "\n"))  # line 275
                    print(ajoin("MIN ", block.lines, "\n"))  # line 276
                    reso = {"i": ConflictResolution.MINE, "t": ConflictResolution.THEIRS, "m": ConflictResolution.NEXT, "u": None}.get(user_input(" Resolve: *M[I]ne, [T]heirs, [M]erge, [U]ser defined: ").strip().lower(), ConflictResolution.MINE)  # type: _coconut.typing.Optional[int]  # line 277
                    debug("User selected %d" % reso)  # line 278
                    _coconut_match_check = False  # line 279
                    _coconut_match_to = reso  # line 279
                    if _coconut_match_to is None:  # line 279
                        _coconut_match_check = True  # line 279
                    if _coconut_match_check:  # line 279
                        warn("Manual input not implemented yet")  # TODO allow multi-line input (CTRL+D?)  # line 280
                    _coconut_match_check = False  # line 281
                    _coconut_match_to = reso  # line 281
                    if _coconut_match_to == ConflictResolution.MINE:  # line 281
                        _coconut_match_check = True  # line 281
                    if _coconut_match_check:  # line 281
                        debug("Using mine")  # line 282
                        output.extend(block.lines)  # line 283
                    _coconut_match_check = False  # line 284
                    _coconut_match_to = reso  # line 284
                    if _coconut_match_to == ConflictResolution.THEIRS:  # line 284
                        _coconut_match_check = True  # line 284
                    if _coconut_match_check:  # line 284
                        debug("Using theirs")  # line 285
                        output.extend(block.replaces.lines)  # line 286
                    _coconut_match_check = False  # line 287
                    _coconut_match_to = reso  # line 287
                    if _coconut_match_to == ConflictResolution.NEXT:  # line 287
                        _coconut_match_check = True  # line 287
                    if _coconut_match_check:  # line 287
                        warn("Intra-line merge not implemented yet, skipping line(s)")  # line 288
                        output.extend(block.replaces.lines)  # line 289
            else:  # e.g. contains a deletion, but user was asking for insert only??  # line 290
                warn("Investigate this case")  # line 291
                output.extend(block.lines)  # default or not .replaces?  # line 292
    debug("Merge output: " + "; ".join(output))  # line 293
    nl = b"\n" if othreol is None else othreol if curreol is None else curreol  # type: bytes  # line 294
    return _coconut_tail_call(nl.join, [line.encode(encoding) for line in output])  # line 295
# TODO handle check for more/less lines in found -/+ blocks to find common section and splitting prefix/suffix out


class Counter:  # line 299
    def __init__(_, initial: 'Number'=0) -> 'None':  # line 300
        _.value = initial  # type: Number  # line 300
    def inc(_, by=1) -> 'Number':  # line 301
        _.value += by  # line 301
        return _.value  # line 301
    def inc_old(_, by=1) -> 'Number':  # line 302
        old = _.value  # line 302
        _.value += by  # line 302
        return old  # line 302

class Logger:  # line 304
    ''' Logger that supports many items. '''  # line 305
    def __init__(_, log):  # line 306
        _._log = log  # line 306
    def debug(_, *s):  # line 307
        _._log.debug(sjoin(*s))  # line 307
    def info(_, *s):  # line 308
        _._log.info(sjoin(*s))  # line 308
    def warn(_, *s):  # line 309
        _._log.warning(sjoin(*s))  # line 309
    def error(_, *s):  # line 310
        _._log.error(sjoin(*s))  # line 310


# Main data class
#@runtime_validation
class Metadata:  # line 315
    ''' This class doesn't represent the entire repository state in memory,
      but serves as a container for different repo operations,
      using only parts of its attributes at any point in time. Use with care.
  '''  # line 319

    def __init__(_, path: 'str') -> 'None':  # line 321
        ''' Create empty container object for various repository operations. '''  # line 322
        _.c = loadConfig()  # line 323
        _.root = path  # type: str  # line 324
        _.branches = {}  # type: Dict[int, BranchInfo]  # branch number zero represents the initial state at branching  # line 325
        _.commits = {}  # type: Dict[int, CommitInfo]  # consecutive numbers per branch, starting at 0  # line 326
        _.paths = {}  # type: Dict[str, PathInfo]  # utf-8 encoded relative, normalized file system paths  # line 327
        _.track = _.c.track  # type: bool  # track files in the repository (tracked patterns are stored for each branch separately)  # line 328
        _.picky = _.c.picky  # type: bool  # pick files on each operation  # line 329
        _.strict = _.c.strict  # type: bool  # be always strict (regarding file contents comparsion)  # line 330
        _.compress = _.c.compress  # type: bool  # these flags are stored per branch, therefor not part of the (default) configuration  # line 331
        _.branch = None  # type: _coconut.typing.Optional[int]  # current branch number  # line 332
        _.commit = None  # type: _coconut.typing.Optional[int]  # current revision number  # line 333

    def isTextType(_, filename: 'str') -> 'bool':  # line 335
        return (((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(mimetypes.guess_type(filename)[0])).startswith("text/") or any([fnmatch.fnmatch(filename, pattern) for pattern in _.c.texttype])) and not any([fnmatch.fnmatch(filename, pattern) for pattern in _.c.bintype])  # line 335

    def listChanges(_, changes: 'ChangeSet', diffmode: 'bool'=False, textglobs: '_coconut.typing.Sequence[str]'=[]) -> 'None':  # line 337
        ''' In diffmode, don't list modified files, because the diff is displayed elsewhere. '''  # line 338
        if len(changes.additions) > 0:  # line 339
            print(ajoin("ADD ", sorted(changes.additions.keys()), "\n"))  # line 339
        if len(changes.deletions) > 0:  # line 340
            print(ajoin("DEL ", sorted(changes.deletions.keys()), "\n"))  # line 340
        if len(changes.modifications) > 0:  # only list binary files  # line 341
            print(ajoin("MOD ", sorted((k for k in changes.modifications.keys() if not _.isTextType(k) or not diffmode)), "\n"))  # only list binary files  # line 341

    def loadBranches(_) -> 'None':  # line 343
        ''' Load list of branches and current branch info from metadata file. '''  # line 344
        try:  # fails if not yet created (on initial branch/commit)  # line 345
            branches = None  # type: List[Tuple]  # line 346
            with codecs.open(os.path.join(_.root, metaFolder, metaFile), "r", encoding=UTF8) as fd:  # line 347
                flags, branches = json.load(fd)  # line 348
            _.branch = flags["branch"]  # line 349
            _.track = flags["track"]  # line 350
            _.picky = flags["picky"]  # line 351
            _.strict = flags["strict"]  # line 352
            _.branches = {i.number: i for i in (BranchInfo(*item) for item in branches)}  # re-create type info  # line 353
        except Exception as E:  # if not found, create metadata folder  # line 354
            _.branches = {}  # line 355
            warn("Couldn't read branches metadata: %r" % E)  # line 356

    def saveBranches(_) -> 'None':  # line 358
        ''' Save list of branches and current branch info to metadata file. '''  # line 359
        with codecs.open(os.path.join(_.root, metaFolder, metaFile), "w", encoding=UTF8) as fd:  # line 360
            json.dump(({"branch": _.branch, "track": _.track, "picky": _.picky, "strict": _.strict, "compress": _.compress}, list(_.branches.values())), fd, ensure_ascii=False)  # line 361

    def getBranchByName(_, name: 'Union[str, int]') -> '_coconut.typing.Optional[int]':  # line 363
        ''' Convenience accessor for named branches. '''  # line 364
        if isinstance(name, int):  # if type(name) is int: return name  # line 365
            return name  # if type(name) is int: return name  # line 365
        try:  # attempt to parse integer string  # line 366
            return int(name)  # attempt to parse integer string  # line 366
        except ValueError:  # line 367
            pass  # line 367
        found = [number for number, branch in _.branches.items() if name == branch.name]  # line 368
        return found[0] if found else None  # line 369

    def loadBranch(_, branch: 'int') -> 'None':  # line 371
        ''' Load all commit information from a branch meta data file. '''  # line 372
        with codecs.open(os.path.join(_.root, metaFolder, "b%d" % branch, metaFile), "r", encoding=UTF8) as fd:  # line 373
            commits = json.load(fd)  # type: List[List[Any]]  # list of CommitInfo that needs to be unmarshalled into value types  # line 374
        _.commits = {i.number: i for i in (CommitInfo(*item) for item in commits)}  # re-create type info  # line 375
        _.branch = branch  # line 376

    def saveBranch(_, branch: 'int') -> 'None':  # line 378
        ''' Save all commit information to a branch meta data file. '''  # line 379
        with codecs.open(os.path.join(_.root, metaFolder, "b%d" % branch, metaFile), "w", encoding=UTF8) as fd:  # line 380
            json.dump(list(_.commits.values()), fd, ensure_ascii=False)  # line 381

    def duplicateBranch(_, branch: 'int', name: '_coconut.typing.Optional[str]') -> 'None':  # line 383
        ''' Create branch from an existing branch/revision. WARN: Caller must have loaded branches information.
        branch: target branch (should not exist yet)
        name: optional name of new branch
        _.branch: current branch
    '''  # line 388
        debug("Duplicating branch '%s' to '%d'..." % ((lambda _coconut_none_coalesce_item: "b%d" % _.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(_.branches[_.branch].name), branch))  # line 389
        tracked = [t for t in _.branches[_.branch].tracked]  # copy  # line 390
        os.makedirs(os.path.join(_.root, metaFolder, "b%d" % branch, "r0"))  # line 391
        _.loadBranch(_.branch)  # line 392
        revision = max(_.commits)  # type: int  # line 393
        _.computeSequentialPathSet(_.branch, revision)  # full set of files in revision to _.paths  # line 394
        for path, pinfo in _.paths.items():  # line 395
            _.copyVersionedFile(_.branch, revision, branch, 0, pinfo)  # line 396
        _.commits = {0: CommitInfo(0, int(time.time() * 1000), "Branched from '%s'" % ((lambda _coconut_none_coalesce_item: "b%d" % _.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(_.branches[_.branch].name)))}  # store initial commit  # line 397
        _.saveBranch(branch)  # save branch meta data to branch folder  # line 398
        _.saveCommit(branch, 0)  # save commit meta data to revision folder  # line 399
        _.branches[branch] = BranchInfo(branch, _.commits[0].ctime, name, _.branches[_.branch].insync, tracked)  # save branch info, before storing repo state at caller  # line 400

    def createBranch(_, branch: 'int', name: '_coconut.typing.Optional[str]'=None, initialMessage: '_coconut.typing.Optional[str]'=None):  # line 402
        ''' Create a new branch from current file tree. This clears all known commits and modifies the file system.
        branch: target branch (should not exist yet)
        name: optional name of new branch
        _.branch: current branch, must exist already
    '''  # line 407
        simpleMode = not (_.track or _.picky)  # line 408
        tracked = [t for t in _.branches[_.branch].tracked] if _.track and len(_.branches) > 0 else []  # in case of initial branch creation  # line 409
        debug((lambda _coconut_none_coalesce_item: "b%d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)("Creating branch '%s'..." % name))  # line 410
        _.paths = {}  # type: Dict[str, PathInfo]  # line 411
        if simpleMode:  # line 412
            changes = _.findChanges(branch, 0, progress=simpleMode)  # type: ChangeSet  # creates revision folder and versioned files  # line 413
            _.listChanges(changes)  # line 414
            _.paths.update(changes.additions.items())  # line 415
        else:  # tracking or picky mode  # line 416
            os.makedirs(os.path.join(_.root, metaFolder, "b%d" % branch, "r0"))  # line 417
            if _.branch is not None:  # not immediately after "offline" - copy files from current branch  # line 418
                _.loadBranch(_.branch)  # line 419
                revision = max(_.commits)  # type: int  # TODO what if last switch was to an earlier revision? no persisting of last checkout  # line 420
                _.computeSequentialPathSet(_.branch, revision)  # full set of files in revision to _.paths  # line 421
                for path, pinfo in _.paths.items():  # line 422
                    _.copyVersionedFile(_.branch, revision, branch, 0, pinfo)  # line 423
        ts = int(time.time() * 1000)  # line 424
        _.commits = {0: CommitInfo(0, ts, "Branched on %s" % strftime(ts) if initialMessage is None else initialMessage)}  # store initial commit for new branch  # line 425
        _.saveBranch(branch)  # save branch meta data (revisions) to branch folder  # line 426
        _.saveCommit(branch, 0)  # save commit meta data to revision folder  # line 427
        _.branches[branch] = BranchInfo(branch, _.commits[0].ctime, name, True if len(_.branches) == 0 else _.branches[_.branch].insync, tracked)  # save branch info, in case it is needed  # line 428

    def removeBranch(_, branch: 'int') -> 'BranchInfo':  # line 430
        ''' Entirely remove a branch and all its revisions from the file system. '''  # line 431
        shutil.rmtree(os.path.join(_.root, metaFolder, "b%d" % branch))  # line 432
        binfo = _.branches[branch]  # line 433
        del _.branches[branch]  # line 434
        _.branch = max(_.branches)  # line 435
        _.saveBranches()  # line 436
        _.commits.clear()  # line 437
        return binfo  # line 438

    def loadCommit(_, branch: 'int', revision: 'int') -> 'None':  # line 440
        ''' Load all file information from a commit meta data. '''  # line 441
        with codecs.open(os.path.join(_.root, metaFolder, "b%d" % branch, "r%d" % revision, metaFile), "r", encoding=UTF8) as fd:  # line 442
            _.paths = json.load(fd)  # line 443
        _.paths = {path: PathInfo(*item) for path, item in _.paths.items()}  # re-create type info  # line 444
        _.branch = branch  # line 445

    def saveCommit(_, branch: 'int', revision: 'int'):  # line 447
        ''' Save all file information to a commit meta data file. '''  # line 448
        target = os.path.join(_.root, metaFolder, "b%d" % branch, "r%d" % revision)  # line 449
        try:  # line 450
            os.makedirs(target)  # line 450
        except:  # line 451
            pass  # line 451
        with codecs.open(os.path.join(target, metaFile), "w", encoding=UTF8) as fd:  # line 452
            json.dump(_.paths, fd, ensure_ascii=False)  # line 453

    def findChanges(_, branch: '_coconut.typing.Optional[int]'=None, revision: '_coconut.typing.Optional[int]'=None, checkContent: 'bool'=False, inverse: 'bool'=False, considerOnly: '_coconut.typing.Optional[FrozenSet[str]]'=None, progress: 'bool'=False) -> 'ChangeSet':  # line 455
        ''' Find changes on the file system vs. in-memory paths (which should reflect the latest commit state).
        Only if both branch and revision are *not* None, write modified/added files to the specified revision folder (thus creating a new revision)
        The function returns the state of file tree *differences*, unless "inverse" is True -> then return original data
        checkContent: also computes file content hashes
        inverse: retain original state (size, mtime, hash) instead of updated one
        considerOnly: set of tracking patterns. For update operation, union of other and current branch
        progress: Show file names during processing
    '''  # line 463
        write = branch is not None and revision is not None  # line 464
        if write:  # line 465
            os.makedirs(os.path.join(_.root, metaFolder, "b%d" % branch, "r%d" % revision))  # line 465
        changes = ChangeSet({}, {}, {})  # type: ChangeSet  # line 466
        counter = 0  # line 467
        timer = time.time()  # line 467
        for path, dirnames, filenames in os.walk(_.root):  # line 468
            dirnames[:] = [f for f in dirnames if len([n for n in _.c.ignoreDirs if fnmatch.fnmatch(f, n)]) == 0 or len([p for p in _.c.ignoreDirsWhitelist if fnmatch.fnmatch(f, p)]) > 0]  # line 469
            filenames[:] = [f for f in filenames if len([n for n in _.c.ignores if fnmatch.fnmatch(f, n)]) == 0 or len([p for p in _.c.ignoresWhitelist if fnmatch.fnmatch(f, p)]) > 0]  # line 470
            dirnames.sort()  # line 471
            filenames.sort()  # line 471
            relpath = os.path.relpath(path, _.root).replace(os.sep, "/")  # line 472
            for file in (filenames if considerOnly is None else list(reduce(lambda last, pattern: last | set(fnmatch.filter(filenames, os.path.basename(pattern))), (p for p in considerOnly if os.path.dirname(p) == relpath), _coconut.set()))):  # if m.track or m.picky: only files that match any path-relevant tracking patterns  # line 473
                filename = relpath + "/" + file  # line 474
                filepath = os.path.join(path, file)  # line 475
                stat = os.stat(filepath)  # line 476
                size, mtime, newtime = stat.st_size, int(stat.st_mtime * 1000), time.time()  # line 477
                if progress and newtime - timer > .1:  # line 478
                    outstring = "\r%s  %s" % (PROGRESS_MARKER[counter % 4], filename)  # line 479
                    sys.stdout.write(outstring + " " * max(0, 80 - len(outstring)))  # TODO could write to new line instead of carriage return, also needs terminal width  # line 480
                    counter += 1  # TODO could write to new line instead of carriage return, also needs terminal width  # line 480
                    timer = newtime  # TODO could write to new line instead of carriage return, also needs terminal width  # line 480
                if filename not in _.paths:  # detected file not present (or untracked) in other branch  # line 481
                    namehash = hashStr(filename)  # line 482
                    changes.additions[filename] = PathInfo(namehash, size, mtime, hashFile(filepath, _.compress, saveTo=os.path.join(_.root, metaFolder, "b%d" % branch, "r%d" % revision, namehash) if write else None) if size > 0 else None)  # line 483
                    continue  # line 484
                last = _.paths[filename]  # filename is known  # line 485
                if last.size is None:  # was removed before but is now added back - does not apply for tracking mode (which never marks files for removal in the history)  # line 486
                    changes.additions[filename] = PathInfo(last.namehash, size, mtime, hashFile(filepath, _.compress, saveTo=os.path.join(_.root, metaFolder, "b%d" % branch, "r%d" % revision, last.namehash) if write else None) if size > 0 else None)  # line 487
                    continue  # line 487
                elif size != last.size or mtime != last.mtime or (checkContent and hashFile(filepath, _.compress) == last.hash):  # detected a modification  # line 488
                    changes.modifications[filename] = PathInfo(last.namehash, last.size if inverse else size, last.mtime if inverse else mtime, last.hash if inverse else hashFile(filepath, _.compress, saveTo=os.path.join(_.root, metaFolder, "b%d" % branch, "r%d" % revision, last.namehash) if write else None) if (last.size if inverse else size) > 0 else None)  # line 489
# Detect deletions. Files no longer being tracked should not be found here
            for folderPath in (p for p, pinfo in _.paths.items() if p[:p.rindex("/")] == relpath and pinfo.size is not None):  # only versioned (and tracked) files that match currently visited folder. TODO don't check for removal just added entries  # line 491
                if folderPath[len(relpath) + 1:] not in filenames:  # filename no longer in file tree TODO use basename and dirname instead of slicing?  # line 492
                    changes.deletions[folderPath] = _.paths[folderPath]  # filename no longer in file tree TODO use basename and dirname instead of slicing?  # line 492
        return changes  # line 493

    def integrateChangeset(_, changes: 'ChangeSet', clear=False) -> 'None':  # line 495
        ''' In-memory update from a changeset, marking deleted files with size=None. Use clear = True to start on an empty path set. '''  # line 496
        if clear:  # line 497
            _.paths.clear()  # line 497
        else:  # line 498
            rm = [p for p, info in _.paths.items() if info.size is None]  # remove files deleted in earlier change sets (revisions)  # line 499
            for old in rm:  # remove previously removed entries completely  # line 500
                del _.paths[old]  # remove previously removed entries completely  # line 500
        for d, info in changes.deletions.items():  # mark now removed entries as deleted  # line 501
            _.paths[d] = PathInfo(info.namehash, None, info.mtime, None)  # mark now removed entries as deleted  # line 501
        _.paths.update(changes.additions)  # line 502
        _.paths.update(changes.modifications)  # line 503

    def computeSequentialPathSet(_, branch: 'int', revision: 'int') -> 'None':  # line 505
        ''' In-memory computation of current list of valid PathInfo entries for specified branch and until specified revision (inclusively) by traversing revision on the file system. '''  # line 506
        _.loadCommit(branch, 0)  # load initial paths  # line 507
        n = Metadata(_.root)  # type: Metadata  # next changes  # line 508
        for revision in range(1, revision + 1):  # line 509
            n.loadCommit(branch, revision)  # line 510
            changes = diffPathSets(_.paths, n.paths)  # type: ChangeSet  # line 511
            _.integrateChangeset(changes)  # line 512

    def parseRevisionString(_, argument: 'str') -> 'Tuple[_coconut.typing.Optional[int], _coconut.typing.Optional[int]]':  # line 514
        ''' Commit identifiers can be str or int for branch, and int for revision.
        Revision identifiers can be negative, with -1 being last commit.
    '''  # line 517
        if argument is None:  # no branch/revision specified  # line 518
            return (_.branch, -1)  # no branch/revision specified  # line 518
        argument = argument.strip()  # line 519
        if argument.startswith("/"):  # current branch  # line 520
            return (_.branch, int(argument[1:]))  # current branch  # line 520
        if argument.endswith("/"):  # line 521
            try:  # line 522
                return (_.getBranchByName(argument[:-1]), -1)  # line 522
            except ValueError:  # line 523
                Exit("Unknown branch label")  # line 523
        if "/" in argument:  # line 524
            b, r = argument.split("/")[:2]  # line 525
            try:  # line 526
                return (_.getBranchByName(b), int(r))  # line 526
            except ValueError:  # line 527
                Exit("Unknown branch label or wrong number format")  # line 527
        branch = _.getBranchByName(argument)  # type: int  # returns number if given (revision) integer  # line 528
        if branch not in _.branches:  # line 529
            branch = None  # line 529
        try:  # either branch name/number or reverse/absolute revision number  # line 530
            return (_.branch if branch is None else branch, int(argument) if branch is None else -1)  # either branch name/number or reverse/absolute revision number  # line 530
        except:  # line 531
            Exit("Unknown branch label or wrong number format")  # line 531
        return (None, None)  # should never be reached TODO raise exception instead?  # line 532

    def copyVersionedFile(_, branch: 'int', revision: 'int', tobranch: 'int', torevision: 'int', pinfo: 'PathInfo') -> 'None':  # line 534
        ''' Copy versioned file to other branch/revision. '''  # line 535
        target = os.path.join(_.root, metaFolder, "b%d" % tobranch, "r%d" % torevision, pinfo.namehash)  # type: str  # line 536
        while True:  # line 537
            source = os.path.join(_.root, metaFolder, "b%d" % branch, "r%d" % revision, pinfo.namehash)  # type: str  # line 538
            if os.path.exists(source):  # line 539
                break  # line 539
            revision -= 1  # line 540
            if revision < 0:  # should never happen  # line 541
                Exit("Cannot copy file '%s' from 'b%d/r%d' to 'b%d/r%d" % (pinfo.namehash, branch, revision, tobranch, torevision))  # should never happen  # line 541
        shutil.copy2(source, target)  # line 542

    def readOrCopyVersionedFile(_, branch: 'int', revision: 'int', namehash: 'str', toFile: '_coconut.typing.Optional[str]'=None) -> '_coconut.typing.Optional[bytes]':  # line 544
        ''' Return file contents, or copy contents into file path provided. '''  # line 545
        source = os.path.join(_.root, metaFolder, "b%d" % branch, "r%d" % revision, namehash)  # type: str  # line 546
        try:  # line 547
            with openIt(source, "r", _.compress) as fd:  # line 548
                if toFile is None:  # read bytes into memory and return  # line 549
                    return fd.read()  # read bytes into memory and return  # line 549
                with open(toFile, "wb") as to:  # line 550
                    while True:  # line 551
                        buffer = fd.read(bufSize)  # line 552
                        to.write(buffer)  # line 553
                        if len(buffer) < bufSize:  # line 554
                            break  # line 554
                    return None  # line 555
        except Exception as E:  # line 556
            warn("Cannot read versioned file: %r (%d/%d/%s)" % (E, branch, revision, namehash))  # line 556
        return None  # line 557

    def restoreFile(_, relpath: '_coconut.typing.Optional[str]', branch: 'int', revision: 'int', pinfo: 'PathInfo') -> '_coconut.typing.Optional[bytes]':  # line 559
        ''' Recreate file for given revision, or return contents if path is None. '''  # line 560
        if relpath is None:  # just return contents as split decoded lines  # line 561
            return _.readOrCopyVersionedFile(branch, revision, pinfo.namehash) if pinfo.size > 0 else b''  # just return contents as split decoded lines  # line 561
        target = os.path.join(_.root, relpath.replace("/", os.sep))  # type: str  # line 562
        if pinfo.size == 0:  # line 563
            with open(target, "wb"):  # line 564
                pass  # line 564
            try:  # update access/modification timestamps on file system  # line 565
                os.utime(target, (-1, pinfo.mtime / 1000.))  # update access/modification timestamps on file system  # line 565
            except Exception as E:  # line 566
                error("Cannot update file's timestamp after restoration '%r'" % E)  # line 566
            return None  # line 567
        while True:  # find latest revision that contained the file physically  # line 568
            source = os.path.join(_.root, metaFolder, "b%d" % branch, "r%d" % revision, pinfo.namehash)  # type: str  # line 569
            if os.path.exists(source):  # line 570
                break  # line 570
            revision -= 1  # line 571
            if revision < 0:  # line 572
                Exit("Cannot restore file '%s' from specified branch '%d'" % (pinfo.namehash, branch))  # line 572
# Restore file by copying buffer-wise
        with openIt(source, "r", _.compress) as fd, open(target, "wb") as to:  # using Coconut's Enhanced Parenthetical Continuation  # line 574
            while True:  # line 575
                buffer = fd.read(bufSize)  # line 576
                to.write(buffer)  # line 577
                if len(buffer) < bufSize:  # line 578
                    break  # line 578
        try:  # update access/modification timestamps on file system  # line 579
            os.utime(target, (-1, pinfo.mtime / 1000.))  # update access/modification timestamps on file system  # line 579
        except Exception as E:  # line 580
            error("Cannot update file's timestamp after restoration '%r'" % E)  # line 580
        return None  # line 581

    def getTrackingPatterns(_, branch: '_coconut.typing.Optional[int]'=None) -> 'FrozenSet[str]':  # line 583
        ''' Returns list of tracking patterns for provided branch or current branch. '''  # line 584
        return _coconut.frozenset() if not _.track and not _.picky else frozenset(_.branches[_.branch if branch is None else branch].tracked)  # line 585


# Main client operations
def offline(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]) -> 'None':  # line 589
    ''' Initial command to start working offline. '''  # line 590
    if '--force' not in options and os.path.exists(metaFolder):  # line 591
        Exit("Repository folder is either already offline or older branches and commits were left over. Use 'sos online' or continue working offline")  # line 592
    m = Metadata(os.getcwd())  # type: Metadata  # line 593
    if '--picky' in options or m.c["picky"]:  # Git-like  # line 594
        m.picky = True  # Git-like  # line 594
    elif '--track' in options or m.c["track"]:  # Svn-like  # line 595
        m.track = True  # Svn-like  # line 595
    if '--strict' in options or m.c["strict"]:  # always hash contents  # line 596
        m.strict = True  # always hash contents  # line 596
    debug("Preparing offline repository...")  # line 597
    m.createBranch(0, str(m.c["defaultbranch"]) if argument is None else argument, initialMessage="Offline repository created on %s" % strftime())  # main branch's name may be None (e.g. for fossil)  # line 598
    m.branch = 0  # line 599
    m.saveBranches()  # no change immediately after going offline, going back online won't issue a warning  # line 600
    info("Offline repository prepared. Use 'sos online' to finish offline work")  # line 601

def online(options: '_coconut.typing.Sequence[str]'=[]) -> 'None':  # line 603
    ''' Finish working offline. '''  # line 604
    force = '--force' in options  # type: bool  # line 605
    if not force:  # line 606
        m = Metadata(os.getcwd())  # line 607
        m.loadBranches()  # line 608
        if any([not b.insync for b in m.branches.values()]) and not force:  # line 609
            Exit("There are still unsynchronized branches.\nUse 'log' to list them. Commit them to your VCS one by one with 'sos commit' and 'sos switch' before leaving offline mode. Use 'online --force' to erase all aggregated offline revisions.")  # line 609
    try:  # line 610
        shutil.rmtree(metaFolder)  # line 610
        info("Left offline modus. Continue work with your online VCS.")  # line 610
    except Exception as E:  # line 611
        Exit("Error removing offline repository: %r" % E)  # line 611

def branch(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]) -> 'None':  # line 613
    ''' Create a new branch (from file tree or last revision) and (by default) continue working on it. '''  # line 614
    last = '--last' in options  # type: bool  # use last revision for branching, not current file tree  # line 615
    stay = '--stay' in options  # type: bool  # continue on current branch after branching  # line 616
    force = '--force' in options  # type: bool  # branch even with local modifications  # line 617
    m = Metadata(os.getcwd())  # type: Metadata  # line 618
    m.loadBranches()  # line 619
    if argument and m.getBranchByName(argument) is not None:  # create a named branch  # line 620
        Exit("Branch '%s' already exists. Cannot proceed" % argument)  # create a named branch  # line 620
    branch = max(m.branches.keys()) + 1  # next branch's key  # line 621
    debug("Branching to %sbranch b%d%s%s..." % ("unnamed " if argument is None else "", branch, " '%s'" % argument if argument else "", " from last revision" if last else ""))  # line 622
    if last:  # line 623
        m.duplicateBranch(branch, argument)  # branch from branch's last revision  # line 624
    else:  # from file tree state  # line 625
        m.createBranch(branch, argument)  # branch from current file tree  # line 626
    if not stay:  # line 627
        m.branch = branch  # line 628
        m.saveBranches()  # line 629
    info("%s new %sbranch b%d%s" % ("Continue work after branching" if stay else "Switched to", "unnamed " if argument is None else "", branch, " '%s'" % argument if argument else ""))  # line 630

def changes(argument: 'str'=None, options: '_coconut.typing.Sequence[str]'=[]) -> 'ChangeSet':  # line 632
    ''' Show changes of file tree vs. (last or specified) revision on current or specified branch. '''  # line 633
    m = Metadata(os.getcwd())  # type: Metadata  # line 634
    branch = None  # type: _coconut.typing.Optional[int]  # line 634
    revision = None  # type: _coconut.typing.Optional[int]  # line 634
    m.loadBranches()  # knows current branch  # line 635
    strict = '--strict' in options or m.strict  # type: bool  # line 636
    branch, revision = m.parseRevisionString(argument)  # line 637
    if branch not in m.branches:  # line 638
        Exit("Unknown branch")  # line 638
    m.loadBranch(branch)  # knows commits  # line 639
    revision = revision if revision >= 0 else len(m.commits) + revision  # negative indexing  # line 640
    if revision < 0 or revision > max(m.commits):  # line 641
        Exit("Unknown revision r%d" % revision)  # line 641
    debug("Checking file tree vs. commit '%s/r%d'..." % ((lambda _coconut_none_coalesce_item: "b%d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 642
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision  # line 643
    changes = m.findChanges(checkContent=strict, considerOnly=None if not m.track else m.getTrackingPatterns() | m.getTrackingPatterns(branch))  # type: ChangeSet  # line 644
    m.listChanges(changes)  # line 645
    return changes  # line 646

def diff(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]) -> 'None':  # line 648
    ''' Show text file differences of file tree vs. (last or specified) revision on current or specified branch. '''  # line 649
    m = Metadata(os.getcwd())  # type: Metadata  # line 650
    branch = None  # type: _coconut.typing.Optional[int]  # line 650
    revision = None  # type: _coconut.typing.Optional[int]  # line 650
    m.loadBranches()  # knows current branch  # line 651
    strict = '--strict' in options or m.strict  # type: bool  # line 652
    branch, revision = m.parseRevisionString(argument)  # line 653
    if branch not in m.branches:  # line 654
        Exit("Unknown branch")  # line 654
    m.loadBranch(branch)  # knows commits  # line 655
    revision = revision if revision >= 0 else len(m.commits) + revision  # negative indexing  # line 656
    if revision < 0 or revision > max(m.commits):  # line 657
        Exit("Unknown revision r%d" % revision)  # line 657
    debug("Diffing file tree vs. commit '%s/r%d'..." % ((lambda _coconut_none_coalesce_item: "b%d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 658
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision  # line 659
    changes = m.findChanges(checkContent=strict, inverse=True, considerOnly=None if not m.track else m.getTrackingPatterns() | m.getTrackingPatterns(branch))  # type: ChangeSet  # line 660
    info("File changes:")  # line 661
    m.listChanges(changes, diffmode=True)  # only list modified binary files  # line 662

    info("Text file modifications:")  # TODO only text files, not binary  # line 664
    differ = difflib.Differ()  # line 665
    for path, pinfo in changes.modifications.items():  # only consider modified files TODO also show A/D here?  # line 666
        print("\nDIF " + path)  # line 667
        content = None  # type: _coconut.typing.Optional[bytes]  # line 668
        othr = None  # type: _coconut.typing.Sequence[str]  # line 668
        curr = None  # type: _coconut.typing.Sequence[str]  # line 668
        if pinfo.size == 0:  # line 669
            content = b""  # line 669
        else:  # line 670
            content = m.restoreFile(None, branch, revision, pinfo)  # line 670
            assert content is not None  # line 670
        abspath = os.path.join(m.root, path.replace("/", os.sep))  # line 671
        encoding, othreol, othr = detectAndLoad(content=content)  # line 672
        encoding, curreol, curr = detectAndLoad(filename=abspath)  # line 673
        currcount, othrcount = Counter(), Counter()  # TODO shows empty new line although none in file. also counting is messed up  # line 674
        last = ""  # line 675
        for no, line in enumerate(differ.compare(othr, curr)):  # line 676
            if line[0] == " ":  # no change in line  # line 677
                continue  # no change in line  # line 677
            print("%04d/%04d %s" % (no + othrcount.inc(-1 if line[0] == "+" or (line[0] == "?" and last == "+") else 0), no + currcount.inc(-1 if line[0] == "-" or (line[0] == "?" and last == "-") else 0), line))  # TODO counting this is definitely wrong and also lists \n as new diff lines. Could reuse block detection from merge instead  # line 678
            last = line[0]  # line 679

def commit(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]) -> 'None':  # line 681
    ''' Create new revision from file tree changes vs. last commit. '''  # line 682
    changes = None  # type: ChangeSet  # line 683
    m, branch, revision, changes, strict, force, trackingPatterns = stopOnChanges(None, options, commit=True)  # special flag creates new revision for detected changes, but abort if no changes  # line 684
    debug((lambda _coconut_none_coalesce_item: "b%d" % m.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)("Committing changes to branch '%s'..." % m.branches[m.branch].name))  # line 685
    m.integrateChangeset(changes, clear=True)  # update pathset to changeset only  # line 686
    m.saveCommit(m.branch, revision)  # revision has already been incremented  # line 687
    m.commits[revision] = CommitInfo(revision, int(time.time() * 1000), argument)  # comment can be None  # line 688
    m.saveBranch(m.branch)  # line 689
    if m.picky:  # line 690
        m.loadBranches()  # TODO is this necessary?  # line 691
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], tracked=[], insync=False)  # remove tracked patterns after commit in picky mode  # line 692
        m.saveBranches()  # line 693
    info("Created new revision r%2d%s (+%d/-%d/~%d)" % (revision, ((" '%s'" % argument) if argument is not None else ""), len(changes.additions), len(changes.deletions), len(changes.modifications)))  # line 694

def status() -> 'None':  # line 696
    ''' Show branches and current repository state. '''  # line 697
    m = Metadata(os.getcwd())  # type: Metadata  # line 698
    m.loadBranches()  # knows current branch  # line 699
    current = m.branch  # type: int  # line 700
    info("Offline repository status:")  # line 701
    sl = max([len((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(b.name)) for b in m.branches.values()])  # type: int  # line 702
    for branch in sorted(m.branches.values(), key=lambda b: b.number):  # line 703
        m.loadBranch(branch.number)  # knows commit history  # line 704
        print("  %s b%d%s @%s (%s) with %d commits%s" % ("*" if current == branch.number else " ", branch.number, ((" %%%ds" % (sl + 2)) % ("'%s'" % branch.name)) if branch.name else "", strftime(branch.ctime), "in sync" if branch.insync else "dirty", len(m.commits), ". Last comment: '%s'" % m.commits[max(m.commits)].message if m.commits[max(m.commits)].message else ""))  # line 705
    if m.track or m.picky and len(m.branches[m.branch].tracked) > 0:  # line 706
        info("\nTracked file patterns:")  # line 707
        print(ajoin("  | ", m.branches[m.branch].tracked, "\n"))  # line 708

def stopOnChanges(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[], check: 'bool'=True, commit: 'bool'=False) -> 'Tuple[Metadata, _coconut.typing.Optional[int], int, ChangeSet, bool, bool, FrozenSet[str]]':  # line 710
    ''' Common behavior for switch, update, delete, commit.
      check: stop program on detected change
      commit: don't stop on changes, because that's what we need in the operation
      Returns (Metadata, (current or target) branch, revision, set of changes vs. last commit on current branch, strict, force flags. '''  # line 714
    m = Metadata(os.getcwd())  # type: Metadata  # line 715
    m.loadBranches()  # knows current branch  # line 716
    trackingPatterns = m.getTrackingPatterns()  # type: FrozenSet[str]  # SVN-like mode  # line 717
    force = '--force' in options  # type: bool  # line 718
    strict = '--strict' in options or m.strict  # type: bool  # line 719
    if argument is not None:  # line 720
        branch, revision = m.parseRevisionString(argument)  # for early abort  # line 721
        if branch is None:  # line 722
            Exit("Branch '%s' doesn't exist. Cannot proceed" % argument)  # line 722
    m.loadBranch(m.branch)  # knows last commits of *current* branch  # line 723

# Determine current changes
    m.computeSequentialPathSet(m.branch, max(m.commits))  # load all commits up to specified revision  # line 726
    changes = m.findChanges(checkContent=strict, considerOnly=None if not m.track and not m.picky else trackingPatterns) if not commit else m.findChanges(m.branch, max(m.commits) + 1, checkContent=strict, considerOnly=None if not m.track and not m.picky else trackingPatterns)  # type: ChangeSet  # line 727
    if (changes.additions or changes.deletions or changes.modifications) and not force:  # and check?  # line 728
        m.listChanges(changes)  # line 729
        if check and not commit:  # line 730
            Exit("File tree contains changes. Use --force to proceed")  # line 730
    elif commit and not force:  #  and not check  # line 731
        Exit("Nothing to commit. Aborting")  #  and not check  # line 731

    if argument is not None:  # branch/revision specified  # line 733
        m.loadBranch(branch)  # knows commits of target branch  # line 734
        revision = revision if revision >= 0 else len(m.commits) + revision  # negative indexing  # line 735
        if revision < 0 or revision > max(m.commits):  # line 736
            Exit("Unknown revision r%2d" % revision)  # line 736
        return (m, branch, revision, changes, strict, force, m.getTrackingPatterns(branch))  # line 737
    return (m, m.branch, max(m.commits) + (1 if commit else 0), changes, strict, force, trackingPatterns)  # line 738

def switch(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]) -> 'None':  # line 740
    ''' Continue work on another branch, replacing file tree changes. '''  # line 741
    changes = None  # type: ChangeSet  # line 742
    m, branch, revision, changes, strict, force, trackingPatterns = stopOnChanges(argument, options)  # line 743
    debug("Switching to branch %sb%d/r%d..." % ("'%s' " % m.branches[branch].name if m.branches[branch].name else "", branch, revision))  # line 744

# Determine file changes from other branch to current file tree
    if '--meta' in options:  # only switch meta data  # line 747
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], tracked=m.branches[branch].tracked)  # line 748
    else:  # full file switch  # line 749
        m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision for target branch into memory  # line 750
        changes = m.findChanges(checkContent=strict, inverse=True, considerOnly=None if not m.track else trackingPatterns | m.getTrackingPatterns(branch))  # determine difference of other branch vs. file tree (forced or in sync with current branch; "addition" means exists now and should be removed)  # line 751
        if not (changes.additions or changes.deletions or changes.modifications):  # line 752
            info("No changes to current file tree")  # line 753
        else:  # integration required  # line 754
            for path, pinfo in changes.deletions.items():  # line 755
                m.restoreFile(path, branch, revision, pinfo)  # is deleted in current file tree: restore from branch to reach target  # line 756
                debug("ADD " + path)  # line 757
            for path, pinfo in changes.additions.items():  # line 758
                os.unlink(os.path.join(m.root, path.replace("/", os.sep)))  # is added in current file tree: remove from branch to reach target  # line 759
                debug("DEL " + path)  # line 760
            for path, pinfo in changes.modifications.items():  # line 761
                m.restoreFile(path, branch, revision, pinfo)  # is modified in current file tree: restore from branch to reach target  # line 762
                debug("MOD " + path)  # line 763
    m.branch = branch  # line 764
    m.saveBranches()  # store switched path info  # line 765
    info("Switched to branch %sb%d/r%d" % ("'%s' " % (m.branches[branch].name if m.branches[branch].name else ""), branch, revision))  # line 766

def update(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]) -> 'None':  # line 768
    ''' Load and integrate a specified other branch/revision into current life file tree.
      In tracking mode, this also updates the set of tracked patterns.
      User options for merge operation: --add (don't remove), --rm (don't insert), --add-lines/--rm-lines (inside each file)
      User options for conflict resolution: --theirs/--mine/--ask
  '''  # line 773
    mrg = firstOfMap({"--add": MergeOperation.INSERT, "--rm": MergeOperation.REMOVE}, options, MergeOperation.BOTH)  # type: int  # default operation is replicate remove state for non-conflicting cases (insertions/deletions)  # line 774
    res = firstOfMap({'--theirs': ConflictResolution.THEIRS, '--mine': ConflictResolution.MINE}, options, ConflictResolution.NEXT)  # type: int  # NEXT means deeper level  # line 775
    mrgline = firstOfMap({'--add-lines': MergeOperation.INSERT, '--rm-lines': MergeOperation.REMOVE}, options, mrg)  # type: int  # default operation for modified files is same as for files  # line 776
    resline = firstOfMap({'--theirs-lines': ConflictResolution.THEIRS, '--mine-lines': ConflictResolution.MINE}, options, ConflictResolution.ASK)  # type: int  # line 777
    m = Metadata(os.getcwd())  # type: Metadata  # TODO same is called inside stop on changes - could return both current and designated branch instead  # line 778
    m.loadBranches()  # line 779
    changes = None  # type: ChangeSet  # line 779
    currentBranch = m.branch  # type: _coconut.typing.Optional[int]  # line 780
    m, branch, revision, changes, strict, force, trackingPatterns = stopOnChanges(argument, options, check=False)  # don't check for current changes, only parse arguments  # line 781
    debug("Integrating changes from '%s/r%d' into file tree..." % ((lambda _coconut_none_coalesce_item: "b%d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 782

# Determine file changes from other branch over current file tree
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision for branch to integrate  # line 785
    trackingUnion = trackingPatterns | m.getTrackingPatterns(branch)  # type: FrozenSet[str]  # line 786
    changes = m.findChanges(checkContent=strict, inverse=True, considerOnly=None if not m.track else trackingUnion)  # determine difference of other branch vs. file tree. "addition" means exists now but not in other, and should be removed unless in tracking mode  # line 787
    if not (mrg & MergeOperation.INSERT and changes.additions or (mrg & MergeOperation.REMOVE and changes.deletions) or changes.modifications):  # line 788
        if trackingUnion == trackingPatterns:  # nothing added  # line 789
            info("No file changes detected, but tracking patterns were merged (run 'sos switch /-1 --meta' to undo)")  # TODO write test to see if this works  # line 790
        else:  # line 791
            info("Nothing to update")  # but write back updated branch info below  # line 792
    else:  # integration required  # line 793
        for path, pinfo in changes.deletions.items():  # deletions mark files not present in current file tree -> needs additon  # line 794
            if mrg & MergeOperation.INSERT:  # deleted in current file tree: restore from branch to reach target  # line 795
                m.restoreFile(path, branch, revision, pinfo)  # deleted in current file tree: restore from branch to reach target  # line 795
            print("ADD " + path if mrg & MergeOperation.INSERT else "(A) " + path)  # line 796
        for path, pinfo in changes.additions.items():  # line 797
            if m.track or m.picky:  # because untracked files of other branch cannot be detected (which is good)  # line 798
                Exit("This should never happen")  # because untracked files of other branch cannot be detected (which is good)  # line 798
            if mrg & MergeOperation.REMOVE:  # line 799
                os.unlink(m.root + os.sep + path.replace("/", os.sep))  # line 799
            print("DEL " if mrg & MergeOperation.REMOVE else "(D) " + path)  # not contained in other branch, but maybe kept  # line 800
        for path, pinfo in changes.modifications.items():  # line 801
            into = os.path.join(m.root, path.replace("/", os.sep))  # type: str  # line 802
            binary = not m.isTextType(path)  # line 803
            if res & ConflictResolution.ASK or binary:  # line 804
                print(("MOD " if not binary else "BIN ") + path)  # line 805
                reso = {"i": ConflictResolution.MINE, "t": ConflictResolution.THEIRS, "m": ConflictResolution.NEXT}.get(user_input(" Resolve: *M[I]ne, [T]heirs, [M]erge: (I)").strip().lower(), ConflictResolution.MINE)  # line 806
                debug("User selected %d" % reso)  # line 807
            else:  # line 808
                reso = res  # line 808
            if reso & ConflictResolution.THEIRS:  # line 809
                m.readOrCopyVersionedFile(branch, revision, pinfo.namehash, into)  # blockwise copy of contents  # line 810
                print("THR " + path)  # line 811
            elif reso & ConflictResolution.MINE:  # line 812
                print("MNE " + path)  # nothing to do! same as skip  # line 813
            else:  # NEXT: line-based merge  # line 814
                file = m.readOrCopyVersionedFile(branch, revision, pinfo.namehash) if pinfo.size > 0 else b''  # type: str  # parse lines TODO decode etc.  # line 815
                if file is not None:  # if None, error message was already logged  # line 816
                    contents = merge(filename=file, intoname=into, mergeOperation=mrgline, conflictResolution=resline)  # type: bytes  # line 817
                    with open(path, "wb") as fd:  # TODO write to temp file first  # line 818
                        fd.write(contents)  # TODO write to temp file first  # line 818
    info("Integrated changes from '%s/r%d' into file tree" % ((lambda _coconut_none_coalesce_item: "b%d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 819
    m.branches[currentBranch] = dataCopy(BranchInfo, m.branches[currentBranch], insync=False, tracked=list(trackingUnion))  # TODO really? it's a change that cannot be undone easily by the user  # line 820
    m.branch = currentBranch  # need to restore setting before saving TODO operate on different objects instead  # line 821
    m.saveBranches()  # line 822

def delete(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]) -> 'None':  # line 824
    ''' Remove a branch entirely. '''  # line 825
    m, branch, revision, changes, strict, force, trackingPatterns = stopOnChanges(argument, options)  # line 826
    if len(m.branches) == 1:  # line 827
        Exit("Cannot remove the only remaining branch. Use 'sos online' to leave offline mode")  # line 827
    debug("Removing branch %d%s..." % (branch, " '%s'" % m.branches[branch].name if m.branches[branch].name else ""))  # line 828
    binfo = m.removeBranch(branch)  # need to keep a reference to removed entry for output below  # line 829
    info("Branch b%d%s removed" % (branch, " '%s'" % binfo.name if binfo.name else ""))  # line 830

def add(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]) -> 'None':  # line 832
    ''' Add a tracked files pattern to current branch's tracked files. '''  # line 833
    force = '--force' in options  # type: bool  # line 834
    m = Metadata(os.getcwd())  # type: Metadata  # line 835
    m.loadBranches()  # line 836
    if not m.track and not m.picky:  # line 837
        Exit("Repository is in simple mode. Needs 'offline --track' or 'offline --picky' instead")  # line 837
    relpath = os.path.relpath(os.path.dirname(os.path.abspath(argument)), m.root)  # for tracking list  # line 838
    pattern = os.path.join(relpath, os.path.basename(argument)).replace(os.sep, "/")  # line 839
    if pattern in m.branches[m.branch].tracked:  # line 840
        Exit("%s '%s' already tracked" % ("Glob" if isglob(pattern) else "File", pattern))  # line 841
    if not force and len(fnmatch.filter(os.listdir(os.path.abspath(relpath)), os.path.basename(pattern.replace("/", os.sep)))) == 0:  # doesn't match any current file  # line 842
        Exit("Pattern doesn't match any file in specified folder. Use --force to add it anyway")  # line 843
    m.branches[m.branch].tracked.append(pattern)  # TODO set insync flag to False? same for rm  # line 844
    m.saveBranches()  # line 845
    info("Added tracking pattern '%s' for folder '%s'" % (os.path.basename(pattern.replace("/", os.sep)), os.path.abspath(relpath)))  # line 846

def rm(argument: 'str') -> 'None':  # line 848
    ''' Remove a tracked files pattern from current branch's tracked files. '''  # line 849
    m = Metadata(os.getcwd())  # type: Metadata  # line 850
    m.loadBranches()  # line 851
    if not m.track and not m.picky:  # line 852
        Exit("Repository is in simple mode. Needs 'offline --track' or 'offline --picky' instead")  # line 852
    relpath = os.path.relpath(os.path.dirname(os.path.abspath(argument)), m.root)  # type: str  # line 853
    pattern = os.path.join(relpath, os.path.basename(argument)).replace(os.sep, "/")  # type: str  # line 854
    if pattern not in m.branches[m.branch].tracked:  # line 855
        suggestion = _coconut.set()  # type: Set[str]  # line 856
        for pat in m.branches[m.branch].tracked:  # line 857
            if fnmatch.fnmatch(pattern, pat):  # line 858
                suggestion.add(pat)  # line 858
        if suggestion:  # line 859
            print("Do you mean any of the following tracked globs? '%s'" % (", ".join(sorted(suggestion))))  # line 859
        Exit("Tracked pattern '%s' not found" % pattern)  # line 860
    m.branches[m.branch].tracked.remove(pattern)  # line 861
    m.saveBranches()  # line 862
    info("Removed tracking pattern '%s' for folder '%s'" % (os.path.basename(pattern.replace("/", os.sep)), os.path.abspath(relpath)))  # line 863

def ls(argument: '_coconut.typing.Optional[str]'=None) -> 'None':  # line 865
    ''' List specified directory, augmenting with repository metadata. '''  # line 866
    cwd = os.getcwd() if argument is None else argument  # type: str  # line 867
    m = Metadata(cwd)  # type: Metadata  # line 868
    m.loadBranches()  # line 869
    relpath = os.path.relpath(cwd, m.root).replace(os.sep, "/")  # type: str  # line 870
    files = list(sorted((entry for entry in os.listdir(cwd) if os.path.isfile(entry))))  # type: List[str]  # line 871
    trackingPatterns = m.getTrackingPatterns() if m.track or m.picky else _coconut.frozenset()  # type: FrozenSet[str]  # for current branch  # line 872
    for file in files:  # line 873
        ignore = None  # type: _coconut.typing.Optional[str]  # line 874
        for ig in m.c.ignores:  # line 875
            if fnmatch.fnmatch(file, ig):  # remember first match TODO document this  # line 876
                ignore = ig  # remember first match TODO document this  # line 876
                break  # remember first match TODO document this  # line 876
        if ig:  # line 877
            for wl in m.c.ignoresWhitelist:  # line 878
                if fnmatch.fnmatch(file, wl):  # found a white list entry for ignored file, undo ignoring it  # line 879
                    ignore = None  # found a white list entry for ignored file, undo ignoring it  # line 879
                    break  # found a white list entry for ignored file, undo ignoring it  # line 879
        if ignore is None:  # line 880
            matches = []  # type: List[str]  # line 881
            for pattern in (p for p in trackingPatterns if os.path.dirname(p) == relpath):  # only patterns matching current folder  # line 882
                if fnmatch.fnmatch(file, os.path.basename(pattern)):  # TODO or only file basename?  # line 883
                    matches.append(pattern)  # TODO or only file basename?  # line 883
        print("%s %s%s" % ("IGN" if ignore is not None else ("TRK" if len(matches) > 0 else "   "), file, ' by "%s"' % ignore if ignore is not None else (" by " + ";".join(['"%s"' % match for match in matches]) if len(matches) > 0 else "")))  # line 884

def log() -> 'None':  # line 886
    ''' List previous commits on current branch. '''  # TODO --verbose for changesets  # line 887
    m = Metadata(os.getcwd())  # type: Metadata  # line 888
    m.loadBranches()  # knows current branch  # line 889
    m.loadBranch(m.branch)  # knows commit history  # line 890
    info((lambda _coconut_none_coalesce_item: "r%2d" % m.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)("Offline commit history of branch '%s':" % m.branches[m.branch].name))  # TODO also retain "from branch/revision" on branching?  # line 891
    nl = len("%d" % max(m.commits))  # determine space needed for revision  # line 892
    for commit in sorted(m.commits.values(), key=lambda co: co.number):  # line 893
        print("  %s r%s @%s: %s" % ("*" if commit.number == max(m.commits) else " ", ("%%%ds" % nl) % commit.number, strftime(commit.ctime), (lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(commit.message)))  # line 894
# TODO list number of files and binary/text

def config(argument, options) -> 'None':  # line 897
    if argument not in ["set", "unset", "show", "add", "rm"]:  # line 898
        Exit("Unknown config command")  # line 898
    if not configr:  # line 899
        Exit("Cannot execute config command. 'configr' module not installed")  # line 899
    c = loadConfig()  # type: Union[configr.Configr, Accessor]  # line 900
    if argument == "set":  # line 901
        if len(options) < 2:  # line 902
            Exit("No key nor value specified")  # line 902
        if options[0] not in (["defaultbranch"] + CONFIGURABLE_FLAGS + CONFIGURABLE_LISTS):  # line 903
            Exit("Unsupported key %r" % options[0])  # line 903
        c[options[0]] = options[1].lower() in TRUTH_VALUES if options[0] in CONFIGURABLE_FLAGS else (options[1].strip() if options[0] not in CONFIGURABLE_LISTS else [options[0]])  # TODO sanitize texts?  # line 904
        f, g = c.saveSettings()  # line 905
        if f is None:  # line 906
            error("Error saving user configuration: %r" % g)  # line 906
    elif argument == "unset":  # line 907
        if len(options) < 1:  # line 908
            Exit("No key specified")  # line 908
        if options[0] not in c.keys():  # line 909
            Exit("Unsupported key")  # line 909
        try:  # line 910
            del c[options[0]]  # line 911
            f, g = c.saveSettings()  # line 912
            if f is None:  # line 913
                error("Error saving user configuration: %r" % g)  # line 913
        except Exception as E:  # line 914
            Exit("Unknown key specified: %r (%r)" % (options[0], E))  # line 914
    elif argument == "add":  # line 915
        if len(options) < 2:  # line 916
            Exit("No key nor value specified")  # line 916
        if options[0] not in CONFIGURABLE_LISTS:  # line 917
            Exit("Unsupported key for add %r" % options[0])  # line 917
        if options[0] not in c.keys():  # add list  # line 918
            c[options[0]] = [options[1]]  # add list  # line 918
        elif options[1] in c[options[0]]:  # line 919
            Exit("Value already contained")  # line 919
        c[options[0]].append(options[1])  # line 920
        f, g = c.saveSettings()  # line 921
        if f is None:  # line 922
            error("Error saving user configuration: %r" % g)  # line 922
    elif argument == "rm":  # line 923
        if len(options) < 2:  # line 924
            Exit("No key nor value specified")  # line 924
        if options[0] not in c.keys():  # line 925
            Exit("Unknown key specified: %r" % options[0])  # line 925
        del c[options[0]][options[0]]  # line 926
        f, g = c.saveSettings()  # line 927
        if f is None:  # line 928
            error("Error saving user configuration: %r" % g)  # line 928
    else:  # Show  # line 929
        for k, v in sorted(c.items()):  # line 930
            print("%s => %s" % (k, v))  # line 930

def parse(root: 'str'):  # line 932
    ''' Main operation. '''  # line 933
    debug("Parsing command-line arguments...")  # line 934
    command = sys.argv[1].strip() if len(sys.argv) > 1 else ""  # line 935
    argument = sys.argv[2].strip() if len(sys.argv) > 2 else None  # line 936
    options = sys.argv[3:] if command == "config" else [c for c in sys.argv[2:] if c.startswith("--")]  # consider second parameter for no-arg command, otherwise from third on  # line 937
    debug("Processing command %r with argument '%s' and options %r." % ("" if command is None else command, "" if argument is None else argument, options))  # line 938
    if command[:1] == "a":  # a  # line 939
        add(argument, options)  # a  # line 939
    elif command[:1] == "b":  # b  # line 940
        branch(argument, options)  # b  # line 940
    elif command[:2] == "ch":  # ch  # line 941
        changes(argument, options)  # ch  # line 941
    elif command[:3] == "com" or command[:2] == "ci":  # com, ci  # line 942
        commit(argument, options)  # com, ci  # line 942
    elif command[:3] == 'con':  # con  # line 943
        config(argument, options)  # con  # line 943
    elif command[:2] == "de":  # de  # line 944
        delete(argument, options)  # de  # line 944
    elif command[:2] == "di":  # di  # line 945
        diff(argument, options)  # di  # line 945
    elif command[:1] == "h":  # h  # line 946
        usage()  # h  # line 946
    elif command[:2] == "lo":  # lo  # line 947
        log()  # lo  # line 947
    elif command[:2] in ["li", "ls"]:  # li, ls  # line 948
        ls(argument)  # li, ls  # line 948
    elif command[:2] == "of":  # of  # line 949
        offline(argument, options)  # of  # line 949
    elif command[:2] == "on":  # on  # line 950
        online(options)  # on  # line 950
    elif command[:1] == "r":  # r  # line 951
        rm(argument)  # r  # line 951
    elif command[:2] == "st":  # st  # line 952
        status()  # st  # line 952
    elif command[:2] == "sw":  # sw  # line 953
        switch(argument, options)  # sw  # line 953
    elif command[:2] == "up":  # up  # line 954
        update(argument, options)  # up  # line 954
    else:  # line 955
        Exit("Unknown command '%s'" % command)  # line 955
    sys.exit(0)  # line 956

def findSosVcsBase() -> 'Tuple[_coconut.typing.Optional[str], _coconut.typing.Optional[str], _coconut.typing.Optional[str]]':  # line 958
    ''' Attempts to find sos and legacy VCS base folders. '''  # line 959
    debug("Detecting root folders...")  # line 960
    path = os.getcwd()  # type: str  # start in current folder, check parent until found or stopped  # line 961
    vcs = (None, None)  # type: Tuple[_coconut.typing.Optional[str], _coconut.typing.Optional[str]]  # line 962
    while not os.path.exists(os.path.join(path, metaFolder)):  # line 963
        contents = set(os.listdir(path))  # line 964
        vcss = [executable for folder, executable in vcsFolders.items() if folder in contents]  # type: _coconut.typing.Sequence[str]  # determine VCS type from dot folder  # line 965
        choice = None  # type: _coconut.typing.Optional[str]  # line 966
        if len(vcss) > 1:  # line 967
            choice = "svn" if "svn" in vcss else vcss[0]  # line 968
            warn("Detected more than one parallel VCS checkouts %r. Falling back to '%s'" % (vcss, choice))  # line 969
        elif len(vcss) > 0:  # line 970
            choice = vcss[0]  # line 970
        if not vcs[0] and choice:  # memorize current repo root  # line 971
            vcs = (path, choice)  # memorize current repo root  # line 971
        new = os.path.dirname(path)  # get parent path  # line 972
        if new == path:  # avoid infinite loop  # line 973
            break  # avoid infinite loop  # line 973
        path = new  # line 974
    if os.path.exists(os.path.join(path, metaFolder)):  # found something  # line 975
        if vcs[0]:  # already detected vcs base and command  # line 976
            return (path, vcs[0], vcs[1])  # already detected vcs base and command  # line 976
        sos = path  # line 977
        while True:  # continue search for VCS base  # line 978
            new = os.path.dirname(path)  # get parent path  # line 979
            if new == path:  # no VCS folder found  # line 980
                return (sos, None, None)  # no VCS folder found  # line 980
            path = new  # line 981
            contents = set(os.listdir(path))  # line 982
            vcss = [executable for folder, executable in vcsFolders.items() if folder in contents]  # determine VCS type  # line 983
            choice = None  # line 984
            if len(vcss) > 1:  # line 985
                choice = "svn" if "svn" in vcss else vcss[0]  # line 986
                warn("Detected more than one parallel VCS checkouts %r. Falling back to '%s'" % (vcss, choice))  # line 987
            elif len(vcss) > 0:  # line 988
                choice = vcss[0]  # line 988
            if choice:  # line 989
                return (sos, path, choice)  # line 989
    return (None, vcs[0], vcs[1])  # line 990

def main() -> 'None':  # line 992
    global debug, info, warn, error  # line 993
    logging.basicConfig(level=level, stream=sys.stderr, format=("%(asctime)-23s %(levelname)-8s %(name)s:%(lineno)d | %(message)s" if '--log' in sys.argv else "%(message)s"))  # line 994
    _log = Logger(logging.getLogger(__name__))  # line 995
    debug, info, warn, error = _log.debug, _log.info, _log.warn, _log.error  # line 995
    for option in (o for o in ['--log', '--verbose', '-v', '--sos'] if o in sys.argv):  # clean up program arguments  # line 996
        sys.argv.remove(option)  # clean up program arguments  # line 996
    if '--help' in sys.argv or len(sys.argv) < 2:  # line 997
        usage()  # line 997
        Exit()  # line 997
    command = sys.argv[1] if len(sys.argv) > 1 else None  # type: _coconut.typing.Optional[str]  # line 998
    root, vcs, cmd = findSosVcsBase()  # root is None if no .sos folder exists up the folder tree (still working online); vcs is checkout/repo root folder; cmd is the VCS base command  # line 999
    debug("Found root folders for SOS/VCS: %s/%s" % ("" if root is None else root, "" if vcs is None else vcs))  # line 1000
    defaults["defaultbranch"] = vcsBranches.get(cmd, "trunk")  # sets dynamic default with SVN fallback  # line 1001
    if force_sos or root is not None or ("" if command is None else command)[:2] == "of" or ("" if command is None else command)[:1] == "h":  # in offline mode or just going offline TODO what about git config?  # line 1002
        os.chdir(os.getcwd() if command[:2] == "of" else os.getcwd() if root is None else root)  # since all operatiosn use os.getcwd() and we save one argument to each function  # line 1003
        parse(root)  # line 1004
    elif cmd is not None:  # online mode - delegate to VCS  # line 1005
        info("SOS: Running '%s %s'" % (cmd, " ".join(sys.argv[1:])))  # line 1006
        import subprocess  # only requuired in this section  # line 1007
        process = subprocess.Popen([cmd] + sys.argv[1:], shell=False, stdin=subprocess.PIPE, stdout=sys.stdout, stderr=sys.stderr)  # line 1008
        inp = ""  # type: str  # line 1009
        while True:  # line 1010
            so, se = process.communicate(input=inp)  # line 1011
            if process.returncode is not None:  # line 1012
                break  # line 1012
            inp = sys.stdin.read()  # line 1013
        if sys.argv[1][:2] == "co" and process.returncode == 0:  # successful commit - assume now in sync again (but leave meta data folder with potential other feature branches behind until "online")  # line 1014
            if root is None:  # line 1015
                Exit("Cannot determine VCS root folder: Unable to mark repository as synchronized and will show a warning when leaving offline mode")  # line 1015
            m = Metadata(root)  # line 1016
            m.loadBranches()  # read repo  # line 1017
            m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], insync=True)  # mark as committed  # line 1018
            m.saveBranches()  # line 1019
    else:  # line 1020
        Exit("No offline repository present, and unable to detect VCS file tree")  # line 1020


# Main part
level = logging.DEBUG if os.environ.get("DEBUG", "False").lower() == "true" or '--verbose' in sys.argv or '-v' in sys.argv else logging.INFO  # line 1024
force_sos = '--sos' in sys.argv  # line 1025
_log = Logger(logging.getLogger(__name__))  # line 1026
debug, info, warn, error = _log.debug, _log.info, _log.warn, _log.error  # line 1026
if __name__ == '__main__':  # line 1027
    main()  # line 1027
