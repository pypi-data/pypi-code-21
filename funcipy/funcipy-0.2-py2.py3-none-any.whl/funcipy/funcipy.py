# Copyright (c) 2017, Venkatesh-Prasad Ranganath
#
# BSD 3-clause License
#
# Author: Venkatesh-Prasad Ranganath (rvprasad)


def map_op(self, func):
    return funcify(map(func, self))


def filter_op(self, func):
    return funcify(filter(func, self))


def __helper__(obj):
    obj.map = map_op.__get__(obj)
    obj.filter = filter_op.__get__(obj)
    return obj


class _ListWrapper(list):
    def __init__(self, obj):
        list.__init__(self, obj)
        __helper__(self)


class _SetWrapper(set):
    def __init__(self, obj):
        set.__init__(self, obj)
        __helper__(self)


class _DictWrapper(dict):
    def __init__(self, obj):
        dict.__init__(self, obj)
        __helper__(self)


class _TupleWrapper(tuple):
    def __new__(cls, value, *args, **kwargs):
        return super(_TupleWrapper, cls).__new__(cls, value)

    def __init__(self, obj):
        __helper__(self)


class _StrWrapper(str):
    def __new__(cls, value, *args, **kwargs):
        return super(_StrWrapper, cls).__new__(cls, value)

    def __init__(self, obj):
        __helper__(self)


class _RangeWrapper(object):
    def __init__(self, obj):
        self.range = obj
        __helper__(self)

    def __iter__(self):
        return _IterWrapper(iter(self.range))

    def __getattr__(self, x):
        return getattr(self.range, x)


class _IterWrapper(object):
    def __init__(self, obj):
        self.iter = obj
        __helper__(self)

    def __iter__(self):
        return self

    def __next__(self):
        return self.iter.__next__()

    def __getattr__(self, x):
        return getattr(self.iter, x)


def funcify(obj):
    if not getattr(obj, '__iter__', None):
        return obj

    if isinstance(obj, list):
        return _ListWrapper(obj)
    elif isinstance(obj, set):
        return _SetWrapper(obj)
    elif isinstance(obj, dict):
        return _DictWrapper(obj)
    elif isinstance(obj, tuple):
        return _TupleWrapper(obj)
    elif isinstance(obj, str):
        return _StrWrapper(obj)
    elif isinstance(obj, range):
        return _RangeWrapper(obj)
    elif getattr(obj, '__dict__', None):
        return __helper__(obj)
    elif getattr(obj, '__next__', None):
        return _IterWrapper(obj)
    else:
        return obj
