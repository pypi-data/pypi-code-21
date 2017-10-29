#!/usr/bin/env python
# -*- coding: latin-1 -*-
#
from collections import Iterable, Mapping, MutableMapping, MutableSequence, MutableSet, Sequence, \
    Set


class aIterable(Iterable):
    def __init__(self, i=None):
        self.iter = i or []

    def __iter__(self):
        for i in self.iter:
            yield i


class aSet(Set):
    def __contains__(self):
        pass

    def __iter__(self):
        pass

    def __len__(self):
        pass


class mSet(MutableSet):
    def __init__(self, i=None):
        self.iter = i or []

    def add(self, value):
        pass

    def discard(self, value):
        pass

    def __contains__(self):
        pass

    def __iter__(self):
        pass

    def __len__(self):
        pass


class aSequence(Sequence):
    def __init__(self, i=None):
        self.iter = i or []

    def __iter__(self):
        for i in self.iter:
            yield i

    def __getitem__(self, index):
        pass

    def __contains__(self, x):
        pass

    def __len__(self):
        pass


class mSequence(MutableSequence):
    def __init__(self, i=None):
        self.iter = i or []

    def __iter__(self):
        for i in self.iter:
            yield i

    def __getitem__(self, index):
        pass

    def __contains__(self, x):
        pass

    def __len__(self):
        pass

    def __delitem__(self):
        pass

    def __setitem__(self):
        pass

    def insert(self):
        pass


class aMapping(Mapping):
    def __getitem__(self, index):
        pass

    def __iter__(self):
        pass

    def __len__(self):
        pass


class mMapping(MutableMapping):
    def __getitem__(self, index):
        pass

    def __iter__(self):
        pass

    def __len__(self):
        pass

    def __delitem__(self, item):
        pass

    def __setitem__(self, item, value):
        pass
