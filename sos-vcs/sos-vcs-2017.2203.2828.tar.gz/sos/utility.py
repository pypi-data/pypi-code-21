#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0xc6a614e5

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

# Utiliy functions
import bz2
import codecs
import difflib
import hashlib
import logging
import os
sys = _coconut_sys
import time
try:
    from typing import Any  # only required for mypy
    from typing import Dict  # only required for mypy
    from typing import IO  # only required for mypy
    from typing import List  # only required for mypy
    from typing import Tuple  # only required for mypy
    from typing import Type  # only required for mypy
    from typing import TypeVar  # only required for mypy
    from typing import Union  # only required for mypy
    Number = Union[int, float]
except:  # typing not available (e.g. Python 2)
    pass  # typing not available (e.g. Python 2)


# Classes
class Accessor(dict):
    ''' Dictionary with attribute access. Writing only supported via dictionary access. '''
    def __init__(_, mapping) -> 'None':
        dict.__init__(_, mapping)
    @_coconut_tco
    def __getattribute__(_, name: 'str') -> 'List[str]':
        try:
            return _[name]
        except:
            return _coconut_tail_call(dict.__getattribute__, _, name)

class Counter:
    def __init__(_, initial: 'Number'=0) -> 'None':
        _.value = initial  # type: Number
    def inc(_, by=1) -> 'Number':
        _.value += by
        return _.value

class Logger:
    ''' Logger that supports many items. '''
    def __init__(_, log):
        _._log = log
    def debug(_, *s):
        _._log.debug(sjoin(*s))
    def info(_, *s):
        _._log.info(sjoin(*s))
    def warn(_, *s):
        _._log.warning(sjoin(*s))
    def error(_, *s):
        _._log.error(sjoin(*s))


# Constants
_log = Logger(logging.getLogger(__name__))
debug, info, warn, error = _log.debug, _log.info, _log.warn, _log.error
UTF8 = "utf_8"  # early used constant, not defined in standard library
CONFIGURABLE_FLAGS = ["strict", "track", "picky", "compress"]
CONFIGURABLE_LISTS = ["texttype", "bintype", "ignores", "ignoreDirs", "ignoresWhitelist", "ignoreDirsWhitelist"]
TRUTH_VALUES = ["true", "yes", "on", "1", "enable", "enabled"]  # all lower-case normalized
PROGRESS_MARKER = ["|", "/", "-", "\\"]
metaFolder = ".sos"  # type: str
metaFile = ".meta"  # type: str
bufSize = 1 << 20  # type: int  # 1 MiB
SVN = "svn"
SLASH = "/"
vcsFolders = {".svn": SVN, ".git": "git", ".bzr": "bzr", ".hg": "hg", ".fslckout": " fossil", ".CVS": "cvs"}  # type: Dict[str, str]
vcsBranches = {SVN: "trunk", "git": "master", "bzr": "trunk", "hg": "default", "fossil": None, "cvs": None}  # type: Dict[str, _coconut.typing.Optional[str]]


# Value types
class BranchInfo(_coconut_NamedTuple("BranchInfo", [("number", 'int'), ("ctime", 'int'), ("name", '_coconut.typing.Optional[str]'), ("insync", 'bool'), ("tracked", 'List[str]')])):  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place
    __slots__ = ()  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place
    __ne__ = _coconut.object.__ne__  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place
    def __new__(_cls, number, ctime, name=None, insync=False, tracked=[]):  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place
        return _coconut.tuple.__new__(_cls, (number, ctime, name, insync, tracked))  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place
# tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place
class CommitInfo(_coconut_NamedTuple("CommitInfo", [("number", 'int'), ("ctime", 'int'), ("message", '_coconut.typing.Optional[str]')])):
    __slots__ = ()
    __ne__ = _coconut.object.__ne__
    def __new__(_cls, number, ctime, message=None):
        return _coconut.tuple.__new__(_cls, (number, ctime, message))

class PathInfo(_coconut_NamedTuple("PathInfo", [("namehash", 'str'), ("size", '_coconut.typing.Optional[int]'), ("mtime", 'int'), ("hash", 'str')])):  # size == None means deleted in this revision
    __slots__ = ()  # size == None means deleted in this revision
    __ne__ = _coconut.object.__ne__  # size == None means deleted in this revision
class ChangeSet(_coconut_NamedTuple("ChangeSet", [("additions", 'Dict[str, PathInfo]'), ("deletions", 'Dict[str, PathInfo]'), ("modifications", 'Dict[str, PathInfo]')])):  # avoid default assignment of {} as it leads to runtime errors (contains data on init for unknown reason)
    __slots__ = ()  # avoid default assignment of {} as it leads to runtime errors (contains data on init for unknown reason)
    __ne__ = _coconut.object.__ne__  # avoid default assignment of {} as it leads to runtime errors (contains data on init for unknown reason)
class Range(_coconut_NamedTuple("Range", [("tipe", 'int'), ("indexes", '_coconut.typing.Sequence[int]')])):  # MergeBlockType[1,2,4], line number, length
    __slots__ = ()  # MergeBlockType[1,2,4], line number, length
    __ne__ = _coconut.object.__ne__  # MergeBlockType[1,2,4], line number, length
class MergeBlock(_coconut_NamedTuple("MergeBlock", [("tipe", 'int'), ("lines", '_coconut.typing.Sequence[str]'), ("line", 'int'), ("replaces", '_coconut.typing.Optional[MergeBlock]'), ("changes", '_coconut.typing.Optional[Range]')])):
    __slots__ = ()
    __ne__ = _coconut.object.__ne__
    def __new__(_cls, tipe, lines, line, replaces=None, changes=None):
        return _coconut.tuple.__new__(_cls, (tipe, lines, line, replaces, changes))



# Enums
class ConflictResolution:  # prefer their changes, prefer my changes, ask user for each change, go to next deeper level (e.g. from files to lines, characters)
    THEIRS, MINE, ASK, NEXT = range(4)  # prefer their changes, prefer my changes, ask user for each change, go to next deeper level (e.g. from files to lines, characters)
class MergeOperation:  # insert remote changes into current, remove remote deletions from current, do both (replicate remote state) TODO handle inline-operations separate?
    INSERT, REMOVE, BOTH = 1, 2, 3  # insert remote changes into current, remove remote deletions from current, do both (replicate remote state) TODO handle inline-operations separate?
class MergeBlockType:  # modify = intra-line changes
    KEEP, INSERT, REMOVE, REPLACE, MODIFY, MOVE = range(6)  # modify = intra-line changes


# Functions
def detect(binary: 'bytes') -> 'str':  # Guess the encoding
    ''' Fallback if chardet library missing. '''
    try:
        binary.decode(UTF8)
        return UTF8
    except UnicodeError:
        pass
    try:
        binary.decode("utf_16")
        return "utf_16"
    except UnicodeError:
        pass
    try:
        binary.decode("cp1252")
        return "cp1252"
    except UnicodeError:
        pass
    return "ascii"  # this code will never be reached, as above is an 8-bit charset that always matches

def openIt(file: 'str', mode: 'str', compress: 'bool'=False) -> 'IO':  # Abstraction for opening both compressed and plain files
    return bz2.BZ2File(file, mode) if compress else open(file, mode + "b")  # Abstraction for opening both compressed and plain files

def eoldet(file: 'bytes') -> '_coconut.typing.Optional[bytes]':
    ''' Determine EOL style from a binary string. '''
    lf = file.count(b"\n")  # type: int
    cr = file.count(b"\r")  # type: int
    crlf = file.count(b"\r\n")  # type: int
    if crlf > 0:  # DOS/Windows/Symbian etc.
        if lf != crlf or cr != crlf:
            warn("Inconsistent CR/NL count with CR+NL. Mixed EOL style detected, may cause problems during merge")
        return b"\r\n"
    if lf != 0 and cr != 0:
        warn("Inconsistent CR/NL count without CR+NL. Mixed EOL style detected, may cause problems during merge")
    if lf > cr:  # Linux/Unix
        return b"\n"  # Linux/Unix
    if cr > lf:  # older 8-bit machines
        return b"\r"  # older 8-bit machines
    return None  # no new line contained, cannot determine

def Exit(message: 'str'="") -> 'None':
    print(message, file=sys.stderr)
    sys.exit(1)

@_coconut_tco  # dynamic Python2/3. don't simplify, eval must be inside function for unknown reason
def user_input(msg: 'str') -> 'str':  # dynamic Python2/3. don't simplify, eval must be inside function for unknown reason
    return _coconut_tail_call(eval("input" if sys.version_info.major >= 3 else "raw_input"), msg)  # dynamic Python2/3. don't simplify, eval must be inside function for unknown reason

try:
    Splittable = TypeVar("Splittable", str, bytes)
except:  # Python 2
    pass  # Python 2
def safeSplit(s: 'Splittable', d: '_coconut.typing.Optional[Splittable]'=None) -> '_coconut.typing.Sequence[Splittable]':
    return s.split(("\n" if isinstance(s, str) else b"\n") if d is None else d) if len(s) > 0 else []

def ajoin(sep: 'str', seq: '_coconut.typing.Sequence[str]', nl="") -> 'str':
    return sep + (nl + sep).join(seq)

@_coconut_tco
def sjoin(*s: 'Tuple[Any]') -> 'str':
    return _coconut_tail_call(" ".join, [str(e) for e in s if e != ''])

@_coconut_tco
def hashStr(datas: 'str') -> 'str':
    return _coconut_tail_call(hashlib.sha256(datas.encode(UTF8)).hexdigest)

@_coconut_tco
def hashFile(path: 'str', compress: 'bool', saveTo: '_coconut.typing.Optional[str]'=None) -> 'str':
    ''' Calculate hash of file contents. '''
    _hash = hashlib.sha256()
    to = openIt(saveTo, "w", compress) if saveTo else None
    with open(path, "rb") as fd:
        while True:
            buffer = fd.read(bufSize)
            _hash.update(buffer)
            if to:
                to.write(buffer)
            if len(buffer) < bufSize:
                break
        if to:
            to.close()
    return _coconut_tail_call(_hash.hexdigest)

def firstOfMap(map: 'Dict[str, Any]', params: '_coconut.typing.Sequence[str]', default: 'Any'=None) -> 'Any':
    ''' Utility. '''
    for k, v in map.items():
        if k in params:
            return v
    return default

@_coconut_tco
def strftime(timestamp: '_coconut.typing.Optional[int]'=None) -> 'str':
    return _coconut_tail_call(time.strftime, "%Y-%m-%d %H:%M:%S", time.localtime(timestamp / 1000. if timestamp is not None else None))

def detectAndLoad(filename: '_coconut.typing.Optional[str]'=None, content: '_coconut.typing.Optional[bytes]'=None) -> 'Tuple[str, bytes, _coconut.typing.Sequence[str]]':
    encoding = None  # type: str
    eol = None  # type: bytes
    lines = []  # type: _coconut.typing.Sequence[str]
    if filename is not None:
        with open(filename, "rb") as fd:
            content = fd.read()
    encoding = (lambda _coconut_none_coalesce_item: sys.getdefaultencoding() if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(detect(content))
    eol = eoldet(content)
    if filename is not None:
        with codecs.open(filename, encoding=encoding) as fd:
            lines = safeSplit(fd.read(), (b"\n" if eol is None else eol).decode(encoding))
    elif content is not None:
        lines = safeSplit(content.decode(encoding), (b"\n" if eol is None else eol).decode(encoding))
    else:
        return (sys.getdefaultencoding(), b"\n", [])
    return (encoding, eol, lines)

def diffPathSets(last: 'Dict[str, PathInfo]', diff: 'Dict[str, PathInfo]') -> 'ChangeSet':
    ''' Computes a changeset between in-memory and on-disk file lists.
      Additions contains PathInfo for entries in diff
      Deletions contains PathInfo for entries not anymore in diff
      Modifications contains PathInfo for entries changed from last to diff (new state)
  '''
    changes = ChangeSet({}, {}, {})  # type: ChangeSet
    for path, pinfo in last.items():
        if path not in diff:  # now change  changes.deletions[path] = pinfo; continue
            continue  # now change  changes.deletions[path] = pinfo; continue
        vs = diff[path]  # reference to potentially changed path set
        if vs.size is None:  # marked for deletion
            changes.deletions[path] = pinfo  # marked for deletion
            continue  # marked for deletion
        if pinfo.size == None:  # re-added
            changes.additions[path] = pinfo  # re-added
            continue  # re-added
        if pinfo.size != vs.size or pinfo.mtime != vs.mtime or pinfo.hash != vs.hash:  # not need to make hash comparison optional here
            changes.modifications[path] = vs  # not need to make hash comparison optional here
    for path, pinfo in diff.items():  # added loop
        if path not in last:
            changes.additions[path] = pinfo
    assert not any([path in changes.deletions for path in changes.additions])  # invariant checks
    assert not any([path in changes.additions for path in changes.deletions])
    return changes

try:
    DataType = TypeVar("DataType", MergeBlock, BranchInfo)
except:  # Python 2
    pass  # Python 2

@_coconut_tco
def dataCopy(_tipe: 'Type[DataType]', _old: 'DataType', *_args, **_kwargs) -> 'DataType':
    r = _old._asdict()
    r.update(**_kwargs)
    return _coconut_tail_call(makedata, _tipe, *(list(_args) + [r[field] for field in _old._fields]))
# TODO test namedtuple instead of instantiated tuple types in "datatype"?

@_coconut_tco
def merge(file: '_coconut.typing.Optional[bytes]'=None, into: '_coconut.typing.Optional[bytes]'=None, filename: '_coconut.typing.Optional[str]'=None, intoname: '_coconut.typing.Optional[str]'=None, mergeOperation=MergeOperation.BOTH, conflictResolution=ConflictResolution.ASK) -> 'bytes':
    ''' Merges binary text contents 'file' into file 'into', returning merged result. '''
    encoding = None  # type: str
    othr = None  # type: _coconut.typing.Sequence[str]
    othreol = None  # type: _coconut.typing.Optional[bytes]
    curr = None  # type: _coconut.typing.Sequence[str]
    curreol = None  # type: _coconut.typing.Optional[bytes]
    differ = difflib.Differ()
    try:  # load files line-wise and normalize line endings (keep the one of the current file) TODO document
        encoding, othreol, othr = detectAndLoad(filename=filename, content=file)
        encoding, curreol, curr = detectAndLoad(filename=intoname, content=into)
    except Exception as E:
        Exit("Cannot merge '%s' into '%s': %r" % (filename, intoname, E))
    if None not in [othreol, curreol] and othreol != curreol:
        warn("Differing EOL-styles detected during merge. Using current file's style for merge output")
    output = list(differ.compare(othr, curr))  # type: List[str]  # from generator expression
    debug("Diff output: " + "".join([o.replace("\n", "\\n") for o in output]))
    blocks = []  # type: List[MergeBlock]  # merged result in blocks
    tmp = []  # type: List[str]  # block lines
    last = " "
    for no, line in enumerate(output + ["X"]):  # EOF marker
        if line[0] == last:  # continue filling consecutive block
            tmp.append(line[2:])  # continue filling consecutive block
            continue  # continue filling consecutive block
        if line == "X":  # EOF marker - perform action for remaining block
            if len(tmp) == 0:  # nothing left to do
                break  # nothing left to do
        if last == " ":  # block is same in both files
            blocks.append(MergeBlock(MergeBlockType.KEEP, [line for line in tmp], line=no - len(tmp)))
        elif last == "-":  # may be a deletion or replacement, store for later
            blocks.append(MergeBlock(MergeBlockType.REMOVE, [line for line in tmp], line=no - len(tmp)))
        elif last == "+":  # may be insertion or replacement
            blocks.append(MergeBlock(MergeBlockType.INSERT, [line for line in tmp], line=no - len(tmp)))
            if len(blocks) >= 2 and len(blocks[-1].lines) == len(blocks[-2].lines):  # replaces previously removed section entirely if any
                if len(blocks[-1].lines) >= 2 or (blocks[-1].changes is None and blocks[-2].changes is None):  # full block or no intra-line comment
                    blocks[-2] = MergeBlock(MergeBlockType.REPLACE, blocks[-1].lines, line=no - len(tmp), replaces=blocks[-2])  # remember replaced stuff
                else:  # may have intra-line modifications
                    blocks[-2] = MergeBlock(MergeBlockType.MODIFY, blocks[-1].lines, line=no - len(tmp), replaces=blocks[-2], changes=blocks[-1].changes)
                blocks.pop()  # remove TOS
        elif last == "?":  # intra-line change comment
            ilm = getIntraLineMarkers(tmp[0])  # tipe is one of MergeBlockType 1, 2, 4. # "? " line includes a trailing \n for some reason
            blocks[-1] = dataCopy(MergeBlock, blocks[-1], tipe=MergeBlockType.MODIFY, changes=ilm)  # update to MODIFY, otherwise may be REPLACE instead
        last = line[0]
        tmp[:] = [line[2:]]
    debug("Diff blocks: " + repr(blocks))
    output = []
    for block in blocks:
        if block.tipe == MergeBlockType.KEEP:
            output.extend(block.lines)
        elif block.tipe == MergeBlockType.INSERT and not (mergeOperation & MergeOperation.REMOVE):
            output.extend(block.lines)
        elif block.tipe == MergeBlockType.REPLACE:  # complete block replacement
            if mergeOperation & MergeOperation.INSERT:  # replaced stuff TODO allow insertion BEFORE and alternatively AFTER?
                output.extend(block.replaces.lines)  # replaced stuff TODO allow insertion BEFORE and alternatively AFTER?
            if not (mergeOperation & MergeBlockType.REMOVE):  # if remove, don't add replaced lines, otherwise do
                output.extend(block.lines)  # if remove, don't add replaced lines, otherwise do
        elif block.tipe == MergeBlockType.REMOVE and mergeOperation & MergeOperation.INSERT:
            output.extend(block.lines)
        elif block.tipe == MergeBlockType.MODIFY:
            if block.changes is not None and block.changes.tipe == MergeBlockType.INSERT:  # cannot be REMOVE, because it's always "-" then "+"
                output.extend(block.lines if mergeOperation & MergeOperation.INSERT else block.replaces.lines)  # TODO logic?
            elif block.replaces.changes is not None and block.replaces.changes.tipe == MergeBlockType.REMOVE:
                output.extend(block.lines if mergeOperation & MergeOperation.REMOVE else block.replaces.lines)
            elif block.changes is not None and block.changes.tipe == MergeBlockType.MODIFY:  # always both sides modified, but may differ in markers
                if conflictResolution == ConflictResolution.THEIRS:
                    output.extend(block.replaces.lines)
                elif conflictResolution == ConflictResolution.MINE:
                    output.extend(block.lines)
                elif conflictResolution == ConflictResolution.ASK:
                    print(ajoin("THR ", block.replaces.lines, "\n"))
                    print(ajoin("MIN ", block.lines, "\n"))
                    reso = {"i": ConflictResolution.MINE, "t": ConflictResolution.THEIRS, "m": ConflictResolution.NEXT, "u": None}.get(user_input(" Resolve: *M[I]ne, [T]heirs, [M]erge, [U]ser defined: ").strip().lower(), ConflictResolution.MINE)  # type: _coconut.typing.Optional[int]
                    debug("User selected %d" % reso)
                    _coconut_match_check = False
                    _coconut_match_to = reso
                    if _coconut_match_to is None:
                        _coconut_match_check = True
                    if _coconut_match_check:
                        warn("Manual input not implemented yet")  # TODO allow multi-line input (CTRL+D?)
                    _coconut_match_check = False
                    _coconut_match_to = reso
                    if _coconut_match_to == ConflictResolution.MINE:
                        _coconut_match_check = True
                    if _coconut_match_check:
                        debug("Using mine")
                        output.extend(block.lines)
                    _coconut_match_check = False
                    _coconut_match_to = reso
                    if _coconut_match_to == ConflictResolution.THEIRS:
                        _coconut_match_check = True
                    if _coconut_match_check:
                        debug("Using theirs")
                        output.extend(block.replaces.lines)
                    _coconut_match_check = False
                    _coconut_match_to = reso
                    if _coconut_match_to == ConflictResolution.NEXT:
                        _coconut_match_check = True
                    if _coconut_match_check:
                        warn("Intra-line merge not implemented yet, skipping line(s)")
                        output.extend(block.replaces.lines)
            else:  # e.g. contains a deletion, but user was asking for insert only??
                warn("Investigate this case")
                output.extend(block.lines)  # default or not .replaces?
    debug("Merge output: " + "; ".join(output))
    nl = b"\n" if othreol is None else othreol if curreol is None else curreol  # type: bytes
    return _coconut_tail_call(nl.join, [line.encode(encoding) for line in output])
# TODO handle check for more/less lines in found -/+ blocks to find common section and splitting prefix/suffix out

@_coconut_tco
def getIntraLineMarkers(line: 'str') -> 'Range':
    ''' Return (type, [affected indices]) of "? "-line diff markers ("? " suffix must be removed). '''
    if "^" in line:
        return _coconut_tail_call(Range, MergeBlockType.MODIFY, [i for i, c in enumerate(line) if c == "^"])
    if "+" in line:
        return _coconut_tail_call(Range, MergeBlockType.INSERT, [i for i, c in enumerate(line) if c == "+"])
    if "-" in line:
        return _coconut_tail_call(Range, MergeBlockType.REMOVE, [i for i, c in enumerate(line) if c == "-"])
    return _coconut_tail_call(Range, MergeBlockType.KEEP, [])

def findSosVcsBase() -> 'Tuple[_coconut.typing.Optional[str], _coconut.typing.Optional[str], _coconut.typing.Optional[str]]':
    ''' Attempts to find sos and legacy VCS base folders. '''
    debug("Detecting root folders...")
    path = os.getcwd()  # type: str  # start in current folder, check parent until found or stopped
    vcs = (None, None)  # type: Tuple[_coconut.typing.Optional[str], _coconut.typing.Optional[str]]
    while not os.path.exists(os.path.join(path, metaFolder)):
        contents = set(os.listdir(path))
        vcss = [executable for folder, executable in vcsFolders.items() if folder in contents]  # type: _coconut.typing.Sequence[str]  # determine VCS type from dot folder
        choice = None  # type: _coconut.typing.Optional[str]
        if len(vcss) > 1:
            choice = SVN if SVN in vcss else vcss[0]
            warn("Detected more than one parallel VCS checkouts %r. Falling back to '%s'" % (vcss, choice))
        elif len(vcss) > 0:
            choice = vcss[0]
        if not vcs[0] and choice:  # memorize current repo root
            vcs = (path, choice)  # memorize current repo root
        new = os.path.dirname(path)  # get parent path
        if new == path:  # avoid infinite loop
            break  # avoid infinite loop
        path = new
    if os.path.exists(os.path.join(path, metaFolder)):  # found something
        if vcs[0]:  # already detected vcs base and command
            return (path, vcs[0], vcs[1])  # already detected vcs base and command
        sos = path
        while True:  # continue search for VCS base
            new = os.path.dirname(path)  # get parent path
            if new == path:  # no VCS folder found
                return (sos, None, None)  # no VCS folder found
            path = new
            contents = set(os.listdir(path))
            vcss = [executable for folder, executable in vcsFolders.items() if folder in contents]  # determine VCS type
            choice = None
            if len(vcss) > 1:
                choice = SVN if SVN in vcss else vcss[0]
                warn("Detected more than one parallel VCS checkouts %r. Falling back to '%s'" % (vcss, choice))
            elif len(vcss) > 0:
                choice = vcss[0]
            if choice:
                return (sos, path, choice)
    return (None, vcs[0], vcs[1])
