#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x26b58554

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
import difflib  # line 2
import fnmatch  # line 2
import hashlib  # line 2
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
try:  # line 7
    from sos import version  # line 7
except:  # line 8
    import version  # line 8

# External dependencies
try:  # optional dependency  # line 11
    import configr  # optional dependency  # line 11
except:  # declare as undefined  # line 12
    configr = None  # declare as undefined  # line 12
#from enforce import runtime_validation  # https://github.com/RussBaz/enforce  TODO doesn't work for "data" types
UTF8 = "utf_8"  # early used constant, not defined in standard library  # line 14
try:  # line 15
    import chardet  # https://github.com/chardet/chardet  # line 16
    def detect(binary: 'bytes') -> 'str':  # line 17
        return chardet.detect(binary)["encoding"]  # line 17
except:  # Python 2 workaround  # line 18
    def detect(binary: 'bytes') -> 'str':  # Guess the encoding  # line 19
        try:  # line 20
            binary.decode(UTF8)  # line 20
            return UTF8  # line 20
        except UnicodeError:  # line 21
            pass  # line 21
        try:  # line 22
            binary.decode("utf_16")  # line 22
            return "utf_16"  # line 22
        except UnicodeError:  # line 23
            pass  # line 23
        try:  # line 24
            binary.decode("cp1252")  # line 24
            return "cp1252"  # line 24
        except UnicodeError:  # line 25
            pass  # line 25
        return "ascii"  # this code will never be reached, as above is an 8-bit charset that always matches  # line 26


class BranchInfo(_coconut_NamedTuple("BranchInfo", [("number", 'int'), ("ctime", 'int'), ("name", '_coconut.typing.Optional[str]'), ("insync", 'bool'), ("tracked", 'List[str]')])):  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 29
    __slots__ = ()  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 29
    __ne__ = _coconut.object.__ne__  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 29
    def __new__(_cls, number, ctime, name=None, insync=False, tracked=[]):  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 29
        return _coconut.tuple.__new__(_cls, (number, ctime, name, insync, tracked))  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 29
# tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place
class CommitInfo(_coconut_NamedTuple("CommitInfo", [("number", 'int'), ("ctime", 'int'), ("message", '_coconut.typing.Optional[str]')])):  # line 30
    __slots__ = ()  # line 30
    __ne__ = _coconut.object.__ne__  # line 30
    def __new__(_cls, number, ctime, message=None):  # line 30
        return _coconut.tuple.__new__(_cls, (number, ctime, message))  # line 30

class PathInfo(_coconut_NamedTuple("PathInfo", [("namehash", 'str'), ("size", '_coconut.typing.Optional[int]'), ("mtime", 'int'), ("hash", 'str')])):  # size == None means deleted in this revision  # line 31
    __slots__ = ()  # size == None means deleted in this revision  # line 31
    __ne__ = _coconut.object.__ne__  # size == None means deleted in this revision  # line 31
class ChangeSet(_coconut_NamedTuple("ChangeSet", [("additions", 'Dict[str, PathInfo]'), ("deletions", 'Dict[str, PathInfo]'), ("modifications", 'Dict[str, PathInfo]')])):  # avoid default assignment of {} as it leads to runtime errors (contains data on init for unknown reason)  # line 32
    __slots__ = ()  # avoid default assignment of {} as it leads to runtime errors (contains data on init for unknown reason)  # line 32
    __ne__ = _coconut.object.__ne__  # avoid default assignment of {} as it leads to runtime errors (contains data on init for unknown reason)  # line 32
class Range(_coconut_NamedTuple("Range", [("tipe", 'int'), ("indexes", '_coconut.typing.Sequence[int]')])):  # MergeBlockType[1,2,4], line number, length  # line 33
    __slots__ = ()  # MergeBlockType[1,2,4], line number, length  # line 33
    __ne__ = _coconut.object.__ne__  # MergeBlockType[1,2,4], line number, length  # line 33
class MergeBlock(_coconut_NamedTuple("MergeBlock", [("tipe", 'int'), ("lines", '_coconut.typing.Sequence[str]'), ("line", 'int'), ("replaces", '_coconut.typing.Optional[MergeBlock]'), ("changes", '_coconut.typing.Optional[Range]')])):  # line 34
    __slots__ = ()  # line 34
    __ne__ = _coconut.object.__ne__  # line 34
    def __new__(_cls, tipe, lines, line, replaces=None, changes=None):  # line 34
        return _coconut.tuple.__new__(_cls, (tipe, lines, line, replaces, changes))  # line 34


class ConflictResolution:  # prefer their changes, prefer my changes, ask user for each change, go to next deeper level (e.g. from files to lines, characters)  # line 36
    THEIRS, MINE, ASK, NEXT = range(4)  # prefer their changes, prefer my changes, ask user for each change, go to next deeper level (e.g. from files to lines, characters)  # line 36
class MergeOperation:  # insert remote changes into current, remove remote deletions from current, do both (replicate remote state) TODO handle inline-operations separate?  # line 37
    INSERT, REMOVE, BOTH = 1, 2, 3  # insert remote changes into current, remove remote deletions from current, do both (replicate remote state) TODO handle inline-operations separate?  # line 37
class MergeBlockType:  # modify = intra-line changes  # line 38
    KEEP, INSERT, REMOVE, REPLACE, MODIFY, MOVE = range(6)  # modify = intra-line changes  # line 38

class Accessor(dict):  # line 40
    ''' Dictionary with attribute access. Writing only supported via dictionary access. '''  # line 41
    def __init__(_, mapping) -> 'None':  # line 42
        dict.__init__(_, mapping)  # line 42
    @_coconut_tco  # line 43
    def __getattribute__(_, name: 'str') -> 'List[str]':  # line 43
        try:  # line 44
            return _[name]  # line 44
        except:  # line 45
            return _coconut_tail_call(dict.__getattribute__, _, name)  # line 45

# Constants
APPNAME = "Subversion Offline Solution  V%s  (C) Arne Bachmann" % version.__release_version__  # type: str  # line 48
CONFIGURABLE_FLAGS = ["strict", "track", "picky", "compress"]  # line 49
CONFIGURABLE_LISTS = ["texttype", "bintype", "ignores", "ignoreDirs", "ignoresWhitelist", "ignoreDirsWhitelist"]  # line 50
TRUTH_VALUES = ["true", "yes", "on", "1", "enable", "enabled"]  # all lower-case normalized  # line 51
PROGRESS_MARKER = ["|", "/", "-", "\\"]  # line 52
metaFolder = ".sos"  # type: str  # line 53
metaFile = ".meta"  # type: str  # line 54
bufSize = 1 << 20  # type: int  # 1 MiB  # line 55
SVN = "svn"  # line 56
SLASH = "/"  # line 57
vcsFolders = {".svn": SVN, ".git": "git", ".bzr": "bzr", ".hg": "hg", ".fslckout": " fossil", ".CVS": "cvs"}  # type: Dict[str, str]  # line 58
vcsBranches = {SVN: "trunk", "git": "master", "bzr": "trunk", "hg": "default", "fossil": None, "cvs": None}  # type: Dict[str, _coconut.typing.Optional[str]]  # line 59
defaults = Accessor({"strict": False, "track": False, "picky": False, "compress": True, "texttype": [], "bintype": [], "ignoreDirs": [".*", "__pycache__"], "ignoreDirsWhitelist": [], "ignores": ["__coconut__.py", "*.bak", "*.py[cdo]", "*.class", ".fslckout"], "ignoresWhitelist": []})  # type: Accessor  # line 60

def Exit(message: 'str'="") -> 'None':  # line 62
    print(message, file=sys.stderr)  # line 62
    sys.exit(1)  # line 62

@_coconut_tco  # dynamic Python2/3. don't simplify, eval must be inside function for unknown reason  # line 64
def user_input(msg: 'str') -> 'str':  # dynamic Python2/3. don't simplify, eval must be inside function for unknown reason  # line 64
    return _coconut_tail_call(eval("input" if sys.version_info.major >= 3 else "raw_input"), msg)  # dynamic Python2/3. don't simplify, eval must be inside function for unknown reason  # line 64

try:  # line 66
    Splittable = TypeVar("Splittable", str, bytes)  # line 66
except:  # Python 2  # line 67
    pass  # Python 2  # line 67
def safeSplit(s: 'Splittable', d: '_coconut.typing.Optional[Splittable]'=None) -> '_coconut.typing.Sequence[Splittable]':  # line 68
    return s.split(("\n" if isinstance(s, str) else b"\n") if d is None else d) if len(s) > 0 else []  # line 68

def ajoin(sep: 'str', seq: '_coconut.typing.Sequence[str]', nl="") -> 'str':  # line 70
    return sep + (sep + nl).join(seq)  # line 70
@_coconut_tco  # line 71
def sjoin(*s: 'Tuple[Any]') -> 'str':  # line 71
    return _coconut_tail_call(" ".join, [str(e) for e in s if e != ''])  # line 71

@_coconut_tco  # line 73
def hashStr(datas: 'str') -> 'str':  # line 73
    return _coconut_tail_call(hashlib.sha256(datas.encode(UTF8)).hexdigest)  # line 73

@_coconut_tco  # line 75
def hashFile(path: 'str', compress: 'bool', saveTo: '_coconut.typing.Optional[str]'=None) -> 'str':  # line 75
    ''' Calculate hash of file contents. '''  # line 76
    hash = hashlib.sha256()  # line 77
    to = openIt(saveTo, "w", compress) if saveTo else None  # line 78
    with open(path, "rb") as fd:  # line 79
        while True:  # line 80
            buffer = fd.read(bufSize)  # line 81
            hash.update(buffer)  # line 82
            if to:  # line 83
                to.write(buffer)  # line 83
            if len(buffer) < bufSize:  # line 84
                break  # line 84
        if to:  # line 85
            to.close()  # line 85
    return _coconut_tail_call(hash.hexdigest)  # line 86

def firstOfMap(map: 'Dict[str, Any]', params: '_coconut.typing.Sequence[str]', default: 'Any'=None) -> 'Any':  # line 88
    ''' Utility. '''  # line 89
    for k, v in map.items():  # line 90
        if k in params:  # line 91
            return v  # line 91
    return default  # line 92

def loadConfig() -> 'Union[configr.Configr, Accessor]':  # Simplifies loading config from file system or returning the defaults  # line 94
    config = None  # type: Union[configr.Configr, Accessor]  # line 95
    if not configr:  # this only applies for the case that configr is not available, thus no settings will be persisted anyway  # line 96
        return defaults  # this only applies for the case that configr is not available, thus no settings will be persisted anyway  # line 96
    config = configr.Configr("sos", defaults=defaults)  # defaults are used if key is not configured, but won't be saved  # line 97
    f, g = config.loadSettings(clientCodeLocation=os.path.abspath(__file__), location=os.environ.get("TEST", None))  # line 98
    if f is None:  # line 99
        debug("Encountered a problem while loading the user configuration: %r" % g)  # line 99
    return config  # line 100

@_coconut_tco  # line 102
def saveConfig(c: 'configr.Configr') -> 'Tuple[_coconut.typing.Optional[str], _coconut.typing.Optional[Exception]]':  # line 102
    return _coconut_tail_call(c.saveSettings, clientCodeLocation=os.path.abspath(__file__), location=os.environ.get("TEST", None))  # line 103

@_coconut_tco  # line 105
def strftime(timestamp: '_coconut.typing.Optional[int]'=None) -> 'str':  # line 105
    return _coconut_tail_call(time.strftime, "%Y-%m-%d %H:%M:%S", time.localtime(timestamp / 1000. if timestamp is not None else None))  # line 105

def diffPathSets(last: 'Dict[str, PathInfo]', diff: 'Dict[str, PathInfo]') -> 'ChangeSet':  # line 107
    ''' Computes a changeset between in-memory and on-disk file lists.
      Additions contains PathInfo for entries in diff
      Deletions contains PathInfo for entries not anymore in diff
      Modifications contains PathInfo for entries changed from last to diff (new state)
  '''  # line 112
    changes = ChangeSet({}, {}, {})  # type: ChangeSet  # line 113
    for path, pinfo in last.items():  # line 114
        if path not in diff:  # now change  changes.deletions[path] = pinfo; continue  # line 115
            continue  # now change  changes.deletions[path] = pinfo; continue  # line 115
        vs = diff[path]  # reference to potentially changed path set  # line 116
        if vs.size is None:  # marked for deletion  # line 117
            changes.deletions[path] = pinfo  # marked for deletion  # line 117
            continue  # marked for deletion  # line 117
        if pinfo.size == None:  # re-added  # line 118
            changes.additions[path] = pinfo  # re-added  # line 118
            continue  # re-added  # line 118
        if pinfo.size != vs.size or pinfo.mtime != vs.mtime or pinfo.hash != vs.hash:  # not need to make hash comparison optional here  # line 119
            changes.modifications[path] = vs  # not need to make hash comparison optional here  # line 119
    for path, pinfo in diff.items():  # added loop  # line 120
        if path not in last:  # line 121
            changes.additions[path] = pinfo  # line 121
    assert not any([path in changes.deletions for path in changes.additions])  # invariant checks  # line 122
    assert not any([path in changes.additions for path in changes.deletions])  # line 123
    return changes  # line 124

try:  # line 126
    DataType = TypeVar("DataType", MergeBlock, BranchInfo)  # line 126
except:  # Python 2  # line 127
    pass  # Python 2  # line 127
@_coconut_tco  # line 128
def dataCopy(_tipe: 'Type[DataType]', _old: 'DataType', *_args, **_kwargs) -> 'DataType':  # line 128
    r = _old._asdict()  # line 128
    r.update(**_kwargs)  # line 128
    return _coconut_tail_call(makedata, _tipe, *(list(_args) + [r[field] for field in _old._fields]))  # line 128
# TODO test namedtuple instead of instantiated tuple types in "datatype"?

@_coconut_tco  # line 131
def getIntraLineMarkers(line: 'str') -> 'Range':  # line 131
    ''' Return (type, [affected indices]) of "? "-line diff markers ("? " suffix must be removed). '''  # line 132
    if "^" in line:  # line 133
        return _coconut_tail_call(Range, MergeBlockType.MODIFY, [i for i, c in enumerate(line) if c == "^"])  # line 133
    if "+" in line:  # line 134
        return _coconut_tail_call(Range, MergeBlockType.INSERT, [i for i, c in enumerate(line) if c == "+"])  # line 134
    if "-" in line:  # line 135
        return _coconut_tail_call(Range, MergeBlockType.REMOVE, [i for i, c in enumerate(line) if c == "-"])  # line 135
    return _coconut_tail_call(Range, MergeBlockType.KEEP, [])  # line 136

def detectAndLoad(filename: '_coconut.typing.Optional[str]'=None, content: '_coconut.typing.Optional[bytes]'=None) -> 'Tuple[str, bytes, _coconut.typing.Sequence[str]]':  # line 138
    encoding = None  # type: str  # line 139
    eol = None  # type: bytes  # line 139
    lines = []  # type: _coconut.typing.Sequence[str]  # line 139
    if filename is not None:  # line 140
        with open(filename, "rb") as fd:  # line 141
            content = fd.read()  # line 141
    encoding = (lambda _coconut_none_coalesce_item: sys.getdefaultencoding() if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(detect(content))  # line 142
    eol = eoldet(content)  # line 143
    if filename is not None:  # line 144
        with codecs.open(filename, encoding=encoding) as fd:  # line 145
            lines = safeSplit(fd.read(), (b"\n" if eol is None else eol).decode(encoding))  # line 145
    elif content is not None:  # line 146
        lines = safeSplit(content.decode(encoding), (b"\n" if eol is None else eol).decode(encoding))  # line 147
    else:  # line 148
        return (sys.getdefaultencoding(), b"\n", [])  # line 148
    return (encoding, eol, lines)  # line 149

def openIt(file: 'str', mode: 'str', compress: 'bool') -> 'IO':  # Abstraction for opening both compressed and plain files  # line 151
    return bz2.BZ2File(file, mode) if compress else open(file, mode + "b")  # Abstraction for opening both compressed and plain files  # line 151

def eoldet(file: 'bytes') -> '_coconut.typing.Optional[bytes]':  # line 153
    ''' Determine EOL style from a binary string. '''  # line 154
    lf = file.count(b"\n")  # type: int  # line 155
    cr = file.count(b"\r")  # type: int  # line 156
    crlf = file.count(b"\r\n")  # type: int  # line 157
    if crlf > 0:  # DOS/Windows/Symbian etc.  # line 158
        if lf != crlf or cr != crlf:  # line 159
            warn("Inconsistent CR/NL count. Mixed EOL style detected, may cause problems during merge")  # line 159
        return b"\r\n"  # line 160
    if lf != 0 and cr != 0:  # line 161
        warn("Inconsistent CR/NL count. Mixed EOL style detected, may cause problems during merge")  # line 161
    if lf > cr:  # Linux/Unix  # line 162
        return b"\n"  # Linux/Unix  # line 162
    if cr > lf:  # older 8-bit machines  # line 163
        return b"\r"  # older 8-bit machines  # line 163
    return None  # no new line contained, cannot determine  # line 164

def usage() -> 'None':  # line 166
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
    config  [set/unset/show/add/rm] [<param>] [<value>]   Configure user-global defaults.
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
                                  for offline: ignore being already offline, start from scratch (same as online --force; offline)
                                  for online: ignore uncommitted branches
                                  for commit, switch, update, add: ignore uncommitted changes before executing command
    --strict                    Perform full content comparison, don't rely only on file size and timestamp
                                  for offline: persist strict mode in repository
                                  for changes, diff, commit, switch, update, delete: perform operation in strict mode
    --{cmd}                       When executing {CMD} not being offline, pass arguments to {CMD} instead (e.g. {cmd} --{cmd} config set key value.)
    --log                       Enable internals logger
    --verbose                   Enable debugging output""".format(appname=APPNAME, cmd="sos", CMD="SOS"))  # line 218

@_coconut_tco  # line 220
def merge(file: '_coconut.typing.Optional[bytes]'=None, into: '_coconut.typing.Optional[bytes]'=None, filename: '_coconut.typing.Optional[str]'=None, intoname: '_coconut.typing.Optional[str]'=None, mergeOperation=MergeOperation.BOTH, conflictResolution=ConflictResolution.ASK) -> 'bytes':  # line 220
    ''' Merges binary text contents 'file' into file 'into', returning merged result. '''  # line 221
    encoding = None  # type: str  # line 222
    othr = None  # type: _coconut.typing.Sequence[str]  # line 222
    othreol = None  # type: _coconut.typing.Optional[bytes]  # line 222
    curr = None  # type: _coconut.typing.Sequence[str]  # line 222
    curreol = None  # type: _coconut.typing.Optional[bytes]  # line 222
    differ = difflib.Differ()  # line 223
    try:  # load files line-wise and normalize line endings (keep the one of the current file) TODO document  # line 224
        encoding, othreol, othr = detectAndLoad(filename=filename, content=file)  # line 225
        encoding, curreol, curr = detectAndLoad(filename=intoname, content=into)  # line 226
    except Exception as E:  # line 227
        Exit("Cannot merge '%s' into '%s': %r" % (filename, intoname, E))  # line 227
    if None not in [othreol, curreol] and othreol != curreol:  # line 228
        warn("Differing EOL-styles detected during merge. Using current file's style for merge output")  # line 228
    output = list(differ.compare(othr, curr))  # type: List[str]  # from generator expression  # line 229
    debug("Diff output: " + "".join([o.replace("\n", "\\n") for o in output]))  # line 230
    blocks = []  # type: List[MergeBlock]  # merged result in blocks  # line 231
    tmp = []  # type: List[str]  # block lines  # line 232
    last = " "  # line 233
    for no, line in enumerate(output + ["X"]):  # EOF marker  # line 234
        if line[0] == last:  # continue filling consecutive block  # line 235
            tmp.append(line[2:])  # continue filling consecutive block  # line 235
            continue  # continue filling consecutive block  # line 235
        if line == "X":  # EOF marker - perform action for remaining block  # line 236
            if len(tmp) == 0:  # nothing left to do  # line 237
                break  # nothing left to do  # line 237
        if last == " ":  # block is same in both files  # line 238
            blocks.append(MergeBlock(MergeBlockType.KEEP, [line for line in tmp], line=no - len(tmp)))  # line 239
        elif last == "-":  # may be a deletion or replacement, store for later  # line 240
            blocks.append(MergeBlock(MergeBlockType.REMOVE, [line for line in tmp], line=no - len(tmp)))  # line 241
        elif last == "+":  # may be insertion or replacement  # line 242
            blocks.append(MergeBlock(MergeBlockType.INSERT, [line for line in tmp], line=no - len(tmp)))  # line 243
            if len(blocks) >= 2 and len(blocks[-1].lines) == len(blocks[-2].lines):  # replaces previously removed section entirely if any  # line 244
                if len(blocks[-1].lines) >= 2 or (blocks[-1].changes is None and blocks[-2].changes is None):  # full block or no intra-line comment  # line 245
                    blocks[-2] = MergeBlock(MergeBlockType.REPLACE, blocks[-1].lines, line=no - len(tmp), replaces=blocks[-2])  # remember replaced stuff  # line 246
                else:  # may have intra-line modifications  # line 247
                    blocks[-2] = MergeBlock(MergeBlockType.MODIFY, blocks[-1].lines, line=no - len(tmp), replaces=blocks[-2], changes=blocks[-1].changes)  # line 248
                blocks.pop()  # remove TOS  # line 249
        elif last == "?":  # intra-line change comment  # line 250
            ilm = getIntraLineMarkers(tmp[0])  # tipe is one of MergeBlockType 1, 2, 4. # "? " line includes a trailing \n for some reason  # line 251
            blocks[-1] = dataCopy(MergeBlock, blocks[-1], tipe=MergeBlockType.MODIFY, changes=ilm)  # update to MODIFY, otherwise may be REPLACE instead  # line 252
        last = line[0]  # line 253
        tmp[:] = [line[2:]]  # line 254
    debug("Diff blocks: " + repr(blocks))  # line 255
    output = []  # line 256
    for block in blocks:  # line 257
        if block.tipe == MergeBlockType.KEEP:  # line 258
            output.extend(block.lines)  # line 259
        elif block.tipe == MergeBlockType.INSERT and not (mergeOperation & MergeOperation.REMOVE):  # line 260
            output.extend(block.lines)  # line 261
        elif block.tipe == MergeBlockType.REPLACE:  # complete block replacement  # line 262
            if mergeOperation & MergeOperation.INSERT:  # replaced stuff TODO allow insertion BEFORE and alternatively AFTER?  # line 263
                output.extend(block.replaces.lines)  # replaced stuff TODO allow insertion BEFORE and alternatively AFTER?  # line 263
            if not (mergeOperation & MergeBlockType.REMOVE):  # if remove, don't add replaced lines, otherwise do  # line 264
                output.extend(block.lines)  # if remove, don't add replaced lines, otherwise do  # line 264
        elif block.tipe == MergeBlockType.REMOVE and mergeOperation & MergeOperation.INSERT:  # line 265
            output.extend(block.lines)  # line 266
        elif block.tipe == MergeBlockType.MODIFY:  # line 267
            if block.changes is not None and block.changes.tipe == MergeBlockType.INSERT:  # cannot be REMOVE, because it's always "-" then "+"  # line 268
                output.extend(block.lines if mergeOperation & MergeOperation.INSERT else block.replaces.lines)  # TODO logic?  # line 269
            elif block.replaces.changes is not None and block.replaces.changes.tipe == MergeBlockType.REMOVE:  # line 270
                output.extend(block.lines if mergeOperation & MergeOperation.REMOVE else block.replaces.lines)  # line 271
            elif block.changes is not None and block.changes.tipe == MergeBlockType.MODIFY:  # always both sides modified, but may differ in markers  # line 272
                if conflictResolution == ConflictResolution.THEIRS:  # line 273
                    output.extend(block.replaces.lines)  # line 274
                elif conflictResolution == ConflictResolution.MINE:  # line 275
                    output.extend(block.lines)  # line 276
                elif conflictResolution == ConflictResolution.ASK:  # line 277
                    print(ajoin("THR ", block.replaces.lines, "\n"))  # line 278
                    print(ajoin("MIN ", block.lines, "\n"))  # line 279
                    reso = {"i": ConflictResolution.MINE, "t": ConflictResolution.THEIRS, "m": ConflictResolution.NEXT, "u": None}.get(user_input(" Resolve: *M[I]ne, [T]heirs, [M]erge, [U]ser defined: ").strip().lower(), ConflictResolution.MINE)  # type: _coconut.typing.Optional[int]  # line 280
                    debug("User selected %d" % reso)  # line 281
                    _coconut_match_check = False  # line 282
                    _coconut_match_to = reso  # line 282
                    if _coconut_match_to is None:  # line 282
                        _coconut_match_check = True  # line 282
                    if _coconut_match_check:  # line 282
                        warn("Manual input not implemented yet")  # TODO allow multi-line input (CTRL+D?)  # line 283
                    _coconut_match_check = False  # line 284
                    _coconut_match_to = reso  # line 284
                    if _coconut_match_to == ConflictResolution.MINE:  # line 284
                        _coconut_match_check = True  # line 284
                    if _coconut_match_check:  # line 284
                        debug("Using mine")  # line 285
                        output.extend(block.lines)  # line 286
                    _coconut_match_check = False  # line 287
                    _coconut_match_to = reso  # line 287
                    if _coconut_match_to == ConflictResolution.THEIRS:  # line 287
                        _coconut_match_check = True  # line 287
                    if _coconut_match_check:  # line 287
                        debug("Using theirs")  # line 288
                        output.extend(block.replaces.lines)  # line 289
                    _coconut_match_check = False  # line 290
                    _coconut_match_to = reso  # line 290
                    if _coconut_match_to == ConflictResolution.NEXT:  # line 290
                        _coconut_match_check = True  # line 290
                    if _coconut_match_check:  # line 290
                        warn("Intra-line merge not implemented yet, skipping line(s)")  # line 291
                        output.extend(block.replaces.lines)  # line 292
            else:  # e.g. contains a deletion, but user was asking for insert only??  # line 293
                warn("Investigate this case")  # line 294
                output.extend(block.lines)  # default or not .replaces?  # line 295
    debug("Merge output: " + "; ".join(output))  # line 296
    nl = b"\n" if othreol is None else othreol if curreol is None else curreol  # type: bytes  # line 297
    return _coconut_tail_call(nl.join, [line.encode(encoding) for line in output])  # line 298
# TODO handle check for more/less lines in found -/+ blocks to find common section and splitting prefix/suffix out


class Counter:  # line 302
    def __init__(_, initial: 'Number'=0) -> 'None':  # line 303
        _.value = initial  # type: Number  # line 303
    def inc(_, by=1) -> 'Number':  # line 304
        _.value += by  # line 304
        return _.value  # line 304
    def inc_old(_, by=1) -> 'Number':  # line 305
        old = _.value  # type: Number  # line 305
        _.value += by  # line 305
        return old  # line 305

class Logger:  # line 307
    ''' Logger that supports many items. '''  # line 308
    def __init__(_, log):  # line 309
        _._log = log  # line 309
    def debug(_, *s):  # line 310
        _._log.debug(sjoin(*s))  # line 310
    def info(_, *s):  # line 311
        _._log.info(sjoin(*s))  # line 311
    def warn(_, *s):  # line 312
        _._log.warning(sjoin(*s))  # line 312
    def error(_, *s):  # line 313
        _._log.error(sjoin(*s))  # line 313


# Main data class
#@runtime_validation
class Metadata:  # line 318
    ''' This class doesn't represent the entire repository state in memory,
      but serves as a container for different repo operations,
      using only parts of its attributes at any point in time. Use with care.
  '''  # line 322

    def __init__(_, path: 'str') -> 'None':  # line 324
        ''' Create empty container object for various repository operations. '''  # line 325
        _.c = loadConfig()  # line 326
        _.root = path  # type: str  # line 327
        _.branches = {}  # type: Dict[int, BranchInfo]  # branch number zero represents the initial state at branching  # line 328
        _.commits = {}  # type: Dict[int, CommitInfo]  # consecutive numbers per branch, starting at 0  # line 329
        _.paths = {}  # type: Dict[str, PathInfo]  # utf-8 encoded relative, normalized file system paths  # line 330
        _.track = _.c.track  # type: bool  # track files in the repository (tracked patterns are stored for each branch separately)  # line 331
        _.picky = _.c.picky  # type: bool  # pick files on each operation  # line 332
        _.strict = _.c.strict  # type: bool  # be always strict (regarding file contents comparsion)  # line 333
        _.compress = _.c.compress  # type: bool  # these flags are stored per branch, therefor not part of the (default) configuration  # line 334
        _.branch = None  # type: _coconut.typing.Optional[int]  # current branch number  # line 335
        _.commit = None  # type: _coconut.typing.Optional[int]  # current revision number  # line 336

    def isTextType(_, filename: 'str') -> 'bool':  # line 338
        return (((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(mimetypes.guess_type(filename)[0])).startswith("text/") or any([fnmatch.fnmatch(filename, pattern) for pattern in _.c.texttype])) and not any([fnmatch.fnmatch(filename, pattern) for pattern in _.c.bintype])  # line 338

    def listChanges(_, changes: 'ChangeSet', diffmode: 'bool'=False, textglobs: '_coconut.typing.Sequence[str]'=[]) -> 'None':  # line 340
        ''' In diffmode, don't list modified files, because the diff is displayed elsewhere. '''  # line 341
        if len(changes.additions) > 0:  # line 342
            print(ajoin("ADD ", sorted(changes.additions.keys()), "\n"))  # line 342
        if len(changes.deletions) > 0:  # line 343
            print(ajoin("DEL ", sorted(changes.deletions.keys()), "\n"))  # line 343
        if len(changes.modifications) > 0:  # only list binary files  # line 344
            print(ajoin("MOD ", sorted((k for k in changes.modifications.keys() if not _.isTextType(k) or not diffmode)), "\n"))  # only list binary files  # line 344

    def loadBranches(_) -> 'None':  # line 346
        ''' Load list of branches and current branch info from metadata file. '''  # line 347
        try:  # fails if not yet created (on initial branch/commit)  # line 348
            branches = None  # type: List[Tuple]  # line 349
            with codecs.open(os.path.join(_.root, metaFolder, metaFile), "r", encoding=UTF8) as fd:  # line 350
                flags, branches = json.load(fd)  # line 351
            _.branch = flags["branch"]  # line 352
            _.track = flags["track"]  # line 353
            _.picky = flags["picky"]  # line 354
            _.strict = flags["strict"]  # line 355
            _.branches = {i.number: i for i in (BranchInfo(*item) for item in branches)}  # re-create type info  # line 356
        except Exception as E:  # if not found, create metadata folder  # line 357
            _.branches = {}  # line 358
            warn("Couldn't read branches metadata: %r" % E)  # line 359

    def saveBranches(_) -> 'None':  # line 361
        ''' Save list of branches and current branch info to metadata file. '''  # line 362
        with codecs.open(os.path.join(_.root, metaFolder, metaFile), "w", encoding=UTF8) as fd:  # line 363
            json.dump(({"branch": _.branch, "track": _.track, "picky": _.picky, "strict": _.strict, "compress": _.compress}, list(_.branches.values())), fd, ensure_ascii=False)  # line 364

    def getBranchByName(_, name: 'Union[str, int]') -> '_coconut.typing.Optional[int]':  # line 366
        ''' Convenience accessor for named branches. '''  # line 367
        if isinstance(name, int):  # if type(name) is int: return name  # line 368
            return name  # if type(name) is int: return name  # line 368
        try:  # attempt to parse integer string  # line 369
            return int(name)  # attempt to parse integer string  # line 369
        except ValueError:  # line 370
            pass  # line 370
        found = [number for number, branch in _.branches.items() if name == branch.name]  # line 371
        return found[0] if found else None  # line 372

    def loadBranch(_, branch: 'int') -> 'None':  # line 374
        ''' Load all commit information from a branch meta data file. '''  # line 375
        with codecs.open(os.path.join(_.root, metaFolder, "b%d" % branch, metaFile), "r", encoding=UTF8) as fd:  # line 376
            commits = json.load(fd)  # type: List[List[Any]]  # list of CommitInfo that needs to be unmarshalled into value types  # line 377
        _.commits = {i.number: i for i in (CommitInfo(*item) for item in commits)}  # re-create type info  # line 378
        _.branch = branch  # line 379

    def saveBranch(_, branch: 'int') -> 'None':  # line 381
        ''' Save all commit information to a branch meta data file. '''  # line 382
        with codecs.open(os.path.join(_.root, metaFolder, "b%d" % branch, metaFile), "w", encoding=UTF8) as fd:  # line 383
            json.dump(list(_.commits.values()), fd, ensure_ascii=False)  # line 384

    def duplicateBranch(_, branch: 'int', name: '_coconut.typing.Optional[str]') -> 'None':  # line 386
        ''' Create branch from an existing branch/revision. WARN: Caller must have loaded branches information.
        branch: target branch (should not exist yet)
        name: optional name of new branch
        _.branch: current branch
    '''  # line 391
        debug("Duplicating branch '%s' to '%d'..." % ((lambda _coconut_none_coalesce_item: "b%d" % _.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(_.branches[_.branch].name), branch))  # line 392
        tracked = [t for t in _.branches[_.branch].tracked]  # copy  # line 393
        os.makedirs(os.path.join(_.root, metaFolder, "b%d" % branch, "r0"))  # line 394
        _.loadBranch(_.branch)  # line 395
        revision = max(_.commits)  # type: int  # line 396
        _.computeSequentialPathSet(_.branch, revision)  # full set of files in revision to _.paths  # line 397
        for path, pinfo in _.paths.items():  # line 398
            _.copyVersionedFile(_.branch, revision, branch, 0, pinfo)  # line 399
        _.commits = {0: CommitInfo(0, int(time.time() * 1000), "Branched from '%s'" % ((lambda _coconut_none_coalesce_item: "b%d" % _.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(_.branches[_.branch].name)))}  # store initial commit  # line 400
        _.saveBranch(branch)  # save branch meta data to branch folder  # line 401
        _.saveCommit(branch, 0)  # save commit meta data to revision folder  # line 402
        _.branches[branch] = BranchInfo(branch, _.commits[0].ctime, name, _.branches[_.branch].insync, tracked)  # save branch info, before storing repo state at caller  # line 403

    def createBranch(_, branch: 'int', name: '_coconut.typing.Optional[str]'=None, initialMessage: '_coconut.typing.Optional[str]'=None):  # line 405
        ''' Create a new branch from current file tree. This clears all known commits and modifies the file system.
        branch: target branch (should not exist yet)
        name: optional name of new branch
        _.branch: current branch, must exist already
    '''  # line 410
        simpleMode = not (_.track or _.picky)  # line 411
        tracked = [t for t in _.branches[_.branch].tracked] if _.track and len(_.branches) > 0 else []  # in case of initial branch creation  # line 412
        debug((lambda _coconut_none_coalesce_item: "b%d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)("Creating branch '%s'..." % name))  # line 413
        _.paths = {}  # type: Dict[str, PathInfo]  # line 414
        if simpleMode:  # line 415
            changes = _.findChanges(branch, 0, progress=simpleMode)  # type: ChangeSet  # creates revision folder and versioned files  # line 416
            _.listChanges(changes)  # line 417
            _.paths.update(changes.additions.items())  # line 418
        else:  # tracking or picky mode  # line 419
            os.makedirs(os.path.join(_.root, metaFolder, "b%d" % branch, "r0"))  # line 420
            if _.branch is not None:  # not immediately after "offline" - copy files from current branch  # line 421
                _.loadBranch(_.branch)  # line 422
                revision = max(_.commits)  # type: int  # TODO what if last switch was to an earlier revision? no persisting of last checkout  # line 423
                _.computeSequentialPathSet(_.branch, revision)  # full set of files in revision to _.paths  # line 424
                for path, pinfo in _.paths.items():  # line 425
                    _.copyVersionedFile(_.branch, revision, branch, 0, pinfo)  # line 426
        ts = int(time.time() * 1000)  # line 427
        _.commits = {0: CommitInfo(0, ts, "Branched on %s" % strftime(ts) if initialMessage is None else initialMessage)}  # store initial commit for new branch  # line 428
        _.saveBranch(branch)  # save branch meta data (revisions) to branch folder  # line 429
        _.saveCommit(branch, 0)  # save commit meta data to revision folder  # line 430
        _.branches[branch] = BranchInfo(branch, _.commits[0].ctime, name, True if len(_.branches) == 0 else _.branches[_.branch].insync, tracked)  # save branch info, in case it is needed  # line 431

    def removeBranch(_, branch: 'int') -> 'BranchInfo':  # line 433
        ''' Entirely remove a branch and all its revisions from the file system. '''  # line 434
        shutil.rmtree(os.path.join(_.root, metaFolder, "b%d" % branch))  # line 435
        binfo = _.branches[branch]  # line 436
        del _.branches[branch]  # line 437
        _.branch = max(_.branches)  # line 438
        _.saveBranches()  # line 439
        _.commits.clear()  # line 440
        return binfo  # line 441

    def loadCommit(_, branch: 'int', revision: 'int') -> 'None':  # line 443
        ''' Load all file information from a commit meta data. '''  # line 444
        with codecs.open(os.path.join(_.root, metaFolder, "b%d" % branch, "r%d" % revision, metaFile), "r", encoding=UTF8) as fd:  # line 445
            _.paths = json.load(fd)  # line 446
        _.paths = {path: PathInfo(*item) for path, item in _.paths.items()}  # re-create type info  # line 447
        _.branch = branch  # line 448

    def saveCommit(_, branch: 'int', revision: 'int'):  # line 450
        ''' Save all file information to a commit meta data file. '''  # line 451
        target = os.path.join(_.root, metaFolder, "b%d" % branch, "r%d" % revision)  # line 452
        try:  # line 453
            os.makedirs(target)  # line 453
        except:  # line 454
            pass  # line 454
        with codecs.open(os.path.join(target, metaFile), "w", encoding=UTF8) as fd:  # line 455
            json.dump(_.paths, fd, ensure_ascii=False)  # line 456

    def findChanges(_, branch: '_coconut.typing.Optional[int]'=None, revision: '_coconut.typing.Optional[int]'=None, checkContent: 'bool'=False, inverse: 'bool'=False, considerOnly: '_coconut.typing.Optional[FrozenSet[str]]'=None, progress: 'bool'=False) -> 'ChangeSet':  # line 458
        ''' Find changes on the file system vs. in-memory paths (which should reflect the latest commit state).
        Only if both branch and revision are *not* None, write modified/added files to the specified revision folder (thus creating a new revision)
        The function returns the state of file tree *differences*, unless "inverse" is True -> then return original data
        checkContent: also computes file content hashes
        inverse: retain original state (size, mtime, hash) instead of updated one
        considerOnly: set of tracking patterns. For update operation, union of other and current branch
        progress: Show file names during processing
    '''  # line 466
        write = branch is not None and revision is not None  # line 467
        if write:  # line 468
            os.makedirs(os.path.join(_.root, metaFolder, "b%d" % branch, "r%d" % revision))  # line 468
        changes = ChangeSet({}, {}, {})  # type: ChangeSet  # line 469
        counter = Counter()  # type: Counter  # line 470
        timer = time.time()  # line 470
        for path, dirnames, filenames in os.walk(_.root):  # line 471
            dirnames[:] = [f for f in dirnames if len([n for n in _.c.ignoreDirs if fnmatch.fnmatch(f, n)]) == 0 or len([p for p in _.c.ignoreDirsWhitelist if fnmatch.fnmatch(f, p)]) > 0]  # line 472
            filenames[:] = [f for f in filenames if len([n for n in _.c.ignores if fnmatch.fnmatch(f, n)]) == 0 or len([p for p in _.c.ignoresWhitelist if fnmatch.fnmatch(f, p)]) > 0]  # line 473
            dirnames.sort()  # line 474
            filenames.sort()  # line 474
            relpath = os.path.relpath(path, _.root).replace(os.sep, SLASH)  # line 475
            for file in (filenames if considerOnly is None else list(reduce(lambda last, pattern: last | set(fnmatch.filter(filenames, os.path.basename(pattern))), (p for p in considerOnly if os.path.dirname(p) == relpath), _coconut.set()))):  # if m.track or m.picky: only files that match any path-relevant tracking patterns  # line 476
                filename = relpath + SLASH + file  # line 477
                filepath = os.path.join(path, file)  # line 478
                stat = os.stat(filepath)  # line 479
                size, mtime, newtime = stat.st_size, int(stat.st_mtime * 1000), time.time()  # line 480
                if progress and newtime - timer > .1:  # line 481
                    outstring = "\r%s  %s" % (PROGRESS_MARKER[counter.inc_old() % 4], filename)  # line 482
                    sys.stdout.write(outstring + " " * max(0, 80 - len(outstring)))  # TODO could write to new line instead of carriage return, also needs terminal width  # line 483
                    timer = newtime  # TODO could write to new line instead of carriage return, also needs terminal width  # line 483
                if filename not in _.paths:  # detected file not present (or untracked) in other branch  # line 484
                    namehash = hashStr(filename)  # line 485
                    changes.additions[filename] = PathInfo(namehash, size, mtime, hashFile(filepath, _.compress, saveTo=os.path.join(_.root, metaFolder, "b%d" % branch, "r%d" % revision, namehash) if write else None) if size > 0 else None)  # line 486
                    continue  # line 487
                last = _.paths[filename]  # filename is known  # line 488
                if last.size is None:  # was removed before but is now added back - does not apply for tracking mode (which never marks files for removal in the history)  # line 489
                    changes.additions[filename] = PathInfo(last.namehash, size, mtime, hashFile(filepath, _.compress, saveTo=os.path.join(_.root, metaFolder, "b%d" % branch, "r%d" % revision, last.namehash) if write else None) if size > 0 else None)  # line 490
                    continue  # line 490
                elif size != last.size or mtime != last.mtime or (checkContent and hashFile(filepath, _.compress) == last.hash):  # detected a modification  # line 491
                    changes.modifications[filename] = PathInfo(last.namehash, last.size if inverse else size, last.mtime if inverse else mtime, last.hash if inverse else hashFile(filepath, _.compress, saveTo=os.path.join(_.root, metaFolder, "b%d" % branch, "r%d" % revision, last.namehash) if write else None) if (last.size if inverse else size) > 0 else None)  # line 492
# Detect deletions. Files no longer being tracked should not be found here
            for folderPath in (p for p, pinfo in _.paths.items() if p[:p.rindex(SLASH)] == relpath and pinfo.size is not None):  # only versioned (and tracked) files that match currently visited folder. TODO don't check for removal just added entries  # line 494
                if folderPath[len(relpath) + 1:] not in filenames:  # filename no longer in file tree TODO use basename and dirname instead of slicing?  # line 495
                    changes.deletions[folderPath] = _.paths[folderPath]  # filename no longer in file tree TODO use basename and dirname instead of slicing?  # line 495
        return changes  # line 496

    def integrateChangeset(_, changes: 'ChangeSet', clear=False) -> 'None':  # line 498
        ''' In-memory update from a changeset, marking deleted files with size=None. Use clear = True to start on an empty path set. '''  # line 499
        if clear:  # line 500
            _.paths.clear()  # line 500
        else:  # line 501
            rm = [p for p, info in _.paths.items() if info.size is None]  # remove files deleted in earlier change sets (revisions)  # line 502
            for old in rm:  # remove previously removed entries completely  # line 503
                del _.paths[old]  # remove previously removed entries completely  # line 503
        for d, info in changes.deletions.items():  # mark now removed entries as deleted  # line 504
            _.paths[d] = PathInfo(info.namehash, None, info.mtime, None)  # mark now removed entries as deleted  # line 504
        _.paths.update(changes.additions)  # line 505
        _.paths.update(changes.modifications)  # line 506

    def computeSequentialPathSet(_, branch: 'int', revision: 'int') -> 'None':  # line 508
        ''' In-memory computation of current list of valid PathInfo entries for specified branch and until specified revision (inclusively) by traversing revision on the file system. '''  # line 509
        _.loadCommit(branch, 0)  # load initial paths  # line 510
        n = Metadata(_.root)  # type: Metadata  # next changes  # line 511
        for revision in range(1, revision + 1):  # line 512
            n.loadCommit(branch, revision)  # line 513
            changes = diffPathSets(_.paths, n.paths)  # type: ChangeSet  # line 514
            _.integrateChangeset(changes)  # line 515

    def parseRevisionString(_, argument: 'str') -> 'Tuple[_coconut.typing.Optional[int], _coconut.typing.Optional[int]]':  # line 517
        ''' Commit identifiers can be str or int for branch, and int for revision.
        Revision identifiers can be negative, with -1 being last commit.
    '''  # line 520
        if argument is None:  # no branch/revision specified  # line 521
            return (_.branch, -1)  # no branch/revision specified  # line 521
        argument = argument.strip()  # line 522
        if argument.startswith(SLASH):  # current branch  # line 523
            return (_.branch, int(argument[1:]))  # current branch  # line 523
        if argument.endswith(SLASH):  # line 524
            try:  # line 525
                return (_.getBranchByName(argument[:-1]), -1)  # line 525
            except ValueError:  # line 526
                Exit("Unknown branch label")  # line 526
        if SLASH in argument:  # line 527
            b, r = argument.split(SLASH)[:2]  # line 528
            try:  # line 529
                return (_.getBranchByName(b), int(r))  # line 529
            except ValueError:  # line 530
                Exit("Unknown branch label or wrong number format")  # line 530
        branch = _.getBranchByName(argument)  # type: int  # returns number if given (revision) integer  # line 531
        if branch not in _.branches:  # line 532
            branch = None  # line 532
        try:  # either branch name/number or reverse/absolute revision number  # line 533
            return (_.branch if branch is None else branch, int(argument) if branch is None else -1)  # either branch name/number or reverse/absolute revision number  # line 533
        except:  # line 534
            Exit("Unknown branch label or wrong number format")  # line 534
        return (None, None)  # should never be reached TODO raise exception instead?  # line 535

    def copyVersionedFile(_, branch: 'int', revision: 'int', tobranch: 'int', torevision: 'int', pinfo: 'PathInfo') -> 'None':  # line 537
        ''' Copy versioned file to other branch/revision. '''  # line 538
        target = os.path.join(_.root, metaFolder, "b%d" % tobranch, "r%d" % torevision, pinfo.namehash)  # type: str  # line 539
        while True:  # line 540
            source = os.path.join(_.root, metaFolder, "b%d" % branch, "r%d" % revision, pinfo.namehash)  # type: str  # line 541
            if os.path.exists(source):  # line 542
                break  # line 542
            revision -= 1  # line 543
            if revision < 0:  # should never happen  # line 544
                Exit("Cannot copy file '%s' from 'b%d/r%d' to 'b%d/r%d" % (pinfo.namehash, branch, revision, tobranch, torevision))  # should never happen  # line 544
        shutil.copy2(source, target)  # line 545

    def readOrCopyVersionedFile(_, branch: 'int', revision: 'int', namehash: 'str', toFile: '_coconut.typing.Optional[str]'=None) -> '_coconut.typing.Optional[bytes]':  # line 547
        ''' Return file contents, or copy contents into file path provided. '''  # line 548
        source = os.path.join(_.root, metaFolder, "b%d" % branch, "r%d" % revision, namehash)  # type: str  # line 549
        try:  # line 550
            with openIt(source, "r", _.compress) as fd:  # line 551
                if toFile is None:  # read bytes into memory and return  # line 552
                    return fd.read()  # read bytes into memory and return  # line 552
                with open(toFile, "wb") as to:  # line 553
                    while True:  # line 554
                        buffer = fd.read(bufSize)  # line 555
                        to.write(buffer)  # line 556
                        if len(buffer) < bufSize:  # line 557
                            break  # line 557
                    return None  # line 558
        except Exception as E:  # line 559
            warn("Cannot read versioned file: %r (%d/%d/%s)" % (E, branch, revision, namehash))  # line 559
        return None  # line 560

    def restoreFile(_, relpath: '_coconut.typing.Optional[str]', branch: 'int', revision: 'int', pinfo: 'PathInfo') -> '_coconut.typing.Optional[bytes]':  # line 562
        ''' Recreate file for given revision, or return contents if path is None. '''  # line 563
        if relpath is None:  # just return contents as split decoded lines  # line 564
            return _.readOrCopyVersionedFile(branch, revision, pinfo.namehash) if pinfo.size > 0 else b''  # just return contents as split decoded lines  # line 564
        target = os.path.join(_.root, relpath.replace(SLASH, os.sep))  # type: str  # line 565
        if pinfo.size == 0:  # line 566
            with open(target, "wb"):  # line 567
                pass  # line 567
            try:  # update access/modification timestamps on file system  # line 568
                os.utime(target, (-1, pinfo.mtime / 1000.))  # update access/modification timestamps on file system  # line 568
            except Exception as E:  # line 569
                error("Cannot update file's timestamp after restoration '%r'" % E)  # line 569
            return None  # line 570
        while True:  # find latest revision that contained the file physically  # line 571
            source = os.path.join(_.root, metaFolder, "b%d" % branch, "r%d" % revision, pinfo.namehash)  # type: str  # line 572
            if os.path.exists(source):  # line 573
                break  # line 573
            revision -= 1  # line 574
            if revision < 0:  # line 575
                Exit("Cannot restore file '%s' from specified branch '%d'" % (pinfo.namehash, branch))  # line 575
# Restore file by copying buffer-wise
        with openIt(source, "r", _.compress) as fd, open(target, "wb") as to:  # using Coconut's Enhanced Parenthetical Continuation  # line 577
            while True:  # line 578
                buffer = fd.read(bufSize)  # line 579
                to.write(buffer)  # line 580
                if len(buffer) < bufSize:  # line 581
                    break  # line 581
        try:  # update access/modification timestamps on file system  # line 582
            os.utime(target, (-1, pinfo.mtime / 1000.))  # update access/modification timestamps on file system  # line 582
        except Exception as E:  # line 583
            error("Cannot update file's timestamp after restoration '%r'" % E)  # line 583
        return None  # line 584

    def getTrackingPatterns(_, branch: '_coconut.typing.Optional[int]'=None) -> 'FrozenSet[str]':  # line 586
        ''' Returns list of tracking patterns for provided branch or current branch. '''  # line 587
        return _coconut.frozenset() if not _.track and not _.picky else frozenset(_.branches[_.branch if branch is None else branch].tracked)  # line 588


# Main client operations
def offline(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]) -> 'None':  # line 592
    ''' Initial command to start working offline. '''  # line 593
    if '--force' not in options and os.path.exists(metaFolder):  # line 594
        Exit("Repository folder is either already offline or older branches and commits were left over. Use 'sos online' or continue working offline")  # line 595
    m = Metadata(os.getcwd())  # type: Metadata  # line 596
    if '--picky' in options or m.c["picky"]:  # Git-like  # line 597
        m.picky = True  # Git-like  # line 597
    elif '--track' in options or m.c["track"]:  # Svn-like  # line 598
        m.track = True  # Svn-like  # line 598
    if '--strict' in options or m.c["strict"]:  # always hash contents  # line 599
        m.strict = True  # always hash contents  # line 599
    debug("Preparing offline repository...")  # line 600
    m.createBranch(0, str(m.c["defaultbranch"]) if argument is None else argument, initialMessage="Offline repository created on %s" % strftime())  # main branch's name may be None (e.g. for fossil)  # line 601
    m.branch = 0  # line 602
    m.saveBranches()  # no change immediately after going offline, going back online won't issue a warning  # line 603
    info("Offline repository prepared. Use 'sos online' to finish offline work")  # line 604

def online(options: '_coconut.typing.Sequence[str]'=[]) -> 'None':  # line 606
    ''' Finish working offline. '''  # line 607
    force = '--force' in options  # type: bool  # line 608
    if not force:  # line 609
        m = Metadata(os.getcwd())  # line 610
        m.loadBranches()  # line 611
        if any([not b.insync for b in m.branches.values()]) and not force:  # line 612
            Exit("There are still unsynchronized branches.\nUse 'log' to list them. Commit them to your VCS one by one with 'sos commit' and 'sos switch' before leaving offline mode. Use 'online --force' to erase all aggregated offline revisions.")  # line 612
    try:  # line 613
        shutil.rmtree(metaFolder)  # line 613
        info("Left offline modus. Continue work with your online VCS.")  # line 613
    except Exception as E:  # line 614
        Exit("Error removing offline repository: %r" % E)  # line 614

def branch(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]) -> 'None':  # line 616
    ''' Create a new branch (from file tree or last revision) and (by default) continue working on it. '''  # line 617
    last = '--last' in options  # type: bool  # use last revision for branching, not current file tree  # line 618
    stay = '--stay' in options  # type: bool  # continue on current branch after branching  # line 619
    force = '--force' in options  # type: bool  # branch even with local modifications  # line 620
    m = Metadata(os.getcwd())  # type: Metadata  # line 621
    m.loadBranches()  # line 622
    if argument and m.getBranchByName(argument) is not None:  # create a named branch  # line 623
        Exit("Branch '%s' already exists. Cannot proceed" % argument)  # create a named branch  # line 623
    branch = max(m.branches.keys()) + 1  # next branch's key  # line 624
    debug("Branching to %sbranch b%d%s%s..." % ("unnamed " if argument is None else "", branch, " '%s'" % argument if argument else "", " from last revision" if last else ""))  # line 625
    if last:  # line 626
        m.duplicateBranch(branch, argument)  # branch from branch's last revision  # line 627
    else:  # from file tree state  # line 628
        m.createBranch(branch, argument)  # branch from current file tree  # line 629
    if not stay:  # line 630
        m.branch = branch  # line 631
        m.saveBranches()  # line 632
    info("%s new %sbranch b%d%s" % ("Continue work after branching" if stay else "Switched to", "unnamed " if argument is None else "", branch, " '%s'" % argument if argument else ""))  # line 633

def changes(argument: 'str'=None, options: '_coconut.typing.Sequence[str]'=[]) -> 'ChangeSet':  # line 635
    ''' Show changes of file tree vs. (last or specified) revision on current or specified branch. '''  # line 636
    m = Metadata(os.getcwd())  # type: Metadata  # line 637
    branch = None  # type: _coconut.typing.Optional[int]  # line 637
    revision = None  # type: _coconut.typing.Optional[int]  # line 637
    m.loadBranches()  # knows current branch  # line 638
    strict = '--strict' in options or m.strict  # type: bool  # line 639
    branch, revision = m.parseRevisionString(argument)  # line 640
    if branch not in m.branches:  # line 641
        Exit("Unknown branch")  # line 641
    m.loadBranch(branch)  # knows commits  # line 642
    revision = revision if revision >= 0 else len(m.commits) + revision  # negative indexing  # line 643
    if revision < 0 or revision > max(m.commits):  # line 644
        Exit("Unknown revision r%d" % revision)  # line 644
    debug("Checking file tree vs. commit '%s/r%d'..." % ((lambda _coconut_none_coalesce_item: "b%d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 645
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision  # line 646
    changes = m.findChanges(checkContent=strict, considerOnly=None if not m.track else m.getTrackingPatterns() | m.getTrackingPatterns(branch))  # type: ChangeSet  # line 647
    m.listChanges(changes)  # line 648
    return changes  # line 649

def diff(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]) -> 'None':  # line 651
    ''' Show text file differences of file tree vs. (last or specified) revision on current or specified branch. '''  # line 652
    m = Metadata(os.getcwd())  # type: Metadata  # line 653
    branch = None  # type: _coconut.typing.Optional[int]  # line 653
    revision = None  # type: _coconut.typing.Optional[int]  # line 653
    m.loadBranches()  # knows current branch  # line 654
    strict = '--strict' in options or m.strict  # type: bool  # line 655
    branch, revision = m.parseRevisionString(argument)  # line 656
    if branch not in m.branches:  # line 657
        Exit("Unknown branch")  # line 657
    m.loadBranch(branch)  # knows commits  # line 658
    revision = revision if revision >= 0 else len(m.commits) + revision  # negative indexing  # line 659
    if revision < 0 or revision > max(m.commits):  # line 660
        Exit("Unknown revision r%d" % revision)  # line 660
    debug("Diffing file tree vs. commit '%s/r%d'..." % ((lambda _coconut_none_coalesce_item: "b%d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 661
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision  # line 662
    changes = m.findChanges(checkContent=strict, inverse=True, considerOnly=None if not m.track else m.getTrackingPatterns() | m.getTrackingPatterns(branch))  # type: ChangeSet  # line 663
    info("File changes:")  # line 664
    m.listChanges(changes, diffmode=True)  # only list modified binary files  # line 665

    info("Text file modifications:")  # TODO only text files, not binary  # line 667
    differ = difflib.Differ()  # line 668
    for path, pinfo in changes.modifications.items():  # only consider modified files TODO also show A/D here?  # line 669
        print("\nDIF " + path)  # line 670
        content = None  # type: _coconut.typing.Optional[bytes]  # line 671
        othr = None  # type: _coconut.typing.Sequence[str]  # line 671
        curr = None  # type: _coconut.typing.Sequence[str]  # line 671
        if pinfo.size == 0:  # line 672
            content = b""  # line 672
        else:  # line 673
            content = m.restoreFile(None, branch, revision, pinfo)  # line 673
            assert content is not None  # line 673
        abspath = os.path.join(m.root, path.replace(SLASH, os.sep))  # line 674
        encoding, othreol, othr = detectAndLoad(content=content)  # line 675
        encoding, curreol, curr = detectAndLoad(filename=abspath)  # line 676
        currcount, othrcount = Counter(), Counter()  # TODO shows empty new line although none in file. also counting is messed up  # line 677
        last = ""  # line 678
        for no, line in enumerate(differ.compare(othr, curr)):  # line 679
            if line[0] == " ":  # no change in line  # line 680
                continue  # no change in line  # line 680
            print("%04d/%04d %s" % (no + othrcount.inc(-1 if line[0] == "+" or (line[0] == "?" and last == "+") else 0), no + currcount.inc(-1 if line[0] == "-" or (line[0] == "?" and last == "-") else 0), line))  # TODO counting this is definitely wrong and also lists \n as new diff lines. Could reuse block detection from merge instead  # line 681
            last = line[0]  # line 682

def commit(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]) -> 'None':  # line 684
    ''' Create new revision from file tree changes vs. last commit. '''  # line 685
    changes = None  # type: ChangeSet  # line 686
    m, branch, revision, changes, strict, force, trackingPatterns = stopOnChanges(None, options, commit=True)  # special flag creates new revision for detected changes, but abort if no changes  # line 687
    debug((lambda _coconut_none_coalesce_item: "b%d" % m.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)("Committing changes to branch '%s'..." % m.branches[m.branch].name))  # line 688
    m.integrateChangeset(changes, clear=True)  # update pathset to changeset only  # line 689
    m.saveCommit(m.branch, revision)  # revision has already been incremented  # line 690
    m.commits[revision] = CommitInfo(revision, int(time.time() * 1000), argument)  # comment can be None  # line 691
    m.saveBranch(m.branch)  # line 692
    if m.picky or m.track:  # TODO is it necessary to load again  # line 693
        m.loadBranches()  # TODO is it necessary to load again  # line 693
    if m.picky:  # HINT was changed from only picky to include track as well  # line 694
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], tracked=[], insync=False)  # remove tracked patterns  # line 695
    elif m.track:  # line 696
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], insync=False)  # set branch dirty  # line 697
    if m.picky or m.track:  # line 698
        m.saveBranches()  # line 698
    info("Created new revision r%2d%s (+%d/-%d/~%d)" % (revision, ((" '%s'" % argument) if argument is not None else ""), len(changes.additions), len(changes.deletions), len(changes.modifications)))  # line 699

def status() -> 'None':  # line 701
    ''' Show branches and current repository state. '''  # line 702
    m = Metadata(os.getcwd())  # type: Metadata  # line 703
    m.loadBranches()  # knows current branch  # line 704
    current = m.branch  # type: int  # line 705
    info("Offline repository status:")  # line 706
    sl = max([len((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(b.name)) for b in m.branches.values()])  # type: int  # line 707
    for branch in sorted(m.branches.values(), key=lambda b: b.number):  # line 708
        m.loadBranch(branch.number)  # knows commit history  # line 709
        print("  %s b%d%s @%s (%s) with %d commits%s" % ("*" if current == branch.number else " ", branch.number, ((" %%%ds" % (sl + 2)) % ("'%s'" % branch.name)) if branch.name else "", strftime(branch.ctime), "in sync" if branch.insync else "dirty", len(m.commits), ". Last comment: '%s'" % m.commits[max(m.commits)].message if m.commits[max(m.commits)].message else ""))  # line 710
    if m.track or m.picky and len(m.branches[m.branch].tracked) > 0:  # line 711
        info("\nTracked file patterns:")  # line 712
        print(ajoin("  | ", m.branches[m.branch].tracked, "\n"))  # line 713

def stopOnChanges(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[], check: 'bool'=True, commit: 'bool'=False) -> 'Tuple[Metadata, _coconut.typing.Optional[int], int, ChangeSet, bool, bool, FrozenSet[str]]':  # line 715
    ''' Common behavior for switch, update, delete, commit.
      check: stop program on detected change
      commit: don't stop on changes, because that's what we need in the operation
      Returns (Metadata, (current or target) branch, revision, set of changes vs. last commit on current branch, strict, force flags. '''  # line 719
    m = Metadata(os.getcwd())  # type: Metadata  # line 720
    m.loadBranches()  # knows current branch  # line 721
    trackingPatterns = m.getTrackingPatterns()  # type: FrozenSet[str]  # SVN-like mode  # line 722
    force = '--force' in options  # type: bool  # line 723
    strict = '--strict' in options or m.strict  # type: bool  # line 724
    if argument is not None:  # line 725
        branch, revision = m.parseRevisionString(argument)  # for early abort  # line 726
        if branch is None:  # line 727
            Exit("Branch '%s' doesn't exist. Cannot proceed" % argument)  # line 727
    m.loadBranch(m.branch)  # knows last commits of *current* branch  # line 728

# Determine current changes
    m.computeSequentialPathSet(m.branch, max(m.commits))  # load all commits up to specified revision  # line 731
    changes = m.findChanges(checkContent=strict, considerOnly=None if not m.track and not m.picky else trackingPatterns) if not commit else m.findChanges(m.branch, max(m.commits) + 1, checkContent=strict, considerOnly=None if not m.track and not m.picky else trackingPatterns)  # type: ChangeSet  # line 732
    if (changes.additions or changes.deletions or changes.modifications) and not force:  # and check?  # line 733
        m.listChanges(changes)  # line 734
        if check and not commit:  # line 735
            Exit("File tree contains changes. Use --force to proceed")  # line 735
    elif commit and not force:  #  and not check  # line 736
        Exit("Nothing to commit. Aborting")  #  and not check  # line 736

    if argument is not None:  # branch/revision specified  # line 738
        m.loadBranch(branch)  # knows commits of target branch  # line 739
        revision = revision if revision >= 0 else len(m.commits) + revision  # negative indexing  # line 740
        if revision < 0 or revision > max(m.commits):  # line 741
            Exit("Unknown revision r%2d" % revision)  # line 741
        return (m, branch, revision, changes, strict, force, m.getTrackingPatterns(branch))  # line 742
    return (m, m.branch, max(m.commits) + (1 if commit else 0), changes, strict, force, trackingPatterns)  # line 743

def switch(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]) -> 'None':  # line 745
    ''' Continue work on another branch, replacing file tree changes. '''  # line 746
    changes = None  # type: ChangeSet  # line 747
    m, branch, revision, changes, strict, force, trackingPatterns = stopOnChanges(argument, options)  # line 748
    debug("Switching to branch %sb%d/r%d..." % ("'%s' " % m.branches[branch].name if m.branches[branch].name else "", branch, revision))  # line 749

# Determine file changes from other branch to current file tree
    if '--meta' in options:  # only switch meta data  # line 752
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], tracked=m.branches[branch].tracked)  # line 753
    else:  # full file switch  # line 754
        m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision for target branch into memory  # line 755
        changes = m.findChanges(checkContent=strict, inverse=True, considerOnly=None if not m.track else trackingPatterns | m.getTrackingPatterns(branch))  # determine difference of other branch vs. file tree (forced or in sync with current branch; "addition" means exists now and should be removed)  # line 756
        if not (changes.additions or changes.deletions or changes.modifications):  # line 757
            info("No changes to current file tree")  # line 758
        else:  # integration required  # line 759
            for path, pinfo in changes.deletions.items():  # line 760
                m.restoreFile(path, branch, revision, pinfo)  # is deleted in current file tree: restore from branch to reach target  # line 761
                debug("ADD " + path)  # line 762
            for path, pinfo in changes.additions.items():  # line 763
                os.unlink(os.path.join(m.root, path.replace(SLASH, os.sep)))  # is added in current file tree: remove from branch to reach target  # line 764
                debug("DEL " + path)  # line 765
            for path, pinfo in changes.modifications.items():  # line 766
                m.restoreFile(path, branch, revision, pinfo)  # is modified in current file tree: restore from branch to reach target  # line 767
                debug("MOD " + path)  # line 768
    m.branch = branch  # line 769
    m.saveBranches()  # store switched path info  # line 770
    info("Switched to branch %sb%d/r%d" % ("'%s' " % (m.branches[branch].name if m.branches[branch].name else ""), branch, revision))  # line 771

def update(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]) -> 'None':  # line 773
    ''' Load and integrate a specified other branch/revision into current life file tree.
      In tracking mode, this also updates the set of tracked patterns.
      User options for merge operation: --add (don't remove), --rm (don't insert), --add-lines/--rm-lines (inside each file)
      User options for conflict resolution: --theirs/--mine/--ask
  '''  # line 778
    mrg = firstOfMap({"--add": MergeOperation.INSERT, "--rm": MergeOperation.REMOVE}, options, MergeOperation.BOTH)  # type: int  # default operation is replicate remove state for non-conflicting cases (insertions/deletions)  # line 779
    res = firstOfMap({'--theirs': ConflictResolution.THEIRS, '--mine': ConflictResolution.MINE}, options, ConflictResolution.NEXT)  # type: int  # NEXT means deeper level  # line 780
    mrgline = firstOfMap({'--add-lines': MergeOperation.INSERT, '--rm-lines': MergeOperation.REMOVE}, options, mrg)  # type: int  # default operation for modified files is same as for files  # line 781
    resline = firstOfMap({'--theirs-lines': ConflictResolution.THEIRS, '--mine-lines': ConflictResolution.MINE}, options, ConflictResolution.ASK)  # type: int  # line 782
    m = Metadata(os.getcwd())  # type: Metadata  # TODO same is called inside stop on changes - could return both current and designated branch instead  # line 783
    m.loadBranches()  # line 784
    changes = None  # type: ChangeSet  # line 784
    currentBranch = m.branch  # type: _coconut.typing.Optional[int]  # line 785
    m, branch, revision, changes, strict, force, trackingPatterns = stopOnChanges(argument, options, check=False)  # don't check for current changes, only parse arguments  # line 786
    debug("Integrating changes from '%s/r%d' into file tree..." % ((lambda _coconut_none_coalesce_item: "b%d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 787

# Determine file changes from other branch over current file tree
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision for branch to integrate  # line 790
    trackingUnion = trackingPatterns | m.getTrackingPatterns(branch)  # type: FrozenSet[str]  # line 791
    changes = m.findChanges(checkContent=strict, inverse=True, considerOnly=None if not m.track else trackingUnion)  # determine difference of other branch vs. file tree. "addition" means exists now but not in other, and should be removed unless in tracking mode  # line 792
    if not (mrg & MergeOperation.INSERT and changes.additions or (mrg & MergeOperation.REMOVE and changes.deletions) or changes.modifications):  # line 793
        if trackingUnion == trackingPatterns:  # nothing added  # line 794
            info("No file changes detected, but tracking patterns were merged (run 'sos switch /-1 --meta' to undo)")  # TODO write test to see if this works  # line 795
        else:  # line 796
            info("Nothing to update")  # but write back updated branch info below  # line 797
    else:  # integration required  # line 798
        for path, pinfo in changes.deletions.items():  # deletions mark files not present in current file tree -> needs additon  # line 799
            if mrg & MergeOperation.INSERT:  # deleted in current file tree: restore from branch to reach target  # line 800
                m.restoreFile(path, branch, revision, pinfo)  # deleted in current file tree: restore from branch to reach target  # line 800
            print("ADD " + path if mrg & MergeOperation.INSERT else "(A) " + path)  # line 801
        for path, pinfo in changes.additions.items():  # line 802
            if m.track or m.picky:  # because untracked files of other branch cannot be detected (which is good)  # line 803
                Exit("This should never happen")  # because untracked files of other branch cannot be detected (which is good)  # line 803
            if mrg & MergeOperation.REMOVE:  # line 804
                os.unlink(m.root + os.sep + path.replace(SLASH, os.sep))  # line 804
            print("DEL " if mrg & MergeOperation.REMOVE else "(D) " + path)  # not contained in other branch, but maybe kept  # line 805
        for path, pinfo in changes.modifications.items():  # line 806
            into = os.path.join(m.root, path.replace(SLASH, os.sep))  # type: str  # line 807
            binary = not m.isTextType(path)  # line 808
            if res & ConflictResolution.ASK or (binary and res == ConflictResolution.NEXT):  # TODO this may ask user even if no interaction was asked for (check line level for interactivity fist)  # line 809
                print(("MOD " if not binary else "BIN ") + path)  # line 810
                reso = {"i": ConflictResolution.MINE, "t": ConflictResolution.THEIRS, "m": ConflictResolution.NEXT}.get(user_input(" Resolve: *M[I]ne, [T]heirs, [M]erge: (I)").strip().lower(), ConflictResolution.MINE)  # line 811
                debug("User selected %d" % reso)  # line 812
            else:  # line 813
                reso = res  # line 813
            if reso & ConflictResolution.THEIRS:  # line 814
                m.readOrCopyVersionedFile(branch, revision, pinfo.namehash, into)  # blockwise copy of contents  # line 815
                print("THR " + path)  # line 816
            elif reso & ConflictResolution.MINE:  # line 817
                print("MNE " + path)  # nothing to do! same as skip  # line 818
            else:  # NEXT: line-based merge  # line 819
                file = m.readOrCopyVersionedFile(branch, revision, pinfo.namehash) if pinfo.size > 0 else b''  # type: str  # parse lines TODO decode etc.  # line 820
                if file is not None:  # if None, error message was already logged  # line 821
                    contents = merge(file=file, intoname=into, mergeOperation=mrgline, conflictResolution=resline)  # type: bytes  # line 822
                    with open(path, "wb") as fd:  # TODO write to temp file first  # line 823
                        fd.write(contents)  # TODO write to temp file first  # line 823
    info("Integrated changes from '%s/r%d' into file tree" % ((lambda _coconut_none_coalesce_item: "b%d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 824
    m.branches[currentBranch] = dataCopy(BranchInfo, m.branches[currentBranch], insync=False, tracked=list(trackingUnion))  # TODO really? it's a change that cannot be undone easily by the user  # line 825
    m.branch = currentBranch  # need to restore setting before saving TODO operate on different objects instead  # line 826
    m.saveBranches()  # line 827

def delete(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]) -> 'None':  # line 829
    ''' Remove a branch entirely. '''  # line 830
    m, branch, revision, changes, strict, force, trackingPatterns = stopOnChanges(argument, options)  # line 831
    if len(m.branches) == 1:  # line 832
        Exit("Cannot remove the only remaining branch. Use 'sos online' to leave offline mode")  # line 832
    debug("Removing branch %d%s..." % (branch, " '%s'" % m.branches[branch].name if m.branches[branch].name else ""))  # line 833
    binfo = m.removeBranch(branch)  # need to keep a reference to removed entry for output below  # line 834
    info("Branch b%d%s removed" % (branch, " '%s'" % binfo.name if binfo.name else ""))  # line 835

def add(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]) -> 'None':  # line 837
    ''' Add a tracked files pattern to current branch's tracked files. '''  # line 838
    force = '--force' in options  # type: bool  # line 839
    m = Metadata(os.getcwd())  # type: Metadata  # line 840
    m.loadBranches()  # line 841
    if not m.track and not m.picky:  # line 842
        Exit("Repository is in simple mode. Needs 'offline --track' or 'offline --picky' instead")  # line 842
    relpath = os.path.relpath(os.path.dirname(os.path.abspath(argument)), m.root)  # for tracking list  # line 843
    pattern = os.path.join(relpath, os.path.basename(argument)).replace(os.sep, SLASH)  # line 844
    if pattern in m.branches[m.branch].tracked:  # line 845
        Exit("Pattern '%s' already tracked")  # line 846
    if not force and len(fnmatch.filter(os.listdir(os.path.abspath(relpath)), os.path.basename(pattern.replace(SLASH, os.sep)))) == 0:  # doesn't match any current file  # line 847
        Exit("Pattern doesn't match any file in specified folder. Use --force to add it anyway")  # line 848
    m.branches[m.branch].tracked.append(pattern)  # TODO set insync flag to False? same for rm  # line 849
    m.saveBranches()  # line 850
    info("Added tracking pattern '%s' for folder '%s'" % (os.path.basename(pattern.replace(SLASH, os.sep)), os.path.abspath(relpath)))  # line 851

def rm(argument: 'str') -> 'None':  # line 853
    ''' Remove a tracked files pattern from current branch's tracked files. '''  # line 854
    m = Metadata(os.getcwd())  # type: Metadata  # line 855
    m.loadBranches()  # line 856
    if not m.track and not m.picky:  # line 857
        Exit("Repository is in simple mode. Needs 'offline --track' or 'offline --picky' instead")  # line 857
    relpath = os.path.relpath(os.path.dirname(os.path.abspath(argument)), m.root)  # type: str  # line 858
    pattern = os.path.join(relpath, os.path.basename(argument)).replace(os.sep, SLASH)  # type: str  # line 859
    if pattern not in m.branches[m.branch].tracked:  # line 860
        suggestion = _coconut.set()  # type: Set[str]  # line 861
        for pat in m.branches[m.branch].tracked:  # line 862
            if fnmatch.fnmatch(pattern, pat):  # line 863
                suggestion.add(pat)  # line 863
        if suggestion:  # line 864
            print("Do you mean any of the following tracked globs? '%s'" % (", ".join(sorted(suggestion))))  # line 864
        Exit("Tracked pattern '%s' not found" % pattern)  # line 865
    m.branches[m.branch].tracked.remove(pattern)  # line 866
    m.saveBranches()  # line 867
    info("Removed tracking pattern '%s' for folder '%s'" % (os.path.basename(pattern.replace(SLASH, os.sep)), os.path.abspath(relpath)))  # line 868

def ls(argument: '_coconut.typing.Optional[str]'=None) -> 'None':  # line 870
    ''' List specified directory, augmenting with repository metadata. '''  # line 871
    cwd = os.getcwd() if argument is None else argument  # type: str  # line 872
    m = Metadata(cwd)  # type: Metadata  # line 873
    m.loadBranches()  # line 874
    relpath = os.path.relpath(cwd, m.root).replace(os.sep, SLASH)  # type: str  # line 875
    files = list(sorted((entry for entry in os.listdir(cwd) if os.path.isfile(entry))))  # type: List[str]  # line 876
    trackingPatterns = m.getTrackingPatterns() if m.track or m.picky else _coconut.frozenset()  # type: FrozenSet[str]  # for current branch  # line 877
    for file in files:  # line 878
        ignore = None  # type: _coconut.typing.Optional[str]  # line 879
        for ig in m.c.ignores:  # line 880
            if fnmatch.fnmatch(file, ig):  # remember first match TODO document this  # line 881
                ignore = ig  # remember first match TODO document this  # line 881
                break  # remember first match TODO document this  # line 881
        if ig:  # line 882
            for wl in m.c.ignoresWhitelist:  # line 883
                if fnmatch.fnmatch(file, wl):  # found a white list entry for ignored file, undo ignoring it  # line 884
                    ignore = None  # found a white list entry for ignored file, undo ignoring it  # line 884
                    break  # found a white list entry for ignored file, undo ignoring it  # line 884
        if ignore is None:  # line 885
            matches = []  # type: List[str]  # line 886
            for pattern in (p for p in trackingPatterns if os.path.dirname(p) == relpath):  # only patterns matching current folder  # line 887
                if fnmatch.fnmatch(file, os.path.basename(pattern)):  # TODO or only file basename?  # line 888
                    matches.append(pattern)  # TODO or only file basename?  # line 888
        print("%s %s%s" % ("IGN" if ignore is not None else ("TRK" if len(matches) > 0 else "   "), file, ' by "%s"' % ignore if ignore is not None else (" by " + ";".join(['"%s"' % match for match in matches]) if len(matches) > 0 else "")))  # line 889

def log() -> 'None':  # line 891
    ''' List previous commits on current branch. '''  # TODO --verbose for changesets  # line 892
    m = Metadata(os.getcwd())  # type: Metadata  # line 893
    m.loadBranches()  # knows current branch  # line 894
    m.loadBranch(m.branch)  # knows commit history  # line 895
    info((lambda _coconut_none_coalesce_item: "r%2d" % m.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)("Offline commit history of branch '%s':" % m.branches[m.branch].name))  # TODO also retain "from branch/revision" on branching?  # line 896
    nl = len("%d" % max(m.commits))  # determine space needed for revision  # line 897
    for commit in sorted(m.commits.values(), key=lambda co: co.number):  # line 898
        print("  %s r%s @%s: %s" % ("*" if commit.number == max(m.commits) else " ", ("%%%ds" % nl) % commit.number, strftime(commit.ctime), (lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(commit.message)))  # line 899
# TODO list number of files and binary/text

def config(argument: 'str', options: 'List[str]'=[]) -> 'None':  # line 902
    if argument not in ["set", "unset", "show", "add", "rm"]:  # line 903
        Exit("Unknown config command")  # line 903
    if not configr:  # line 904
        Exit("Cannot execute config command. 'configr' module not installed")  # line 904
    c = loadConfig()  # type: Union[configr.Configr, Accessor]  # line 905
    if argument == "set":  # line 906
        if len(options) < 2:  # line 907
            Exit("No key nor value specified")  # line 907
        if options[0] not in (["defaultbranch"] + CONFIGURABLE_FLAGS + CONFIGURABLE_LISTS):  # line 908
            Exit("Unsupported key %r" % options[0])  # line 908
        c[options[0]] = options[1].lower() in TRUTH_VALUES if options[0] in CONFIGURABLE_FLAGS else (options[1].strip() if options[0] not in CONFIGURABLE_LISTS else safeSplit(options[1], ";"))  # TODO sanitize texts?  # line 909
    elif argument == "unset":  # line 910
        if len(options) < 1:  # line 911
            Exit("No key specified")  # line 911
        if options[0] not in c.keys():  # line 912
            Exit("Unknown key")  # line 912
        del c[options[0]]  # line 913
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
    elif argument == "rm":  # line 920
        if len(options) < 2:  # line 921
            Exit("No key nor value specified")  # line 921
        if options[0] not in c.keys():  # line 922
            Exit("Unknown key specified: %r" % options[0])  # line 922
        if options[1] not in c[options[0]]:  # line 923
            Exit("Unknown value: %r" % options[1])  # line 923
        c[options[0]].remove(options[1])  # line 924
    else:  # Show  # line 925
        for k, v in sorted(c.items()):  # line 926
            print("%s => %r" % (k, v))  # line 926
        return  # line 927
    f, g = saveConfig(c)  # line 928
    if f is None:  # line 929
        error("Error saving user configuration: %r" % g)  # line 929

def parse(root: 'str'):  # line 931
    ''' Main operation. '''  # line 932
    debug("Parsing command-line arguments...")  # line 933
    command = sys.argv[1].strip() if len(sys.argv) > 1 else ""  # line 934
    argument = sys.argv[2].strip() if len(sys.argv) > 2 else None  # line 935
    options = sys.argv[3:] if command == "config" else [c for c in sys.argv[2:] if c.startswith("--")]  # consider second parameter for no-arg command, otherwise from third on  # line 936
    debug("Processing command %r with argument '%s' and options %r." % ("" if command is None else command, "" if argument is None else argument, options))  # line 937
    if command[:1] == "a":  # a  # line 938
        add(argument, options)  # a  # line 938
    elif command[:1] == "b":  # b  # line 939
        branch(argument, options)  # b  # line 939
    elif command[:2] == "ch":  # ch  # line 940
        changes(argument, options)  # ch  # line 940
    elif command[:3] == "com" or command[:2] == "ci":  # com, ci  # line 941
        commit(argument, options)  # com, ci  # line 941
    elif command[:3] == 'con':  # con  # line 942
        config(argument, options)  # con  # line 942
    elif command[:2] == "de":  # de  # line 943
        delete(argument, options)  # de  # line 943
    elif command[:2] == "di":  # di  # line 944
        diff(argument, options)  # di  # line 944
    elif command[:1] == "h":  # h  # line 945
        usage()  # h  # line 945
    elif command[:2] == "lo":  # lo  # line 946
        log()  # lo  # line 946
    elif command[:2] in ["li", "ls"]:  # li, ls  # line 947
        ls(argument)  # li, ls  # line 947
    elif command[:2] == "of":  # of  # line 948
        offline(argument, options)  # of  # line 948
    elif command[:2] == "on":  # on  # line 949
        online(options)  # on  # line 949
    elif command[:1] == "r":  # r  # line 950
        rm(argument)  # r  # line 950
    elif command[:2] == "st":  # st  # line 951
        status()  # st  # line 951
    elif command[:2] == "sw":  # sw  # line 952
        switch(argument, options)  # sw  # line 952
    elif command[:2] == "up":  # up  # line 953
        update(argument, options)  # up  # line 953
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
        vcss = [executable for folder, executable in vcsFolders.items() if folder in contents]  # type: _coconut.typing.Sequence[str]  # determine VCS type from dot folder  # line 964
        choice = None  # type: _coconut.typing.Optional[str]  # line 965
        if len(vcss) > 1:  # line 966
            choice = SVN if SVN in vcss else vcss[0]  # line 967
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
                choice = SVN if SVN in vcss else vcss[0]  # line 985
                warn("Detected more than one parallel VCS checkouts %r. Falling back to '%s'" % (vcss, choice))  # line 986
            elif len(vcss) > 0:  # line 987
                choice = vcss[0]  # line 987
            if choice:  # line 988
                return (sos, path, choice)  # line 988
    return (None, vcs[0], vcs[1])  # line 989

def main() -> 'None':  # line 991
    global debug, info, warn, error  # line 992
    logging.basicConfig(level=level, stream=sys.stderr, format=("%(asctime)-23s %(levelname)-8s %(name)s:%(lineno)d | %(message)s" if '--log' in sys.argv else "%(message)s"))  # line 993
    _log = Logger(logging.getLogger(__name__))  # line 994
    debug, info, warn, error = _log.debug, _log.info, _log.warn, _log.error  # line 994
    for option in (o for o in ['--log', '--verbose', '-v', '--sos'] if o in sys.argv):  # clean up program arguments  # line 995
        sys.argv.remove(option)  # clean up program arguments  # line 995
    if '--help' in sys.argv or len(sys.argv) < 2:  # line 996
        usage()  # line 996
        Exit()  # line 996
    command = sys.argv[1] if len(sys.argv) > 1 else None  # type: _coconut.typing.Optional[str]  # line 997
    root, vcs, cmd = findSosVcsBase()  # root is None if no .sos folder exists up the folder tree (still working online); vcs is checkout/repo root folder; cmd is the VCS base command  # line 998
    debug("Found root folders for SOS/VCS: %s/%s" % ("" if root is None else root, "" if vcs is None else vcs))  # line 999
    defaults["defaultbranch"] = vcsBranches.get(cmd, "trunk")  # sets dynamic default with SVN fallback  # line 1000
    if force_sos or root is not None or ("" if command is None else command)[:2] == "of" or ("" if command is None else command)[:1] == "h":  # in offline mode or just going offline TODO what about git config?  # line 1001
        os.chdir(os.getcwd() if command[:2] == "of" else os.getcwd() if root is None else root)  # since all operatiosn use os.getcwd() and we save one argument to each function  # line 1002
        parse(root)  # line 1003
    elif cmd is not None:  # online mode - delegate to VCS  # line 1004
        info("SOS: Running '%s %s'" % (cmd, " ".join(sys.argv[1:])))  # line 1005
        import subprocess  # only requuired in this section  # line 1006
        process = subprocess.Popen([cmd] + sys.argv[1:], shell=False, stdin=subprocess.PIPE, stdout=sys.stdout, stderr=sys.stderr)  # line 1007
        inp = ""  # type: str  # line 1008
        while True:  # line 1009
            so, se = process.communicate(input=inp)  # line 1010
            if process.returncode is not None:  # line 1011
                break  # line 1011
            inp = sys.stdin.read()  # line 1012
        if sys.argv[1][:2] == "co" and process.returncode == 0:  # successful commit - assume now in sync again (but leave meta data folder with potential other feature branches behind until "online")  # line 1013
            if root is None:  # line 1014
                Exit("Cannot determine VCS root folder: Unable to mark repository as synchronized and will show a warning when leaving offline mode")  # line 1014
            m = Metadata(root)  # line 1015
            m.loadBranches()  # read repo  # line 1016
            m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], insync=True)  # mark as committed  # line 1017
            m.saveBranches()  # line 1018
    else:  # line 1019
        Exit("No offline repository present, and unable to detect VCS file tree")  # line 1019


# Main part
level = logging.DEBUG if os.environ.get("DEBUG", "False").lower() == "true" or '--verbose' in sys.argv or '-v' in sys.argv else logging.INFO  # line 1023
force_sos = '--sos' in sys.argv  # line 1024
_log = Logger(logging.getLogger(__name__))  # line 1025
debug, info, warn, error = _log.debug, _log.info, _log.warn, _log.error  # line 1025
if __name__ == '__main__':  # line 1026
    main()  # line 1026
