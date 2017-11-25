#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0xf1dc8c63

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

import builtins  # line 1
import doctest  # line 1
import logging  # line 1
import os  # line 1
import shutil  # line 1
sys = _coconut_sys  # line 1
import time  # line 1
import traceback  # line 1
import unittest  # line 1
StringIO = (__import__("StringIO" if sys.version_info.major < 3 else "io")).StringIO  # enables import via ternary expression  # line 2
try:  # Py3  # line 3
    from unittest import mock  # Py3  # line 3
except:  # installed via pip  # line 4
    import mock  # installed via pip  # line 4
try:  # only required for mypy  # line 5
    from typing import Any  # only required for mypy  # line 5
    from typing import Dict  # only required for mypy  # line 5
    from typing import FrozenSet  # only required for mypy  # line 5
    from typing import IO  # only required for mypy  # line 5
    from typing import List  # only required for mypy  # line 5
    from typing import Set  # only required for mypy  # line 5
    from typing import Tuple  # only required for mypy  # line 5
    from typing import Type  # only required for mypy  # line 5
    from typing import TypeVar  # only required for mypy  # line 5
    from typing import Union  # only required for mypy  # line 5
except:  # Python 2  # line 6
    pass  # Python 2  # line 6
try:  # optional dependency  # line 7
    import configr  # optional dependency  # line 7
except:  # declare as undefined  # line 8
    configr = None  # declare as undefined  # line 8

from sos import sos  # line 10

testFolder = os.path.abspath(os.path.join(os.getcwd(), "test"))  # line 12

@_coconut_tco  # line 14
def debugTestRunner(post_mortem=None):  # line 14
    ''' Unittest runner doing post mortem debugging on failing tests. '''  # line 15
    import pdb  # line 16
    if post_mortem is None:  # line 17
        post_mortem = pdb.post_mortem  # line 17
    class DebugTestResult(unittest.TextTestResult):  # line 18
        def addError(self, test, err):  # called before tearDown()  # line 19
            traceback.print_exception(*err)  # line 20
            post_mortem(err[2])  # line 21
            super(DebugTestResult, self).addError(test, err)  # line 22
        def addFailure(self, test, err):  # line 23
            traceback.print_exception(*err)  # line 24
            post_mortem(err[2])  # line 25
            super(DebugTestResult, self).addFailure(test, err)  # line 26
    return _coconut_tail_call(unittest.TextTestRunner, resultclass=DebugTestResult)  # line 27

def branchFolder(branch: 'int', revision: 'int') -> 'str':  # line 29
    return "." + os.sep + sos.metaFolder + os.sep + "b%d" % branch + os.sep + "r%d" % revision  # line 29


@_coconut_tco  # line 32
def wrapChannels(func: '_coconut.typing.Callable[..., Any]'):  # line 32
    ''' Wrap function call to capture and return strings emitted on stdout and stderr. '''  # line 33
    oldv, oldo, olde = sys.argv, sys.stdout, sys.stderr  # line 34
    buf = StringIO()  # line 35
    sys.stdout = sys.stderr = buf  # line 36
    handler = logging.StreamHandler(buf)  # line 37
    logging.getLogger().addHandler(handler)  # line 38
    try:  # capture output into buf  # line 39
        func()  # capture output into buf  # line 39
    except Exception as E:  # line 40
        buf.write(str(E) + "\n")  # line 40
        traceback.print_exc(file=buf)  # line 40
    logging.getLogger().removeHandler(handler)  # line 41
    sys.argv, sys.stdout, sys.stderr = oldv, oldo, olde  # line 42
    return _coconut_tail_call(buf.getvalue)  # line 43

def mockInput(datas: '_coconut.typing.Sequence[str]', func) -> 'Any':  # line 45
    with mock.patch('builtins.input' if sys.version_info.major >= 3 else '__builtin__.raw_input', side_effect=datas):  # line 46
        return func()  # line 46


class Tests(unittest.TestCase):  # line 49
    ''' Entire test suite. '''  # line 50

    def setUp(_):  # line 52
        for entry in os.listdir(testFolder):  # cannot remove testFolder on Windows when using TortoiseSVN as VCS  # line 53
            resource = os.path.join(testFolder, entry)  # line 54
            try:  # line 55
                os.unlink(resource)  # line 55
            except:  # line 56
                shutil.rmtree(resource)  # line 56
        os.chdir(testFolder)  # line 57

    def tearDown(_):  # line 59
        pass  # line 60

    def assertAllIn(_, what, where):  # line 62
        ''' Helper assert. '''  # line 63
        [_.assertIn(w, where) for w in what]  # line 64

    def assertInAll(_, what, where):  # line 66
        [_.assertIn(what, w) for w in where]  # line 67

    def createFile(_, number: 'Union[int, str]', contents: 'str'="x" * 10, prefix: '_coconut.typing.Optional[str]'=None) -> 'None':  # line 69
        with open(("." if prefix is None else prefix) + os.sep + (("file%d" % number) if isinstance(number, int) else number), "wb") as fd:  # line 70
            fd.write(contents if isinstance(contents, bytes) else contents.encode("cp1252"))  # line 70

    def existsFile(_, number: 'int', expectedContents: 'str'=None) -> 'bool':  # line 72
        if not os.path.exists("." + os.sep + "file%d" % number):  # line 73
            return False  # line 73
        if expectedContents is None:  # line 74
            return True  # line 74
        with open("." + os.sep + "file%d" % number, "wb") as fd:  # line 75
            return fd.read() == expectedContents  # line 75

    def testAccessor(_):  # line 77
        a = sos.Accessor({"a": 1})  # line 78
        _.assertEqual((1, 1), (a["a"], a.a))  # line 79

    def testFirstofmap(_):  # line 81
        _.assertEqual(2, sos.firstOfMap({"a": 1, "b": 2}, ["x", "b"]))  # line 82
        _.assertIsNone(sos.firstOfMap({"a": 1, "b": 2}, []))  # line 83

    def testFindChanges(_):  # line 85
        m = sos.Metadata(os.getcwd())  # line 86
        m.loadBranches()  # line 87
        _.createFile(1, "1")  # line 88
        m.createBranch(0)  # line 89
        _.assertEqual(1, len(m.paths))  # line 90
        time.sleep(1.1)  # time required by filesystem time resolution issues  # line 91
        _.createFile(1, "2")  # line 92
        _.createFile(2, "2")  # line 93
        changes = m.findChanges()  # detect time skew  # line 94
        _.assertEqual(1, len(changes.additions))  # line 95
        _.assertEqual(0, len(changes.deletions))  # line 96
        _.assertEqual(1, len(changes.modifications))  # line 97
        m.integrateChangeset(changes)  # line 98
        _.createFile(2, "12")  # modify file  # line 99
        changes = m.findChanges(0, 1)  # by size, creating new commit  # line 100
        _.assertEqual(0, len(changes.additions))  # line 101
        _.assertEqual(0, len(changes.deletions))  # line 102
        _.assertEqual(1, len(changes.modifications))  # line 103
        _.assertTrue(os.path.exists(branchFolder(0, 1)))  # line 104
        _.assertTrue(os.path.exists(branchFolder(0, 1) + os.sep + "03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2"))  # line 105

    def testDiffFunc(_):  # line 107
        a = {"./a": sos.PathInfo("", 0, 0, "")}  # line 108
        b = {"./a": sos.PathInfo("", 0, 0, "")}  # line 109
        changes = sos.diffPathSets(a, b)  # line 110
        _.assertEqual(0, len(changes.additions))  # line 111
        _.assertEqual(0, len(changes.deletions))  # line 112
        _.assertEqual(0, len(changes.modifications))  # line 113
        b = {"./a": sos.PathInfo("", 1, 0, "")}  # line 114
        changes = sos.diffPathSets(a, b)  # line 115
        _.assertEqual(0, len(changes.additions))  # line 116
        _.assertEqual(0, len(changes.deletions))  # line 117
        _.assertEqual(1, len(changes.modifications))  # line 118
        b = {}  # diff contains no entries -> no change  # line 119
        changes = sos.diffPathSets(a, b)  # line 120
        _.assertEqual(0, len(changes.additions))  # line 121
        _.assertEqual(0, len(changes.deletions))  # line 122
        _.assertEqual(0, len(changes.modifications))  # line 123
        b = {"./a": sos.PathInfo("", None, 1, "")}  # in diff marked as deleted  # line 124
        changes = sos.diffPathSets(a, b)  # line 125
        _.assertEqual(0, len(changes.additions))  # line 126
        _.assertEqual(1, len(changes.deletions))  # line 127
        _.assertEqual(0, len(changes.modifications))  # line 128
        b = {"./b": sos.PathInfo("", 1, 1, "")}  # line 129
        changes = sos.diffPathSets(a, b)  # line 130
        _.assertEqual(1, len(changes.additions))  # line 131
        _.assertEqual(0, len(changes.deletions))  # line 132
        _.assertEqual(0, len(changes.modifications))  # line 133
        a = {"./a": sos.PathInfo("", None, 0, "")}  # mark as deleted  # line 134
        b = {"./a": sos.PathInfo("", 1, 0, "")}  # re-added  # line 135
        changes = sos.diffPathSets(a, b)  # line 136
        _.assertEqual(1, len(changes.additions))  # line 137
        _.assertEqual(0, len(changes.deletions))  # line 138
        _.assertEqual(0, len(changes.modifications))  # line 139
        changes = sos.diffPathSets(b, a)  # line 140
        _.assertEqual(0, len(changes.additions))  # line 141
        _.assertEqual(1, len(changes.deletions))  # line 142
        _.assertEqual(0, len(changes.modifications))  # line 143

    def testComputeSequentialPathSet(_):  # line 145
        os.makedirs(branchFolder(0, 0))  # line 146
        os.makedirs(branchFolder(0, 1))  # line 147
        os.makedirs(branchFolder(0, 2))  # line 148
        os.makedirs(branchFolder(0, 3))  # line 149
        os.makedirs(branchFolder(0, 4))  # line 150
        m = sos.Metadata(os.getcwd())  # line 151
        m.branch = 0  # line 152
        m.commit = 2  # line 153
        m.saveBranches()  # line 154
        m.paths = {"./a": sos.PathInfo("", 0, 0, "")}  # line 155
        m.saveCommit(0, 0)  # initial  # line 156
        m.paths["./a"] = sos.PathInfo("", 1, 0, "")  # line 157
        m.saveCommit(0, 1)  # mod  # line 158
        m.paths["./b"] = sos.PathInfo("", 0, 0, "")  # line 159
        m.saveCommit(0, 2)  # add  # line 160
        m.paths["./a"] = sos.PathInfo("", None, 0, "")  # line 161
        m.saveCommit(0, 3)  # del  # line 162
        m.paths["./a"] = sos.PathInfo("", None, 0, "")  # line 163
        m.saveCommit(0, 4)  # readd  # line 164
        m.commits = {i: sos.CommitInfo(i, 0, None) for i in range(5)}  # line 165
        m.saveBranch(0)  # line 166
        m.computeSequentialPathSet(0, 4)  # line 167
        _.assertEqual(2, len(m.paths))  # line 168

    def testParseRevisionString(_):  # line 170
        m = sos.Metadata(os.getcwd())  # line 171
        m.branch = 1  # line 172
        m.commits = {0: 0, 1: 1, 2: 2}  # line 173
        _.assertEqual((1, 3), m.parseRevisionString("3"))  # line 174
        _.assertEqual((2, 3), m.parseRevisionString("2/3"))  # line 175
        _.assertEqual((1, -1), m.parseRevisionString(None))  # line 176
        _.assertEqual((2, -1), m.parseRevisionString("2/"))  # line 177
        _.assertEqual((1, -2), m.parseRevisionString("/-2"))  # line 178

    def testOfflineEmpty(_):  # line 180
        os.mkdir("." + os.sep + sos.metaFolder)  # line 181
        try:  # line 182
            sos.offline("trunk")  # line 182
            _.fail()  # line 182
        except SystemExit:  # line 183
            pass  # line 183
        os.rmdir("." + os.sep + sos.metaFolder)  # line 184
        sos.offline("test")  # line 185
        _.assertIn(sos.metaFolder, os.listdir("."))  # line 186
        _.assertAllIn(["b0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder))  # line 187
        _.assertAllIn(["r0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 188
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder)))  # only branch folder and meta data file  # line 189
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0")))  # only commit folder and meta data file  # line 190
        _.assertEqual(1, len(os.listdir(branchFolder(0, 0))))  # only meta data file  # line 191

    def testOfflineWithFiles(_):  # line 193
        _.createFile(1, "x" * 100)  # line 194
        _.createFile(2)  # line 195
        sos.offline("test")  # line 196
        _.assertAllIn(["file1", "file2", sos.metaFolder], os.listdir("."))  # line 197
        _.assertAllIn(["b0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder))  # line 198
        _.assertAllIn(["r0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 199
        _.assertAllIn([sos.metaFile, "03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2", "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa"], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0" + os.sep + "r0"))  # line 200
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder)))  # only branch folder and meta data file  # line 201
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0")))  # only commit folder and meta data file  # line 202
        _.assertEqual(3, len(os.listdir(branchFolder(0, 0))))  # only meta data file plus branch base file copies  # line 203

    def testBranch(_):  # line 205
        _.createFile(1, "x" * 100)  # line 206
        _.createFile(2)  # line 207
        sos.offline("test")  # b0/r0  # line 208
        sos.branch("other")  # b1/r0  # line 209
        _.assertAllIn(["b0", "b1", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder))  # line 210
        _.assertEqual(list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))), list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b1"))))  # line 211
        _.assertEqual(list(sorted(os.listdir(branchFolder(0, 0)))), list(sorted(os.listdir(branchFolder(1, 0)))))  # line 213
        _.createFile(1, "z")  # modify file  # line 215
        sos.branch()  # b2/r0  branch to unnamed branch with modified file tree contents  # line 216
        _.assertNotEqual(os.stat("." + os.sep + sos.metaFolder + os.sep + "b1" + os.sep + "r0" + os.sep + "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa").st_size, os.stat("." + os.sep + sos.metaFolder + os.sep + "b2" + os.sep + "r0" + os.sep + "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa").st_size)  # line 217
        _.createFile(3, "z")  # line 219
        sos.branch("from_last_revision", ["--last", "--stay"])  # b3/r0 create copy of other file1,file2 and don't switch  # line 220
        _.assertEqual(list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b3" + os.sep + "r0"))), list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b2" + os.sep + "r0"))))  # line 221
# Check sos.status output which branch is marked


    def testComittingAndChanges(_):  # line 226
        _.createFile(1, "x" * 100)  # line 227
        _.createFile(2)  # line 228
        sos.offline("test")  # line 229
        changes = sos.changes()  # line 230
        _.assertEqual(0, len(changes.additions))  # line 231
        _.assertEqual(0, len(changes.deletions))  # line 232
        _.assertEqual(0, len(changes.modifications))  # line 233
        _.createFile(1, "z")  # line 234
        changes = sos.changes()  # line 235
        _.assertEqual(0, len(changes.additions))  # line 236
        _.assertEqual(0, len(changes.deletions))  # line 237
        _.assertEqual(1, len(changes.modifications))  # line 238
        sos.commit("message")  # line 239
        _.assertAllIn(["r0", "r1", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 240
        _.assertAllIn([sos.metaFile, "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa"], os.listdir(branchFolder(0, 1)))  # line 241
        _.assertEqual(2, len(os.listdir(branchFolder(0, 1))))  # no further files, only the modified one  # line 242
        _.assertEqual(1, len(sos.changes("/0").modifications))  # vs. implicit (same) branch revision  # line 243
        _.assertEqual(1, len(sos.changes("0/0").modifications))  # vs. explicit branch revision  # line 244
        _.createFile(1, "")  # create empty file, mentioned in meta data, but not stored as own file  # line 245
        _.assertEqual(0, len(changes.additions))  # line 246
        _.assertEqual(0, len(changes.deletions))  # line 247
        _.assertEqual(1, len(changes.modifications))  # line 248
        sos.commit("modified")  # line 249
        _.assertEqual(1, len(os.listdir(branchFolder(0, 2))))  # no further files, only the modified one  # line 250
        try:  # expecting Exit due to no changes  # line 251
            sos.commit("nothing")  # expecting Exit due to no changes  # line 251
            _.fail()  # expecting Exit due to no changes  # line 251
        except:  # line 252
            pass  # line 252

    def testSwitch(_):  # line 254
        _.createFile(1, "x" * 100)  # line 255
        _.createFile(2, "y")  # line 256
        sos.offline("test")  # file1-2  in initial branch commit  # line 257
        sos.branch("second")  # file1-2  switch, having same files  # line 258
        sos.switch("test")  # no change  switch back, no problem  # line 259
        sos.switch("second")  # no change  # switch back, no problem  # line 260
        _.createFile(3, "y")  # generate a file  # line 261
        try:  # uncommited changes detected  # line 262
            sos.switch("test")  # uncommited changes detected  # line 262
            _.fail()  # uncommited changes detected  # line 262
        except SystemExit:  # line 263
            pass  # line 263
        sos.commit("Finish")  # file1-3  commit third file into branch second  # line 264
        sos.changes()  # line 265
        sos.switch("test")  # file1-2, remove file3 from file tree  # line 266
        _.assertFalse(_.existsFile(3))  # removed when switching back to test  # line 267
        _.createFile(4, "xy")  # generate a file  # line 268
        sos.switch("second", "--force")  # avoids warning on uncommited changes, but keeps file4  # line 269
        _.assertFalse(_.existsFile(4))  # removed when forcedly switching back to test  # line 270
        _.assertTrue(_.existsFile(3))  # was restored from branch's revision r1  # line 271
        os.unlink("." + os.sep + "file1")  # remove old file1  # line 272
        sos.switch("test", "--force")  # should restore file1 and remove file3  # line 273
        _.assertTrue(_.existsFile(1))  # was restored from branch's revision r1  # line 274
        _.assertFalse(_.existsFile(3))  # was restored from branch's revision r1  # line 275

    def testAutoDetectVCS(_):  # line 277
        os.mkdir(".git")  # line 278
        sos.offline(sos.vcsBranches[sos.findSosVcsBase()[2]])  # create initial branch  # line 279
        with open(sos.metaFolder + os.sep + sos.metaFile, "r") as fd:  # line 280
            meta = fd.read()  # line 280
        _.assertTrue("\"master\"" in meta)  # line 281
        os.rmdir(".git")  # line 282

    def testUpdate(_):  # line 284
        sos.offline("trunk")  # create initial branch b0/r0  # line 285
        _.createFile(1, "x" * 100)  # line 286
        sos.commit("second")  # create b0/r1  # line 287

        sos.switch("/0")  # go back to b0/r0 - deletes file1  # line 289
        _.assertFalse(_.existsFile(1))  # line 290

        sos.update("/1")  # recreate file1  # line 292
        _.assertTrue(_.existsFile(1))  # line 293

        sos.commit("third", ["--force"])  # force because nothing to commit. should create r2 with same contents as r1, but as differential from r1, not from r0 (= no changes in meta folder)  # line 295
        _.assertTrue(os.path.exists(branchFolder(0, 2)))  # line 296
        _.assertTrue(os.path.exists(branchFolder(0, 2) + os.sep + sos.metaFile))  # line 297
        _.assertEqual(1, len(os.listdir(branchFolder(0, 2))))  # only meta data file, no differential files  # line 298

        sos.update("/1")  # do nothing, as nothing has changed  # line 300
        _.assertTrue(_.existsFile(1))  # line 301

        _.createFile(2, "y" * 100)  # line 303
#    out = wrapChannels(lambda: sos.branch("other"))  # won't comply as there are changes
#    _.assertIn("--force", out)
        sos.branch("other", ["--force"])  # automatically including file 2 (as we are in simple mode)  # line 306
        _.assertTrue(_.existsFile(2))  # line 307
        sos.update("trunk", ["--add"])  # only add stuff  # line 308
        _.assertTrue(_.existsFile(2))  # line 309
        sos.update("trunk")  # nothing to do  # line 310
        _.assertFalse(_.existsFile(2))  # removes file not present in original branch  # line 311

        theirs = b"a\nb\nc\nd\ne\nf\ng\nh\nx\nx\nj\nk"  # line 313
        _.createFile(10, theirs)  # line 314
        mine = b"a\nc\nd\ne\ng\nf\nx\nh\ny\ny\nj"  # missing "b", inserted g, modified g->x, replace x/x -> y/y, removed k  # line 315
        _.createFile(11, mine)  # line 316
        _.assertEqual(b"a\nb\nc\nd\ne\nf\ng\nh\nx\nx\nj\nk", sos.merge(filename="." + os.sep + "file10", intoname="." + os.sep + "file11", mergeOperation=sos.MergeOperation.BOTH, conflictResolution=sos.ConflictResolution.THEIRS))  # completely recreated other file  # line 317
        _.assertEqual(b"a\nb\nc\nd\ne\ng\nf\ng\nx\nh\nx\nx\ny\ny\nj\nk", sos.merge(filename="." + os.sep + "file10", intoname="." + os.sep + "file11", mergeOperation=sos.MergeOperation.INSERT, conflictResolution=sos.ConflictResolution.MINE))  # line 318

    def testEolDet(_):  # line 320
        _.assertEqual(b"\n", sos.eoldet(b"a\nb"))  # line 321
        _.assertEqual(b"\r\n", sos.eoldet(b"a\r\nb\r\n"))  # line 322
        _.assertIsNone(sos.eoldet(b""))  # line 323
        _.assertIsNone(sos.eoldet(b"sdf"))  # line 324

    def testMerge(_):  # line 326
        a = b"a\nb\ncc\nd"  # line 327
        b = b"a\nb\nee\nd"  # line 328
        _.assertEqual(b"a\nb\ncc\nee\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT))  # means insert changes from a into b, but don't replace  # line 329
        _.assertEqual(b"a\nb\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.REMOVE))  # line 330
        _.assertEqual(b"a\nb\ncc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.BOTH))  # line 331
# Now test intra-line merging without conflicts
        _.assertEqual(b"a\nbc d\ne", sos.merge(b"a\nbc d\ne", b"a\nbcd\ne", mergeOperation=sos.MergeOperation.INSERT))  # because it's a deletion ['  a', '- bc d', '?   -\n', '+ bcd', '  e']  # line 333
        _.assertEqual(b"a\nbcd\ne", sos.merge(b"a\nbc d\ne", b"a\nbcd\ne", mergeOperation=sos.MergeOperation.REMOVE))  # ['  a', '- bc d', '?   -\n', '+ bcd', '  e']  # line 334
        _.assertEqual(b"a\nbc d\ne", sos.merge(b"a\nbcd\ne", b"a\nbc d\ne", mergeOperation=sos.MergeOperation.INSERT))  # nothing to insert  # line 335
        _.assertEqual(b"a\nbcd\ne", sos.merge(b"a\nbcd\ne", b"a\nbc d\ne", mergeOperation=sos.MergeOperation.REMOVE))  # remove space  # line 336
# Test with change + insert (conflict)
        _.assertEqual(b"a\nb fdd d\ne", sos.merge(b"a\nb cd d\ne", b"a\nb fdd d\ne", conflictResolution=sos.ConflictResolution.MINE))  # line 338
        _.assertEqual(b"a\nb cd d\ne", sos.merge(b"a\nb cd d\ne", b"a\nb fdd d\ne", conflictResolution=sos.ConflictResolution.THEIRS))  # ['  a', '- b cd d', '?   ^\n', '+ b fdd d', '?   ^^\n', '  e']  # line 339
        _.assertEqual(b"a\nb fdd d\ne", mockInput(["i"], lambda : sos.merge(b"a\nb cd d\ne", b"a\nb fdd d\ne", conflictResolution=sos.ConflictResolution.ASK)))  # ['  a', '- b cd d', '?   ^\n', '+ b fdd d', '?   ^^\n', '  e']  # line 340
        _.assertEqual(b"a\nb cd d\ne", mockInput(["t"], lambda : sos.merge(b"a\nb cd d\ne", b"a\nb fdd d\ne", conflictResolution=sos.ConflictResolution.ASK)))  # ['  a', '- b cd d', '?   ^\n', '+ b fdd d', '?   ^^\n', '  e']  # line 341
        _.assertEqual(b"abbc", sos.merge(b"abbc", b"addc", mergeOperation=sos.MergeOperation.BOTH, conflictResolution=sos.ConflictResolution.THEIRS))  # line 342
        _.assertEqual(b"a\nbb\nc", sos.merge(b"a\nbb\nc", b"a\ndd\nc", mergeOperation=sos.MergeOperation.BOTH, conflictResolution=sos.ConflictResolution.THEIRS))  # line 343
        _.assertIn("Differing EOL-styles", wrapChannels(lambda : sos.merge(b"a\nb", b"a\r\nb")))  # expect warning  # line 344
        _.assertIn(b"a\r\nb", sos.merge(b"a\nb", b"a\r\nb"))  # in doubt, use "mine" CR-LF  # line 345

    def testPickyMode(_):  # line 347
        sos.offline("trunk", ["--picky"])  # line 348
        sos.add("file?", ["--force"])  # line 349
        _.createFile(1, "aa")  # line 350
        sos.commit("First")  # add one file  # line 351
        _.assertEqual(2, len(os.listdir(branchFolder(0, 1))))  # line 352
        _.createFile(2, "b")  # line 353
        sos.commit("Second", ["--force"])  # add nothing, because picky  # line 354
        _.assertEqual(1, len(os.listdir(branchFolder(0, 2))))  # line 355
        sos.add("file?")  # line 356
        sos.commit("Third")  # add nothing, because picky  # line 357
        _.assertEqual(2, len(os.listdir(branchFolder(0, 3))))  # line 358

    def testTrackedSubfolder(_):  # line 360
        os.mkdir("." + os.sep + "sub")  # line 361
        sos.offline("trunk", ["--track"])  # line 362
        _.createFile(1, "x")  # line 363
        _.createFile(1, "x", prefix="sub")  # line 364
        sos.add("file?")  # add glob pattern to track  # line 365
        sos.commit("First")  # line 366
        _.assertEqual(2, len(os.listdir(branchFolder(0, 1))))  # one new file + meta file  # line 367
        sos.add("sub/file?")  # add glob pattern to track  # line 368
        sos.commit("Second")  # one new file + meta  # line 369
        _.assertEqual(2, len(os.listdir(branchFolder(0, 1))))  # one new file + meta file  # line 370
        os.unlink("file1")  # remove from basefolder  # line 371
        _.createFile(2, "y")  # line 372
        sos.rm("sub/file?")  # line 373
        sos.commit("Third")  # line 374
        _.assertEqual(2, len(os.listdir(branchFolder(0, 2))))  # one new file + meta  # line 375
# TODO check if /file1 and sub/file1 were removed from index

    def testTrackedMode(_):  # line 378
        ''' Difference in semantics vs simple mode:
          - For remote/other branch we can only know and consider tracked files, thus ignoring all complexity stemming from handling addition of untracked files.
          - For current branch, we can take into account tracked and untracked ones, in theory, but it doesn't make sense.
        In conclusion, using the union of tracking patterns from both sides to find affected files makes sense, but disallow deleting files not present in remote branch.
    '''  # line 383
        sos.offline("test", options=["--track"])  # set up repo in tracking mode (SVN- or gitless-style)  # line 384
        _.createFile(1)  # line 385
        _.createFile("a123a")  # untracked file "a123a"  # line 386
        sos.add("file?")  # add glob tracking pattern  # line 387
        sos.commit("second")  # versions "file1"  # line 388
        _.assertEqual(2, len(os.listdir(branchFolder(0, 1))))  # one new file + meta file  # line 389

        _.createFile(2)  # untracked file "file2"  # line 391
        sos.commit("third")  # versions "file2"  # line 392
        _.assertEqual(2, len(os.listdir(branchFolder(0, 2))))  # one new file + meta file  # line 393

        os.mkdir("." + os.sep + "sub")  # line 395
        _.createFile(3, prefix="sub")  # untracked file "sub/file3"  # line 396
        sos.commit("fourth", ["--force"])  # no tracking pattern matches the subfolder  # line 397
        _.assertEqual(1, len(os.listdir(branchFolder(0, 3))))  # meta file only, no other tracked path/file  # line 398

        sos.branch("Other")  # second branch containing file1 and file2 tracked by "./file?"  # line 400
        sos.rm("file?")  # remove tracking pattern, but don't touch previously created and versioned files  # line 401
        sos.add("a*a")  # add tracking pattern  # line 402
        changes = sos.changes()  # should pick up addition  # line 403
        _.assertEqual(0, len(changes.modifications))  # line 404
        _.assertEqual(0, len(changes.deletions))  # not tracked anymore, but contained in version history and not removed  # line 405
        _.assertEqual(1, len(changes.additions))  # detected one addition "a123a", but won't recognize untracking files as deletion  # line 406

        sos.commit("Second_2")  # line 408
        _.assertEqual(2, len(os.listdir(branchFolder(1, 1))))  # "a123a" + meta file  # line 409
        _.assertTrue(os.path.exists("." + os.sep + "file1"))  # line 410
        _.assertTrue(os.path.exists("." + os.sep + "file2"))  # line 411

        sos.switch("test")  # go back to first branch - tracks only "file?", but not "a*a"  # line 413
        _.assertTrue(os.path.exists("." + os.sep + "file1"))  # line 414
        _.assertTrue(os.path.exists("." + os.sep + "a123a"))  # should not have been touched so far  # line 415

        sos.update("Other")  # integrate tracked files and tracking pattern from second branch into working state of master branch  # line 417
        _.assertTrue(os.path.exists("." + os.sep + "file1"))  # line 418
        _.assertTrue(os.path.exists("." + os.sep + "a123a"))  # line 419

        _.createFile("axxxa")  # new file that should be tracked on "test" now that we integrated "Other"  # line 421
        sos.commit("fifth")  # create new revision after integrating updates from second branch  # line 422
        _.assertEqual(3, len(os.listdir(branchFolder(0, 4))))  # one new file from other branch + one new in current folder + meta file  # line 423
        sos.switch("Other")  # switch back to just integrated branch that tracks only "a*a" - shouldn't do anything  # line 424
        _.assertTrue(os.path.exists("." + os.sep + "file1"))  # line 425
        _.assertTrue(os.path.exists("." + os.sep + "a123a"))  # line 426
        _.assertFalse(os.path.exists("." + os.sep + "axxxa"))  # because tracked in both branches, but not present in other -> delete in file tree TODO document  # line 427
# TODO test switch --meta

    def testLs(_):  # line 430
        sos.offline("test", options=["--track"])  # set up repo in tracking mode (SVN- or gitless-style)  # line 431
        _.createFile(1)  # line 432
        _.createFile("foo")  # line 433
        sos.add("file*")  # capture one file  # line 434
        out = sos.safeSplit(wrapChannels(lambda : sos.ls()).replace("\r", ""), "\n")  # line 435
        _.assertEqual('TRK file1 by "./file*"', out[0][-22:])  # line 436
        _.assertEqual("    foo", out[1][-7:])  # line 437

    def testWhitelist(_):  # line 439
# TODO do same for simple mode, easy
        _.createFile(1)  # line 441
        sos.defaults.ignores[:] = ["file*"]  # replace in-place  # line 442
        sos.offline("xx", ["--track"])  # because nothing to commit due to ignore pattern  # line 443
        sos.add("file*")  # line 444
        sos.commit(options=["--force"])  # attempt to commit the file  # line 445
        _.assertEqual(1, len(os.listdir(branchFolder(0, 1))))  # only meta data, file1 was ignored  # line 446
        sos.online(["--force"])  # line 447
        _.assertFalse(os.path.exists(sos.metaFolder))  # line 448
        _.createFile(1)  # line 449
        sos.defaults.ignoresWhitelist[:] = ["file*"]  # line 450
        sos.offline("xx", ["--track"])  # line 451
        sos.add("file*")  # line 452
        sos.commit()  # line 453
        _.assertEqual(2, len(os.listdir(branchFolder(0, 1))))  # meta data and "file1", file1 was whitelisted  # line 454

    def testRemove(_):  # line 456
        _.createFile(1, "x" * 100)  # line 457
        sos.offline("trunk")  # line 458
        try:  # line 459
            sos.delete("trunk")  # line 459
            _fail()  # line 459
        except:  # line 460
            pass  # line 460
        _.createFile(2, "y" * 10)  # line 461
        sos.branch("added")  # line 462
        sos.delete("trunk")  # line 463
        _.assertEqual(2, len(os.listdir(sos.metaFolder)))  # meta data file and "b1"  # line 464
        _.assertTrue(os.path.exists("." + os.sep + sos.metaFolder + os.sep + "b1"))  # line 465
        sos.branch("next")  # line 466
        _.createFile(3, "y" * 10)  # make a change  # line 467
        sos.delete("added", "--force")  # should succeed  # line 468

    def testDiff(_):  # line 470
# Need to test stdout diffs
        pass  # line 472

    def testFindBase(_):  # line 474
        old = os.getcwd()  # line 475
        try:  # line 476
            os.mkdir("." + os.sep + ".git")  # line 477
            os.makedirs("." + os.sep + "a" + os.sep + sos.metaFolder)  # line 478
            os.makedirs("." + os.sep + "a" + os.sep + "b")  # line 479
            os.chdir("a" + os.sep + "b")  # line 480
            s, vcs, cmd = sos.findSosVcsBase()  # line 481
            _.assertIsNotNone(s)  # line 482
            _.assertIsNotNone(vcs)  # line 483
            _.assertEqual("git", cmd)  # line 484
        finally:  # line 485
            os.chdir(old)  # line 485


if __name__ == '__main__':  # line 488
    logging.basicConfig(level=logging.DEBUG if '-v' in sys.argv or os.getenv("DEBUG", "false") == "true" else logging.INFO, stream=sys.stderr, format="%(asctime)-23s %(levelname)-8s %(name)s:%(lineno)d | %(message)s" if '-v' in sys.argv or os.getenv("DEBUG", "false") == "true" else "%(message)s")  # line 489
    if configr:  # line 490
        c = configr.Configr("sos")  # line 491
        c.loadSettings()  # line 491
        if len(c.keys()) > 0:  # line 492
            sos.Exit("Cannot run test suite with local SOS user configuration")  # line 492
    unittest.main(testRunner=debugTestRunner() if '-v' in sys.argv and not os.getenv("BUILD", "false").lower() == "true" else None)  # warnings = "ignore")  # line 493
