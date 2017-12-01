#!/usr/bin/env python3
# coding: utf-8

from __future__ import division, print_function

import collections


class DefaultOrderedDict(collections.OrderedDict):
    # Source: http://stackoverflow.com/a/6190500/562769
    def __init__(self, default_factory=None, *a, **kw):
        if (default_factory is not None and
                not isinstance(default_factory, collections.Callable)):
            raise TypeError('first argument must be a callable')
        collections.OrderedDict.__init__(self, *a, **kw)
        self.default_factory = default_factory

    def __getitem__(self, key):
        try:
            return collections.OrderedDict.__getitem__(self, key)
        except KeyError:
            return self.__missing__(key)

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        self[key] = value = self.default_factory()
        return value

    def __reduce__(self):
        if self.default_factory is None:
            args = tuple()
        else:
            args = self.default_factory,
        return type(self), args, None, None, self.items()


class RecursiveDefaultDict(collections.defaultdict):
    def __init__(self, **kwargs):
        super(RecursiveDefaultDict, self).__init__(self.__class__, **kwargs)


class RecursiveCounter(RecursiveDefaultDict):
    def total(self, as_string=False):
        s = 0
        for v in self.values():
            if isinstance(v, six.integer_types) or isinstance(v, float):
                s += v
            elif isinstance(v, RecursiveCounter):
                s += v.total()
        if as_string:
            s = str(s)
        return s
