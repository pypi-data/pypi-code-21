#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x5ccc674e

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
import codecs
import difflib
import fnmatch
import json
import logging
import mimetypes
import os
import shutil
sys = _coconut_sys
import time
try:
    from typing import Any  # only required for mypy
    from typing import Dict  # only required for mypy
    from typing import FrozenSet  # only required for mypy
    from typing import IO  # only required for mypy
    from typing import List  # only required for mypy
    from typing import Set  # only required for mypy
    from typing import Tuple  # only required for mypy
    from typing import Type  # only required for mypy
    from typing import TypeVar  # only required for mypy
    from typing import Union  # only required for mypy
except:  # typing not available (e.g. Python 2)
    pass  # typing not available (e.g. Python 2)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from sos import version
    from sos.utility import *
except:
    import version
    from utility import *

# External dependencies
try:  # optional dependency
    import configr  # optional dependency
except:  # declare as undefined
    configr = None  # declare as undefined
try:
    import chardet  # https://github.com/chardet/chardet
    def detect(binary: 'bytes') -> 'str':
        return chardet.detect(binary)["encoding"]
except:  # uses version from utility.coco
    pass  # uses version from utility.coco
#from enforce import runtime_validation  # https://github.com/RussBaz/enforce  TODO doesn't work for "data" types


# Constants
APPNAME = "Subversion Offline Solution  V%s  (C) Arne Bachmann" % version.__release_version__  # type: str
defaults = Accessor({"strict": False, "track": False, "picky": False, "compress": True, "texttype": [], "bintype": [], "ignoreDirs": [".*", "__pycache__"], "ignoreDirsWhitelist": [], "ignores": ["__coconut__.py", "*.bak", "*.py[cdo]", "*.class", ".fslckout"], "ignoresWhitelist": []})


# Functions
def loadConfig() -> 'Union[configr.Configr, Accessor]':  # Simplifies loading config from file system or returning the defaults
    config = None  # type: Union[configr.Configr, Accessor]
    if not configr:  # this only applies for the case that configr is not available, thus no settings will be persisted anyway
        return defaults  # this only applies for the case that configr is not available, thus no settings will be persisted anyway
    config = configr.Configr("sos", defaults=defaults)  # defaults are used if key is not configured, but won't be saved
    f, g = config.loadSettings(clientCodeLocation=os.path.abspath(__file__), location=os.environ.get("TEST", None))
    if f is None:
        debug("Encountered a problem while loading the user configuration: %r" % g)
    return config

@_coconut_tco
def saveConfig(c: 'configr.Configr') -> 'Tuple[_coconut.typing.Optional[str], _coconut.typing.Optional[Exception]]':
    return _coconut_tail_call(c.saveSettings, clientCodeLocation=os.path.abspath(__file__), location=os.environ.get("TEST", None))

def usage() -> 'None':
    print("""/// {appname} ///

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
    config  [set/unset/show/add/rm] [<param> [<value>]]   Configure user-global defaults.
                                                          Flags (1/0, on/off, true/false, yes/no):
                                                            strict, track, picky, compress
                                                          Lists (semicolon-separated when set; single values for add/rm):
                                                            texttype, bintype, ignores, ignoreDirs, ignoresWhitelist, ignoreDirsWhitelist
                                                          Supported texts:
                                                            defaultbranch (has a dynamic default value, depending on VCS discovered)
    help, --help                                          Show this usage information

  Arguments:
    <branch/revision>           Revision string. Branch is optional and may be a label or index
                                Revision is an optional integer and may be negative to reference from the latest commits (-1 is most recent revision)

  Common options:
    --force                     Executes potentially harmful operations
                                  for offline: ignore being already offline, start from scratch (same as 'sos online --force && sos offline')
                                  for online: ignore uncommitted branches
                                  for commit, switch, update, add: ignore uncommitted changes before executing command
    --strict                    Perform full content comparison, don't rely only on file size and timestamp
                                  for offline: persist strict mode in repository
                                  for changes, diff, commit, switch, update, delete: perform operation in strict mode
    --{cmd}                       When executing {CMD} not being offline, pass arguments to {CMD} instead (e.g. {cmd} --{cmd} config set key value.)
    --log                       Enable internals logger
    --verbose                   Enable debugging output""".format(appname=APPNAME, cmd="sos", CMD="SOS"))

# Main data class
#@runtime_validation
class Metadata:
    ''' This class doesn't represent the entire repository state in memory,
      but serves as a container for different repo operations,
      using only parts of its attributes at any point in time. Use with care.
  '''

    def __init__(_, path: 'str') -> 'None':
        ''' Create empty container object for various repository operations. '''
        _.c = loadConfig()
        _.root = path  # type: str
        _.branches = {}  # type: Dict[int, BranchInfo]  # branch number zero represents the initial state at branching
        _.commits = {}  # type: Dict[int, CommitInfo]  # consecutive numbers per branch, starting at 0
        _.paths = {}  # type: Dict[str, PathInfo]  # utf-8 encoded relative, normalized file system paths
        _.track = _.c.track  # type: bool  # track files in the repository (tracked patterns are stored for each branch separately)
        _.picky = _.c.picky  # type: bool  # pick files on each operation
        _.strict = _.c.strict  # type: bool  # be always strict (regarding file contents comparsion)
        _.compress = _.c.compress  # type: bool  # these flags are stored per branch, therefore not part of the (default) configuration
        _.branch = None  # type: _coconut.typing.Optional[int]  # current branch number
        _.commit = None  # type: _coconut.typing.Optional[int]  # current revision number

    def isTextType(_, filename: 'str') -> 'bool':
        return (((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(mimetypes.guess_type(filename)[0])).startswith("text/") or any([fnmatch.fnmatch(filename, pattern) for pattern in _.c.texttype])) and not any([fnmatch.fnmatch(filename, pattern) for pattern in _.c.bintype])

    def listChanges(_, changes: 'ChangeSet', diffmode: 'bool'=False, textglobs: '_coconut.typing.Sequence[str]'=[]) -> 'None':
        ''' In diffmode, don't list modified files, because the diff is displayed elsewhere. '''
        if len(changes.additions) > 0:
            print(ajoin("ADD ", sorted(changes.additions.keys()), "\n"))
        if len(changes.deletions) > 0:
            print(ajoin("DEL ", sorted(changes.deletions.keys()), "\n"))
        if len(changes.modifications) > 0:  # only list binary files
            print(ajoin("MOD ", sorted((k for k in changes.modifications.keys() if not _.isTextType(k) or not diffmode)), "\n"))  # only list binary files

    def loadBranches(_) -> 'None':
        ''' Load list of branches and current branch info from metadata file. '''
        try:  # fails if not yet created (on initial branch/commit)
            branches = None  # type: List[Tuple]
            with codecs.open(os.path.join(_.root, metaFolder, metaFile), "r", encoding=UTF8) as fd:
                flags, branches = json.load(fd)
            _.branch = flags["branch"]
            _.track = flags["track"]
            _.picky = flags["picky"]
            _.strict = flags["strict"]
            _.compress = flags["compress"]
            _.branches = {i.number: i for i in (BranchInfo(*item) for item in branches)}  # re-create type info
        except Exception as E:  # if not found, create metadata folder
            _.branches = {}
            warn("Couldn't read branches metadata: %r" % E)

    def saveBranches(_) -> 'None':
        ''' Save list of branches and current branch info to metadata file. '''
        with codecs.open(os.path.join(_.root, metaFolder, metaFile), "w", encoding=UTF8) as fd:
            json.dump(({"branch": _.branch, "track": _.track, "picky": _.picky, "strict": _.strict, "compress": _.compress}, list(_.branches.values())), fd, ensure_ascii=False)

    def getBranchByName(_, name: 'Union[str, int]') -> '_coconut.typing.Optional[int]':
        ''' Convenience accessor for named branches. '''
        if isinstance(name, int):  # if type(name) is int: return name
            return name  # if type(name) is int: return name
        try:  # attempt to parse integer string
            return int(name)  # attempt to parse integer string
        except ValueError:
            pass
        found = [number for number, branch in _.branches.items() if name == branch.name]
        return found[0] if found else None

    def loadBranch(_, branch: 'int') -> 'None':
        ''' Load all commit information from a branch meta data file. '''
        with codecs.open(os.path.join(_.root, metaFolder, "b%d" % branch, metaFile), "r", encoding=UTF8) as fd:
            commits = json.load(fd)  # type: List[List[Any]]  # list of CommitInfo that needs to be unmarshalled into value types
        _.commits = {i.number: i for i in (CommitInfo(*item) for item in commits)}  # re-create type info
        _.branch = branch

    def saveBranch(_, branch: 'int') -> 'None':
        ''' Save all commit information to a branch meta data file. '''
        with codecs.open(os.path.join(_.root, metaFolder, "b%d" % branch, metaFile), "w", encoding=UTF8) as fd:
            json.dump(list(_.commits.values()), fd, ensure_ascii=False)

    def duplicateBranch(_, branch: 'int', name: '_coconut.typing.Optional[str]') -> 'None':
        ''' Create branch from an existing branch/revision. WARN: Caller must have loaded branches information.
        branch: target branch (should not exist yet)
        name: optional name of new branch
        _.branch: current branch
    '''
        debug("Duplicating branch '%s' to '%d'..." % ((lambda _coconut_none_coalesce_item: "b%d" % _.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(_.branches[_.branch].name), branch))
        tracked = [t for t in _.branches[_.branch].tracked]  # copy
        os.makedirs(os.path.join(_.root, metaFolder, "b%d" % branch, "r0"))
        _.loadBranch(_.branch)
        revision = max(_.commits)  # type: int
        _.computeSequentialPathSet(_.branch, revision)  # full set of files in revision to _.paths
        for path, pinfo in _.paths.items():
            _.copyVersionedFile(_.branch, revision, branch, 0, pinfo)
        _.commits = {0: CommitInfo(0, int(time.time() * 1000), "Branched from '%s'" % ((lambda _coconut_none_coalesce_item: "b%d" % _.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(_.branches[_.branch].name)))}  # store initial commit
        _.saveBranch(branch)  # save branch meta data to branch folder
        _.saveCommit(branch, 0)  # save commit meta data to revision folder
        _.branches[branch] = BranchInfo(branch, _.commits[0].ctime, name, _.branches[_.branch].insync, tracked)  # save branch info, before storing repo state at caller

    def createBranch(_, branch: 'int', name: '_coconut.typing.Optional[str]'=None, initialMessage: '_coconut.typing.Optional[str]'=None):
        ''' Create a new branch from current file tree. This clears all known commits and modifies the file system.
        branch: target branch (should not exist yet)
        name: optional name of new branch
        _.branch: current branch, must exist already
    '''
        simpleMode = not (_.track or _.picky)
        tracked = [t for t in _.branches[_.branch].tracked] if _.track and len(_.branches) > 0 else []  # in case of initial branch creation
        debug((lambda _coconut_none_coalesce_item: "b%d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)("Creating branch '%s'..." % name))
        _.paths = {}  # type: Dict[str, PathInfo]
        if simpleMode:
            changes = _.findChanges(branch, 0, progress=simpleMode)  # type: ChangeSet  # creates revision folder and versioned files
            _.listChanges(changes)
            _.paths.update(changes.additions.items())
        else:  # tracking or picky mode
            os.makedirs(os.path.join(_.root, metaFolder, "b%d" % branch, "r0"))
            if _.branch is not None:  # not immediately after "offline" - copy files from current branch
                _.loadBranch(_.branch)
                revision = max(_.commits)  # type: int  # TODO what if last switch was to an earlier revision? no persisting of last checkout
                _.computeSequentialPathSet(_.branch, revision)  # full set of files in revision to _.paths
                for path, pinfo in _.paths.items():
                    _.copyVersionedFile(_.branch, revision, branch, 0, pinfo)
        ts = int(time.time() * 1000)
        _.commits = {0: CommitInfo(0, ts, "Branched on %s" % strftime(ts) if initialMessage is None else initialMessage)}  # store initial commit for new branch
        _.saveBranch(branch)  # save branch meta data (revisions) to branch folder
        _.saveCommit(branch, 0)  # save commit meta data to revision folder
        _.branches[branch] = BranchInfo(branch, _.commits[0].ctime, name, True if len(_.branches) == 0 else _.branches[_.branch].insync, tracked)  # save branch info, in case it is needed

    def removeBranch(_, branch: 'int') -> 'BranchInfo':
        ''' Entirely remove a branch and all its revisions from the file system. '''
        shutil.rmtree(os.path.join(_.root, metaFolder, "b%d" % branch))
        binfo = _.branches[branch]
        del _.branches[branch]
        _.branch = max(_.branches)
        _.saveBranches()
        _.commits.clear()
        return binfo

    def loadCommit(_, branch: 'int', revision: 'int') -> 'None':
        ''' Load all file information from a commit meta data. '''
        with codecs.open(os.path.join(_.root, metaFolder, "b%d" % branch, "r%d" % revision, metaFile), "r", encoding=UTF8) as fd:
            _.paths = json.load(fd)
        _.paths = {path: PathInfo(*item) for path, item in _.paths.items()}  # re-create type info
        _.branch = branch

    def saveCommit(_, branch: 'int', revision: 'int'):
        ''' Save all file information to a commit meta data file. '''
        target = os.path.join(_.root, metaFolder, "b%d" % branch, "r%d" % revision)
        try:
            os.makedirs(target)
        except:
            pass
        with codecs.open(os.path.join(target, metaFile), "w", encoding=UTF8) as fd:
            json.dump(_.paths, fd, ensure_ascii=False)

    def findChanges(_, branch: '_coconut.typing.Optional[int]'=None, revision: '_coconut.typing.Optional[int]'=None, checkContent: 'bool'=False, inverse: 'bool'=False, considerOnly: '_coconut.typing.Optional[FrozenSet[str]]'=None, progress: 'bool'=False) -> 'ChangeSet':
        ''' Find changes on the file system vs. in-memory paths (which should reflect the latest commit state).
        Only if both branch and revision are *not* None, write modified/added files to the specified revision folder (thus creating a new revision)
        The function returns the state of file tree *differences*, unless "inverse" is True -> then return original data
        checkContent: also computes file content hashes
        inverse: retain original state (size, mtime, hash) instead of updated one
        considerOnly: set of tracking patterns. For update operation, union of other and current branch
        progress: Show file names during processing
    '''
        write = branch is not None and revision is not None
        if write:
            os.makedirs(os.path.join(_.root, metaFolder, "b%d" % branch, "r%d" % revision))
        changes = ChangeSet({}, {}, {})  # type: ChangeSet
        counter = Counter(-1)  # type: Counter
        timer = time.time()
        for path, dirnames, filenames in os.walk(_.root):
            dirnames[:] = [f for f in dirnames if len([n for n in _.c.ignoreDirs if fnmatch.fnmatch(f, n)]) == 0 or len([p for p in _.c.ignoreDirsWhitelist if fnmatch.fnmatch(f, p)]) > 0]
            filenames[:] = [f for f in filenames if len([n for n in _.c.ignores if fnmatch.fnmatch(f, n)]) == 0 or len([p for p in _.c.ignoresWhitelist if fnmatch.fnmatch(f, p)]) > 0]
            dirnames.sort()
            filenames.sort()
            relpath = os.path.relpath(path, _.root).replace(os.sep, SLASH)
            for file in (filenames if considerOnly is None else list(reduce(lambda last, pattern: last | set(fnmatch.filter(filenames, os.path.basename(pattern))), (p for p in considerOnly if os.path.dirname(p) == relpath), _coconut.set()))):  # if m.track or m.picky: only files that match any path-relevant tracking patterns
                filename = relpath + SLASH + file
                filepath = os.path.join(path, file)
                stat = os.stat(filepath)
                size, mtime, newtime = stat.st_size, int(stat.st_mtime * 1000), time.time()
                if progress and newtime - timer > .1:
                    outstring = "\rPreparing %s  %s" % (PROGRESS_MARKER[counter.inc() % 4], filename)
                    sys.stdout.write(outstring + " " * max(0, 80 - len(outstring)))  # TODO could write to new line instead of carriage return, also needs terminal width
                    sys.stdout.flush()  # TODO could write to new line instead of carriage return, also needs terminal width
                    timer = newtime  # TODO could write to new line instead of carriage return, also needs terminal width
                if filename not in _.paths:  # detected file not present (or untracked) in other branch
                    namehash = hashStr(filename)
                    changes.additions[filename] = PathInfo(namehash, size, mtime, hashFile(filepath, _.compress, saveTo=os.path.join(_.root, metaFolder, "b%d" % branch, "r%d" % revision, namehash) if write else None) if size > 0 else None)
                    continue
                last = _.paths[filename]  # filename is known
                if last.size is None:  # was removed before but is now added back - does not apply for tracking mode (which never marks files for removal in the history)
                    changes.additions[filename] = PathInfo(last.namehash, size, mtime, hashFile(filepath, _.compress, saveTo=os.path.join(_.root, metaFolder, "b%d" % branch, "r%d" % revision, last.namehash) if write else None) if size > 0 else None)
                    continue
                elif size != last.size or mtime != last.mtime or (checkContent and hashFile(filepath, _.compress) == last.hash):  # detected a modification
                    changes.modifications[filename] = PathInfo(last.namehash, last.size if inverse else size, last.mtime if inverse else mtime, last.hash if inverse else hashFile(filepath, _.compress, saveTo=os.path.join(_.root, metaFolder, "b%d" % branch, "r%d" % revision, last.namehash) if write else None) if (last.size if inverse else size) > 0 else None)
# Detect deletions. Files no longer being tracked should not be found here
            for folderPath in (p for p, pinfo in _.paths.items() if p[:p.rindex(SLASH)] == relpath and pinfo.size is not None):  # only versioned (and tracked) files that match currently visited folder. TODO don't check for removal just added entries
                if folderPath[len(relpath) + 1:] not in filenames:  # filename no longer in file tree TODO use basename and dirname instead of slicing?
                    changes.deletions[folderPath] = _.paths[folderPath]  # filename no longer in file tree TODO use basename and dirname instead of slicing?
        if progress:  # force new line
            print("Preparation finished." + " " * 59, file=sys.stdout)  # force new line
        return changes

    def integrateChangeset(_, changes: 'ChangeSet', clear=False) -> 'None':
        ''' In-memory update from a changeset, marking deleted files with size=None. Use clear = True to start on an empty path set. '''
        if clear:
            _.paths.clear()
        else:
            rm = [p for p, info in _.paths.items() if info.size is None]  # remove files deleted in earlier change sets (revisions)
            for old in rm:  # remove previously removed entries completely
                del _.paths[old]  # remove previously removed entries completely
        for d, info in changes.deletions.items():  # mark now removed entries as deleted
            _.paths[d] = PathInfo(info.namehash, None, info.mtime, None)  # mark now removed entries as deleted
        _.paths.update(changes.additions)
        _.paths.update(changes.modifications)

    def computeSequentialPathSet(_, branch: 'int', revision: 'int') -> 'None':
        ''' In-memory computation of current list of valid PathInfo entries for specified branch and until specified revision (inclusively) by traversing revision on the file system. '''
        _.loadCommit(branch, 0)  # load initial paths
        n = Metadata(_.root)  # type: Metadata  # next changes
        for revision in range(1, revision + 1):
            n.loadCommit(branch, revision)
            changes = diffPathSets(_.paths, n.paths)  # type: ChangeSet
            _.integrateChangeset(changes)

    def parseRevisionString(_, argument: 'str') -> 'Tuple[_coconut.typing.Optional[int], _coconut.typing.Optional[int]]':
        ''' Commit identifiers can be str or int for branch, and int for revision.
        Revision identifiers can be negative, with -1 being last commit.
    '''
        if argument is None:  # no branch/revision specified
            return (_.branch, -1)  # no branch/revision specified
        argument = argument.strip()
        if argument.startswith(SLASH):  # current branch
            return (_.branch, int(argument[1:]))  # current branch
        if argument.endswith(SLASH):
            try:
                return (_.getBranchByName(argument[:-1]), -1)
            except ValueError:
                Exit("Unknown branch label")
        if SLASH in argument:
            b, r = argument.split(SLASH)[:2]
            try:
                return (_.getBranchByName(b), int(r))
            except ValueError:
                Exit("Unknown branch label or wrong number format")
        branch = _.getBranchByName(argument)  # type: int  # returns number if given (revision) integer
        if branch not in _.branches:
            branch = None
        try:  # either branch name/number or reverse/absolute revision number
            return (_.branch if branch is None else branch, int(argument) if branch is None else -1)  # either branch name/number or reverse/absolute revision number
        except:
            Exit("Unknown branch label or wrong number format")
        return (None, None)  # should never be reached TODO raise exception instead?

    def findRevision(_, branch: 'int', revision: 'int', namehash: 'str') -> 'Tuple[int, str]':
        while True:  # find latest revision that contained the file physically
            source = os.path.join(_.root, metaFolder, "b%d" % branch, "r%d" % revision, namehash)  # type: str
            if os.path.exists(source) and os.path.isfile(source):
                break
            revision -= 1
            if revision < 0:
                Exit("Cannot determine versioned file '%s' from specified branch '%d'" % (namehash, branch))
        return revision, source

    def copyVersionedFile(_, branch: 'int', revision: 'int', tobranch: 'int', torevision: 'int', pinfo: 'PathInfo') -> 'None':
        ''' Copy versioned file to other branch/revision. '''
        target = os.path.join(_.root, metaFolder, "b%d" % tobranch, "r%d" % torevision, pinfo.namehash)  # type: str
        revision, source = _.findRevision(branch, revision, pinfo.namehash)
        shutil.copy2(source, target)

    def readOrCopyVersionedFile(_, branch: 'int', revision: 'int', namehash: 'str', toFile: '_coconut.typing.Optional[str]'=None) -> '_coconut.typing.Optional[bytes]':
        ''' Return file contents, or copy contents into file path provided. '''
        source = os.path.join(_.root, metaFolder, "b%d" % branch, "r%d" % revision, namehash)  # type: str
        try:
            with openIt(source, "r", _.compress) as fd:
                if toFile is None:  # read bytes into memory and return
                    return fd.read()  # read bytes into memory and return
                with open(toFile, "wb") as to:
                    while True:
                        buffer = fd.read(bufSize)
                        to.write(buffer)
                        if len(buffer) < bufSize:
                            break
                    return None
        except Exception as E:
            warn("Cannot read versioned file: %r (%d/%d/%s)" % (E, branch, revision, namehash))
        return None

    def restoreFile(_, relpath: '_coconut.typing.Optional[str]', branch: 'int', revision: 'int', pinfo: 'PathInfo') -> '_coconut.typing.Optional[bytes]':
        ''' Recreate file for given revision, or return contents if path is None. '''
        if relpath is None:  # just return contents
            return _.readOrCopyVersionedFile(branch, _.findRevision(branch, revision, pinfo.namehash)[0], pinfo.namehash) if pinfo.size > 0 else b''  # just return contents
        target = os.path.join(_.root, relpath.replace(SLASH, os.sep))  # type: str
        if pinfo.size == 0:
            with open(target, "wb"):
                pass
            try:  # update access/modification timestamps on file system
                os.utime(target, (-1, pinfo.mtime / 1000.))  # update access/modification timestamps on file system
            except Exception as E:
                error("Cannot update file's timestamp after restoration '%r'" % E)
            return None
        revision, source = _.findRevision(branch, revision, pinfo.namehash)
# Restore file by copying buffer-wise
        with openIt(source, "r", _.compress) as fd, open(target, "wb") as to:  # using Coconut's Enhanced Parenthetical Continuation
            while True:
                buffer = fd.read(bufSize)
                to.write(buffer)
                if len(buffer) < bufSize:
                    break
        try:  # update access/modification timestamps on file system
            os.utime(target, (-1, pinfo.mtime / 1000.))  # update access/modification timestamps on file system
        except Exception as E:
            error("Cannot update file's timestamp after restoration '%r'" % E)
        return None

    def getTrackingPatterns(_, branch: '_coconut.typing.Optional[int]'=None) -> 'FrozenSet[str]':
        ''' Returns list of tracking patterns for provided branch or current branch. '''
        return _coconut.frozenset() if not _.track and not _.picky else frozenset(_.branches[_.branch if branch is None else branch].tracked)


# Main client operations
def offline(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]) -> 'None':
    ''' Initial command to start working offline. '''
    if '--force' not in options and os.path.exists(metaFolder):
        Exit("Repository folder is either already offline or older branches and commits were left over. Use 'sos online' or continue working offline")
    m = Metadata(os.getcwd())  # type: Metadata
    if '--picky' in options or m.c.picky:  # Git-like
        m.picky = True  # Git-like
    elif '--track' in options or m.c.track:  # Svn-like
        m.track = True  # Svn-like
    if '--strict' in options or m.c.strict:  # always hash contents
        m.strict = True  # always hash contents
    debug("Preparing offline repository...")
    m.createBranch(0, str(defaults["defaultbranch"]) if argument is None else argument, initialMessage="Offline repository created on %s" % strftime())  # main branch's name may be None (e.g. for fossil)
    m.branch = 0
    m.saveBranches()  # no change immediately after going offline, going back online won't issue a warning
    info("Offline repository prepared. Use 'sos online' to finish offline work")

def online(options: '_coconut.typing.Sequence[str]'=[]) -> 'None':
    ''' Finish working offline. '''
    force = '--force' in options  # type: bool
    m = Metadata(os.getcwd())
    m.loadBranches()
    if any([not b.insync for b in m.branches.values()]) and not force:
        Exit("There are still unsynchronized (dirty) branches.\nUse 'sos log' to list them.\nUse 'sos commit' and 'sos switch' to commit relevant ones to your VCS before leaving offline mode.\nUse 'sos online --force' to erase all aggregated offline revisions.")
    strict = '--strict' in options or m.strict  # type: bool
    if options.count("--force") < 2:
        changes = m.findChanges(checkContent=strict, considerOnly=None if not m.track else m.getTrackingPatterns())  # type: ChangeSet
        if len(changes.additions) > 0 or len(changes.deletions) > 0 or len(changes.modifications) > 0:
            Exit("File tree is modified vs. current branch.\nUse 'sos online --force --force' to continue with removing the offline repository.")
    try:
        shutil.rmtree(metaFolder)
        info("Exited offline mode. Continue working with your traditional VCS.")
    except Exception as E:
        Exit("Error removing offline repository: %r" % E)

def branch(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]) -> 'None':
    ''' Create a new branch (from file tree or last revision) and (by default) continue working on it. '''
    last = '--last' in options  # type: bool  # use last revision for branching, not current file tree
    stay = '--stay' in options  # type: bool  # continue on current branch after branching
    force = '--force' in options  # type: bool  # branch even with local modifications
    m = Metadata(os.getcwd())  # type: Metadata
    m.loadBranches()
    if argument and m.getBranchByName(argument) is not None:  # create a named branch
        Exit("Branch '%s' already exists. Cannot proceed" % argument)  # create a named branch
    branch = max(m.branches.keys()) + 1  # next branch's key
    debug("Branching to %sbranch b%d%s%s..." % ("unnamed " if argument is None else "", branch, " '%s'" % argument if argument else "", " from last revision" if last else ""))
    if last:
        m.duplicateBranch(branch, argument)  # branch from branch's last revision
    else:  # from file tree state
        m.createBranch(branch, argument)  # branch from current file tree
    if not stay:
        m.branch = branch
        m.saveBranches()
    info("%s new %sbranch b%d%s" % ("Continue work after branching" if stay else "Switched to", "unnamed " if argument is None else "", branch, " '%s'" % argument if argument else ""))

def changes(argument: 'str'=None, options: '_coconut.typing.Sequence[str]'=[]) -> 'ChangeSet':
    ''' Show changes of file tree vs. (last or specified) revision on current or specified branch. '''
    m = Metadata(os.getcwd())  # type: Metadata
    branch = None  # type: _coconut.typing.Optional[int]
    revision = None  # type: _coconut.typing.Optional[int]
    m.loadBranches()  # knows current branch
    strict = '--strict' in options or m.strict  # type: bool
    branch, revision = m.parseRevisionString(argument)
    if branch not in m.branches:
        Exit("Unknown branch")
    m.loadBranch(branch)  # knows commits
    revision = revision if revision >= 0 else len(m.commits) + revision  # negative indexing
    if revision < 0 or revision > max(m.commits):
        Exit("Unknown revision r%d" % revision)
    info("/// Changes of file tree vs. revision '%s/r%d'" % ((lambda _coconut_none_coalesce_item: "b%d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision
    changes = m.findChanges(checkContent=strict, considerOnly=None if not m.track else m.getTrackingPatterns() | m.getTrackingPatterns(branch))  # type: ChangeSet
    m.listChanges(changes)
    return changes

def diff(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]) -> 'None':
    ''' Show text file differences of file tree vs. (last or specified) revision on current or specified branch. '''
    m = Metadata(os.getcwd())  # type: Metadata
    branch = None  # type: _coconut.typing.Optional[int]
    revision = None  # type: _coconut.typing.Optional[int]
    m.loadBranches()  # knows current branch
    strict = '--strict' in options or m.strict  # type: bool
    branch, revision = m.parseRevisionString(argument)
    if branch not in m.branches:
        Exit("Unknown branch")
    m.loadBranch(branch)  # knows commits
    revision = revision if revision >= 0 else len(m.commits) + revision  # negative indexing
    if revision < 0 or revision > max(m.commits):
        Exit("Unknown revision r%d" % revision)
    info("/// Differences of file tree vs. revision '%s/r%d'" % ((lambda _coconut_none_coalesce_item: "b%d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision
    changes = m.findChanges(checkContent=strict, inverse=True, considerOnly=None if not m.track else m.getTrackingPatterns() | m.getTrackingPatterns(branch))  # type: ChangeSet
    info("/// File changes")
    m.listChanges(changes, diffmode=True)  # only list modified binary files

    info("\n/// Textual modifications")  # TODO only text files, not binary
    differ = difflib.Differ()  # TODO move to utility and remove difflib import
    for path, pinfo in changes.modifications.items():  # only consider modified files TODO also show A/D here? or replace listing above?
        print("\nDIF " + path)
        content = None  # type: _coconut.typing.Optional[bytes]
        othr = None  # type: _coconut.typing.Sequence[str]
        curr = None  # type: _coconut.typing.Sequence[str]
        if pinfo.size == 0:  # empty file contents
            content = b""  # empty file contents
        else:  # versioned file
            content = m.restoreFile(None, branch, revision, pinfo)  # versioned file
            assert content is not None  # versioned file
        abspath = os.path.join(m.root, path.replace(SLASH, os.sep))  # current file
        encoding, othreol, othr = detectAndLoad(content=content)
        encoding, curreol, curr = detectAndLoad(filename=abspath)
        currcount, othrcount = Counter(), Counter()  # TODO shows empty new line although none in file. also counting is messed up
        last = ""
        for no, line in enumerate(differ.compare(othr, curr)):
            if line[0] == " ":  # no change in line
                continue  # no change in line
            print("%04d/%04d %s" % (no + othrcount.inc(-1 if line[0] == "+" or (line[0] == "?" and last == "+") else 0), no + currcount.inc(-1 if line[0] == "-" or (line[0] == "?" and last == "-") else 0), line))  # TODO counting this is definitely wrong and also lists \n as new diff lines. Could reuse block detection from merge instead
            last = line[0]

def commit(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]) -> 'None':
    ''' Create new revision from file tree changes vs. last commit. '''
    changes = None  # type: ChangeSet
    m, branch, revision, changes, strict, force, trackingPatterns = exitOnChanges(None, options, commit=True)  # special flag creates new revision for detected changes, but abort if no changes
    info((lambda _coconut_none_coalesce_item: "b%d" % m.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)("Committing changes to branch '%s'..." % m.branches[m.branch].name))
    m.integrateChangeset(changes, clear=True)  # update pathset to changeset only
    m.saveCommit(m.branch, revision)  # revision has already been incremented
    m.commits[revision] = CommitInfo(revision, int(time.time() * 1000), argument)  # comment can be None
    m.saveBranch(m.branch)
    if m.picky or m.track:  # TODO is it necessary to load again
        m.loadBranches()  # TODO is it necessary to load again
    if m.picky:  # HINT was changed from only picky to include track as well
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], tracked=[], insync=False)  # remove tracked patterns
    elif m.track:
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], insync=False)  # set branch dirty
    if m.picky or m.track:
        m.saveBranches()
    info("Created new revision r%02d%s (+%d/-%d/*%d)" % (revision, ((" '%s'" % argument) if argument is not None else ""), len(changes.additions), len(changes.deletions), len(changes.modifications)))

def status() -> 'None':
    ''' Show branches and current repository state. '''
    m = Metadata(os.getcwd())  # type: Metadata
    m.loadBranches()  # knows current branch
    current = m.branch  # type: int
    info("/// Offline repository status")
    sl = max([len((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(b.name)) for b in m.branches.values()])  # type: int
    for branch in sorted(m.branches.values(), key=lambda b: b.number):
        m.loadBranch(branch.number)  # knows commit history
        print("  %s b%d%s @%s (%s) with %d commits%s" % ("*" if current == branch.number else " ", branch.number, ((" %%%ds" % (sl + 2)) % ("'%s'" % branch.name)) if branch.name else "", strftime(branch.ctime), "in sync" if branch.insync else "dirty", len(m.commits), ". Last comment: '%s'" % m.commits[max(m.commits)].message if m.commits[max(m.commits)].message else ""))
    if m.track or m.picky and len(m.branches[m.branch].tracked) > 0:
        info("\nTracked file patterns:")
        print(ajoin("  | ", m.branches[m.branch].tracked, "\n"))

def exitOnChanges(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[], check: 'bool'=True, commit: 'bool'=False) -> 'Tuple[Metadata, _coconut.typing.Optional[int], int, ChangeSet, bool, bool, FrozenSet[str]]':
    ''' Common behavior for switch, update, delete, commit.
      check: stop program on detected change
      commit: don't stop on changes, because that's what we need in the operation
      Returns (Metadata, (current or target) branch, revision, set of changes vs. last commit on current branch, strict, force flags. '''
    m = Metadata(os.getcwd())  # type: Metadata
    m.loadBranches()  # knows current branch
    trackingPatterns = m.getTrackingPatterns()  # type: FrozenSet[str]  # SVN-like mode
    force = '--force' in options  # type: bool
    strict = '--strict' in options or m.strict  # type: bool
    if argument is not None:
        branch, revision = m.parseRevisionString(argument)  # for early abort
        if branch is None:
            Exit("Branch '%s' doesn't exist. Cannot proceed" % argument)
    m.loadBranch(m.branch)  # knows last commits of *current* branch

# Determine current changes
    m.computeSequentialPathSet(m.branch, max(m.commits))  # load all commits up to specified revision
    changes = m.findChanges(checkContent=strict, considerOnly=None if not m.track and not m.picky else trackingPatterns) if not commit else m.findChanges(m.branch, max(m.commits) + 1, checkContent=strict, considerOnly=None if not m.track and not m.picky else trackingPatterns)  # type: ChangeSet
    if (changes.additions or changes.deletions or changes.modifications) and not force:  # and check?
        m.listChanges(changes)
        if check and not commit:
            Exit("File tree contains changes. Use --force to proceed")
    elif commit and not force:  #  and not check
        Exit("Nothing to commit. Aborting")  #  and not check

    if argument is not None:  # branch/revision specified
        m.loadBranch(branch)  # knows commits of target branch
        revision = revision if revision >= 0 else len(m.commits) + revision  # negative indexing
        if revision < 0 or revision > max(m.commits):
            Exit("Unknown revision r%02d" % revision)
        return (m, branch, revision, changes, strict, force, m.getTrackingPatterns(branch))
    return (m, m.branch, max(m.commits) + (1 if commit else 0), changes, strict, force, trackingPatterns)

def switch(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]) -> 'None':
    ''' Continue work on another branch, replacing file tree changes. '''
    changes = None  # type: ChangeSet
    m, branch, revision, changes, strict, force, trackingPatterns = exitOnChanges(argument, options)
    info("/// Switching to branch %sb%d/r%d" % ("'%s' " % m.branches[branch].name if m.branches[branch].name else "", branch, revision))

# Determine file changes from other branch to current file tree
    if '--meta' in options:  # only switch meta data
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], tracked=m.branches[branch].tracked)
    else:  # full file switch
        m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision for target branch into memory
        changes = m.findChanges(checkContent=strict, inverse=True, considerOnly=None if not m.track else trackingPatterns | m.getTrackingPatterns(branch))  # determine difference of other branch vs. file tree (forced or in sync with current branch; "addition" means exists now and should be removed)
        if not (changes.additions or changes.deletions or changes.modifications):
            info("No changes to current file tree")
        else:  # integration required
            for path, pinfo in changes.deletions.items():
                m.restoreFile(path, branch, revision, pinfo)  # is deleted in current file tree: restore from branch to reach target
                debug("ADD " + path)
            for path, pinfo in changes.additions.items():
                os.unlink(os.path.join(m.root, path.replace(SLASH, os.sep)))  # is added in current file tree: remove from branch to reach target
                debug("DEL " + path)
            for path, pinfo in changes.modifications.items():
                m.restoreFile(path, branch, revision, pinfo)  # is modified in current file tree: restore from branch to reach target
                debug("MOD " + path)
    m.branch = branch
    m.saveBranches()  # store switched path info
    info("Switched to branch %sb%d/r%d" % ("'%s' " % (m.branches[branch].name if m.branches[branch].name else ""), branch, revision))

def update(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]) -> 'None':
    ''' Load and integrate a specified other branch/revision into current life file tree.
      In tracking mode, this also updates the set of tracked patterns.
      User options for merge operation: --add (don't remove), --rm (don't insert), --add-lines/--rm-lines (inside each file)
      User options for conflict resolution: --theirs/--mine/--ask
  '''
    mrg = firstOfMap({"--add": MergeOperation.INSERT, "--rm": MergeOperation.REMOVE}, options, MergeOperation.BOTH)  # type: int  # default operation is replicate remove state for non-conflicting cases (insertions/deletions)
    res = firstOfMap({'--theirs': ConflictResolution.THEIRS, '--mine': ConflictResolution.MINE}, options, ConflictResolution.NEXT)  # type: int  # NEXT means deeper level
    mrgline = firstOfMap({'--add-lines': MergeOperation.INSERT, '--rm-lines': MergeOperation.REMOVE}, options, mrg)  # type: int  # default operation for modified files is same as for files
    resline = firstOfMap({'--theirs-lines': ConflictResolution.THEIRS, '--mine-lines': ConflictResolution.MINE}, options, ConflictResolution.ASK)  # type: int
    m = Metadata(os.getcwd())  # type: Metadata  # TODO same is called inside stop on changes - could return both current and designated branch instead
    m.loadBranches()
    changes = None  # type: ChangeSet
    currentBranch = m.branch  # type: _coconut.typing.Optional[int]
    m, branch, revision, changes, strict, force, trackingPatterns = exitOnChanges(argument, options, check=False)  # don't check for current changes, only parse arguments
    debug("Integrating changes from '%s/r%d' into file tree..." % ((lambda _coconut_none_coalesce_item: "b%d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))

# Determine file changes from other branch over current file tree
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision for branch to integrate
    trackingUnion = trackingPatterns | m.getTrackingPatterns(branch)  # type: FrozenSet[str]
    changes = m.findChanges(checkContent=strict, inverse=True, considerOnly=None if not m.track else trackingUnion)  # determine difference of other branch vs. file tree. "addition" means exists now but not in other, and should be removed unless in tracking mode
    if not (mrg & MergeOperation.INSERT and changes.additions or (mrg & MergeOperation.REMOVE and changes.deletions) or changes.modifications):
        if trackingUnion == trackingPatterns:  # nothing added
            info("No file changes detected, but tracking patterns were merged (run 'sos switch /-1 --meta' to undo)")  # TODO write test to see if this works
        else:
            info("Nothing to update")  # but write back updated branch info below
    else:  # integration required
        for path, pinfo in changes.deletions.items():  # deletions mark files not present in current file tree -> needs additon
            if mrg & MergeOperation.INSERT:  # deleted in current file tree: restore from branch to reach target
                m.restoreFile(path, branch, revision, pinfo)  # deleted in current file tree: restore from branch to reach target
            print("ADD " + path if mrg & MergeOperation.INSERT else "(A) " + path)
        for path, pinfo in changes.additions.items():
            if m.track or m.picky:  # because untracked files of other branch cannot be detected (which is good)
                Exit("This should never happen")  # because untracked files of other branch cannot be detected (which is good)
            if mrg & MergeOperation.REMOVE:
                os.unlink(m.root + os.sep + path.replace(SLASH, os.sep))
            print("DEL " if mrg & MergeOperation.REMOVE else "(D) " + path)  # not contained in other branch, but maybe kept
        for path, pinfo in changes.modifications.items():
            into = os.path.join(m.root, path.replace(SLASH, os.sep))  # type: str
            binary = not m.isTextType(path)
            if res & ConflictResolution.ASK or (binary and res == ConflictResolution.NEXT):  # TODO this may ask user even if no interaction was asked for (check line level for interactivity fist)
                print(("MOD " if not binary else "BIN ") + path)
                reso = {"i": ConflictResolution.MINE, "t": ConflictResolution.THEIRS, "m": ConflictResolution.NEXT}.get(user_input(" Resolve: *M[I]ne, [T]heirs, [M]erge: (I)").strip().lower(), ConflictResolution.MINE)
                debug("User selected %d" % reso)
            else:
                reso = res
            if reso & ConflictResolution.THEIRS:
                m.readOrCopyVersionedFile(branch, revision, pinfo.namehash, toFile=into)  # blockwise copy of contents
                print("THR " + path)
            elif reso & ConflictResolution.MINE:
                print("MNE " + path)  # nothing to do! same as skip
            else:  # NEXT: line-based merge
                file = m.readOrCopyVersionedFile(branch, revision, pinfo.namehash) if pinfo.size > 0 else b''  # type: _coconut.typing.Optional[bytes]  # parse lines TODO decode etc.
                if file is not None:  # if None, error message was already logged
                    contents = merge(file=file, intoname=into, mergeOperation=mrgline, conflictResolution=resline)  # type: bytes
                    with open(path, "wb") as fd:  # TODO write to temp file first
                        fd.write(contents)  # TODO write to temp file first
    info("Integrated changes from '%s/r%d' into file tree" % ((lambda _coconut_none_coalesce_item: "b%d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))
    m.branches[currentBranch] = dataCopy(BranchInfo, m.branches[currentBranch], insync=False, tracked=list(trackingUnion))  # TODO really? it's a change that cannot be undone easily by the user
    m.branch = currentBranch  # need to restore setting before saving TODO operate on different objects instead
    m.saveBranches()

def delete(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]) -> 'None':
    ''' Remove a branch entirely. '''
    m, branch, revision, changes, strict, force, trackingPatterns = exitOnChanges(argument, options)
    if len(m.branches) == 1:
        Exit("Cannot remove the only remaining branch. Use 'sos online' to leave offline mode")
    debug("Removing branch %d%s..." % (branch, " '%s'" % m.branches[branch].name if m.branches[branch].name else ""))
    binfo = m.removeBranch(branch)  # need to keep a reference to removed entry for output below
    info("Branch b%d%s removed" % (branch, " '%s'" % binfo.name if binfo.name else ""))

def add(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]) -> 'None':
    ''' Add a tracked files pattern to current branch's tracked files. '''
    force = '--force' in options  # type: bool
    m = Metadata(os.getcwd())  # type: Metadata
    m.loadBranches()
    if not m.track and not m.picky:
        Exit("Repository is in simple mode. Needs 'offline --track' or 'offline --picky' instead")
    relpath = os.path.relpath(os.path.dirname(os.path.abspath(argument)), m.root)  # for tracking list
    pattern = os.path.join(relpath, os.path.basename(argument)).replace(os.sep, SLASH)
    if pattern in m.branches[m.branch].tracked:
        Exit("Pattern '%s' already tracked")
    if not force and len(fnmatch.filter(os.listdir(os.path.abspath(relpath)), os.path.basename(pattern.replace(SLASH, os.sep)))) == 0:  # doesn't match any current file
        Exit("Pattern doesn't match any file in specified folder. Use --force to add it anyway")
    m.branches[m.branch].tracked.append(pattern)  # TODO set insync flag to False? same for rm
    m.saveBranches()
    info("Added tracking pattern '%s' for folder '%s'" % (os.path.basename(pattern.replace(SLASH, os.sep)), os.path.abspath(relpath)))

def rm(argument: 'str') -> 'None':
    ''' Remove a tracked files pattern from current branch's tracked files. '''
    m = Metadata(os.getcwd())  # type: Metadata
    m.loadBranches()
    if not m.track and not m.picky:
        Exit("Repository is in simple mode. Needs 'offline --track' or 'offline --picky' instead")
    relpath = os.path.relpath(os.path.dirname(os.path.abspath(argument)), m.root)  # type: str
    pattern = os.path.join(relpath, os.path.basename(argument)).replace(os.sep, SLASH)  # type: str
    if pattern not in m.branches[m.branch].tracked:
        suggestion = _coconut.set()  # type: Set[str]
        for pat in m.branches[m.branch].tracked:
            if fnmatch.fnmatch(pattern, pat):
                suggestion.add(pat)
        if suggestion:
            print("Do you mean any of the following tracked globs? '%s'" % (", ".join(sorted(suggestion))))
        Exit("Tracked pattern '%s' not found" % pattern)
    m.branches[m.branch].tracked.remove(pattern)
    m.saveBranches()
    info("Removed tracking pattern '%s' for folder '%s'" % (os.path.basename(pattern.replace(SLASH, os.sep)), os.path.abspath(relpath)))

def ls(argument: '_coconut.typing.Optional[str]'=None) -> 'None':
    ''' List specified directory, augmenting with repository metadata. '''
    cwd = os.getcwd() if argument is None else argument  # type: str
    m = Metadata(cwd)  # type: Metadata
    m.loadBranches()
    relpath = os.path.relpath(cwd, m.root).replace(os.sep, SLASH)  # type: str
    files = list(sorted((entry for entry in os.listdir(cwd) if os.path.isfile(entry))))  # type: List[str]
    trackingPatterns = m.getTrackingPatterns() if m.track or m.picky else _coconut.frozenset()  # type: FrozenSet[str]  # for current branch
    for file in files:
        ignore = None  # type: _coconut.typing.Optional[str]
        for ig in m.c.ignores:
            if fnmatch.fnmatch(file, ig):  # remember first match TODO document this
                ignore = ig  # remember first match TODO document this
                break  # remember first match TODO document this
        if ig:
            for wl in m.c.ignoresWhitelist:
                if fnmatch.fnmatch(file, wl):  # found a white list entry for ignored file, undo ignoring it
                    ignore = None  # found a white list entry for ignored file, undo ignoring it
                    break  # found a white list entry for ignored file, undo ignoring it
        if ignore is None:
            matches = []  # type: List[str]
            for pattern in (p for p in trackingPatterns if os.path.dirname(p) == relpath):  # only patterns matching current folder
                if fnmatch.fnmatch(file, os.path.basename(pattern)):  # TODO or only file basename?
                    matches.append(pattern)  # TODO or only file basename?
        print("%s %s%s" % ("IGN" if ignore is not None else ("TRK" if len(matches) > 0 else "   "), file, ' by "%s"' % ignore if ignore is not None else (" by " + ";".join(['"%s"' % match for match in matches]) if len(matches) > 0 else "")))

def log() -> 'None':
    ''' List previous commits on current branch. '''  # TODO --verbose for changesets
    m = Metadata(os.getcwd())  # type: Metadata
    m.loadBranches()  # knows current branch
    m.loadBranch(m.branch)  # knows commit history
    info((lambda _coconut_none_coalesce_item: "r%02d" % m.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)("/// Offline commit history of branch '%s'" % m.branches[m.branch].name))  # TODO also retain "from branch/revision" on branching?
    nl = len("%d" % max(m.commits))  # determine space needed for revision
    for commit in sorted(m.commits.values(), key=lambda co: co.number):
        print("  %s r%s @%s: %s" % ("*" if commit.number == max(m.commits) else " ", ("%%%ds" % nl) % commit.number, strftime(commit.ctime), (lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(commit.message)))
# TODO list number of files and binary/text

def config(argument: 'str', options: 'List[str]'=[]) -> 'None':
    if argument not in ["set", "unset", "show", "add", "rm"]:
        Exit("Unknown config command")
    if not configr:
        Exit("Cannot execute config command. 'configr' module not installed")
    c = loadConfig()  # type: Union[configr.Configr, Accessor]
    if argument == "set":
        if len(options) < 2:
            Exit("No key nor value specified")
        if options[0] not in (["defaultbranch"] + CONFIGURABLE_FLAGS + CONFIGURABLE_LISTS):
            Exit("Unsupported key %r" % options[0])
        c[options[0]] = options[1].lower() in TRUTH_VALUES if options[0] in CONFIGURABLE_FLAGS else (options[1].strip() if options[0] not in CONFIGURABLE_LISTS else safeSplit(options[1], ";"))  # TODO sanitize texts?
    elif argument == "unset":
        if len(options) < 1:
            Exit("No key specified")
        if options[0] not in c.keys():
            Exit("Unknown key")
        del c[options[0]]
    elif argument == "add":
        if len(options) < 2:
            Exit("No key nor value specified")
        if options[0] not in CONFIGURABLE_LISTS:
            Exit("Unsupported key for add %r" % options[0])
        if options[0] not in c.keys():  # add list
            c[options[0]] = [options[1]]  # add list
        elif options[1] in c[options[0]]:
            Exit("Value already contained")
        c[options[0]].append(options[1])
    elif argument == "rm":
        if len(options) < 2:
            Exit("No key nor value specified")
        if options[0] not in c.keys():
            Exit("Unknown key specified: %r" % options[0])
        if options[1] not in c[options[0]]:
            Exit("Unknown value: %r" % options[1])
        c[options[0]].remove(options[1])
    else:  # Show
        for k, v in sorted(c.items()):
            print("%s => %r" % (k, v))
        return
    f, g = saveConfig(c)
    if f is None:
        error("Error saving user configuration: %r" % g)

def parse(root: 'str'):
    ''' Main operation. '''
    debug("Parsing command-line arguments...")
    command = sys.argv[1].strip() if len(sys.argv) > 1 else ""
    argument = sys.argv[2].strip() if len(sys.argv) > 2 else None
    options = sys.argv[3:] if command == "config" else [c for c in sys.argv[2:] if c.startswith("--")]  # consider second parameter for no-arg command, otherwise from third on
    debug("Processing command %r with argument '%s' and options %r." % ("" if command is None else command, "" if argument is None else argument, options))
    if command[:1] == "a":  # a
        add(argument, options)  # a
    elif command[:1] == "b":  # b
        branch(argument, options)  # b
    elif command[:2] == "ch":  # ch
        changes(argument, options)  # ch
    elif command[:3] == "com" or command[:2] == "ci":  # com, ci
        commit(argument, options)  # com, ci
    elif command[:3] == 'con':  # con
        config(argument, options)  # con
    elif command[:2] == "de":  # de
        delete(argument, options)  # de
    elif command[:2] == "di":  # di
        diff(argument, options)  # di
    elif command[:1] == "h":  # h
        usage()  # h
    elif command[:2] == "lo":  # lo
        log()  # lo
    elif command[:2] in ["li", "ls"]:  # li, ls
        ls(argument)  # li, ls
    elif command[:2] == "of":  # of
        offline(argument, options)  # of
    elif command[:2] == "on":  # on
        online(options)  # on
    elif command[:1] == "r":  # r
        rm(argument)  # r
    elif command[:2] == "st":  # st
        status()  # st
    elif command[:2] == "sw":  # sw
        switch(argument, options)  # sw
    elif command[:2] == "up":  # up
        update(argument, options)  # up
    else:
        Exit("Unknown command '%s'" % command)
    sys.exit(0)

def main() -> 'None':
    global debug, info, warn, error
    logging.basicConfig(level=level, stream=sys.stderr, format=("%(asctime)-23s %(levelname)-8s %(name)s:%(lineno)d | %(message)s" if '--log' in sys.argv else "%(message)s"))
    _log = Logger(logging.getLogger(__name__))
    debug, info, warn, error = _log.debug, _log.info, _log.warn, _log.error
    for option in (o for o in ['--log', '--verbose', '-v', '--sos'] if o in sys.argv):  # clean up program arguments
        sys.argv.remove(option)  # clean up program arguments
    if '--help' in sys.argv or len(sys.argv) < 2:
        usage()
        Exit()
    command = sys.argv[1] if len(sys.argv) > 1 else None  # type: _coconut.typing.Optional[str]
    root, vcs, cmd = findSosVcsBase()  # root is None if no .sos folder exists up the folder tree (still working online); vcs is checkout/repo root folder; cmd is the VCS base command
    debug("Found root folders for SOS|VCS: %s|%s" % ("" if root is None else root, "" if vcs is None else vcs))
    defaults["defaultbranch"] = vcsBranches.get(cmd, "trunk")  # sets dynamic default with SVN fallback
    if force_sos or root is not None or ("" if command is None else command)[:2] == "of" or ("" if command is None else command)[:1] == "h":  # in offline mode or just going offline TODO what about git config?
        os.chdir(os.getcwd() if command[:2] == "of" else os.getcwd() if root is None else root)  # since all operatiosn use os.getcwd() and we save one argument to each function
        parse(root)
    elif cmd is not None:  # online mode - delegate to VCS
        info("SOS: Running '%s %s'" % (cmd, " ".join(sys.argv[1:])))
        import subprocess  # only requuired in this section
        process = subprocess.Popen([cmd] + sys.argv[1:], shell=False, stdin=subprocess.PIPE, stdout=sys.stdout, stderr=sys.stderr)
        inp = ""  # type: str
        while True:
            so, se = process.communicate(input=inp)
            if process.returncode is not None:
                break
            inp = sys.stdin.read()
        if sys.argv[1][:2] == "co" and process.returncode == 0:  # successful commit - assume now in sync again (but leave meta data folder with potential other feature branches behind until "online")
            if root is None:
                Exit("Cannot determine VCS root folder: Unable to mark repository as synchronized and will show a warning when leaving offline mode")
            m = Metadata(root)
            m.loadBranches()  # read repo
            m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], insync=True)  # mark as committed
            m.saveBranches()
    else:
        Exit("No offline repository present, and unable to detect VCS file tree")


# Main part
level = logging.DEBUG if os.environ.get("DEBUG", "False").lower() == "true" or '--verbose' in sys.argv or '-v' in sys.argv else logging.INFO
force_sos = '--sos' in sys.argv
_log = Logger(logging.getLogger(__name__))
debug, info, warn, error = _log.debug, _log.info, _log.warn, _log.error
if __name__ == '__main__':
    main()
