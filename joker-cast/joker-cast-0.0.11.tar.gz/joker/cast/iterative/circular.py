#!/usr/bin/env python3
# coding: utf-8

from __future__ import division, print_function

import itertools

import six
from joker.cast.numeric import ceil


class _ListWrapper(object):
    def __init__(self, iterable):
        self._items = list(iterable)

    def __repr__(self):
        c = self.__class__.__name__
        return '{}({})'.format(c, self._items)


class Pool(_ListWrapper):
    def __init__(self, iterable):
        super(Pool, self).__init__(iterable)
        self._cycle = itertools.cycle(self._items)

    def shuffle(self):
        import random
        random.shuffle(self._items)
        self._cycle = itertools.cycle(self._items)
        return self

    def take(self, n):
        return list(itertools.islice(self._cycle, n))


class Circular(_ListWrapper):
    """
    >>> c = Circular([0, 1, 2, 3, 4]) 
    >>> list(c[-1:5])
    [4, 0, 1, 2, 3, 4]
    """
    def __init__(self, iterable):
        super(Circular, self).__init__(iterable)
        assert self._items

    def ix_turn(self, ix):
        if ix is None:
            return
        return len(self._items) - 1 - ix

    def ix_shift(self, *indexes):
        m = min(i for i in indexes if i is not None)
        if m >= 0:
            return indexes
        n = len(self._items)
        shift = ceil(-1. * m / n) * n
        new_indexes = []
        for ix in indexes:
            if ix is None:
                new_indexes.append(None)
            else:
                new_indexes.append(ix + shift)
        return tuple(new_indexes)

    def standardize(self, slc):
        """
        :param slc: a slice instance 
        :return: (start, stop, step)  # a tuple  
        """
        assert isinstance(slc, slice)
        if slc.step is None or slc.step >= 0:
            return self.ix_shift(slc.start, slc.stop, slc.step)
        return self.ix_shift(
            self.ix_turn(slc.start),
            self.ix_turn(slc.stop),
            -slc.step)

    def __getitem__(self, key):
        n = len(self._items)
        if isinstance(key, six.integer_types):
            return self._items[key % n]

        if isinstance(key, slice):
            start, stop, step = self.standardize(key)
            if key.step and key.step < 0:
                c_items = itertools.cycle(self._items[::-1])
            else:
                c_items = itertools.cycle(self._items)
            return itertools.islice(c_items, start, stop, step)


class CircularString(object):
    """
    >>> cs = CircularString('0123456789')
    >>> cs[-1:12]
    '9012345678901'
    """
    def __init__(self, string):
        self._string = string
        self._circular = Circular(string)

    def __repr__(self):
        c = self.__class__.__name__
        return '{}({})'.format(c, self._string)

    def __getitem__(self, key):
        return ''.join(list(self._circular[key]))


