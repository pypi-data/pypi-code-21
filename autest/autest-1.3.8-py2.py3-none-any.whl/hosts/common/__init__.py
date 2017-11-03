from __future__ import absolute_import, division, print_function
import collections
from . import is_a


def flatten(iterable):
    if isinstance(iterable, collections.Iterable) and not isinstance(iterable, str):
        return [a for i in iterable for a in flatten(i)]
    else:
        return [iterable]


def make_list(obj, flatten_list=True):
    if not is_a.List(obj):
        obj = [obj]
    if flatten_list:
        obj = flatten(obj)
    return obj


class DelayVariable(object):
    ''' This class defines a varable that will not be evaluted until it is requested
    This allow it to be assigned some logic and not execute it till requested, as needed
    '''
    __slots__ = ['__func', '__weakref__']

    def __init__(self, func):
        self.__func = func

    def __eval__(self):
        return self.__func()

    def __str__(self):
        return str(self.__eval__())

    def __repr__(self):
        return str(self.__eval__())


class DelayFormat(DelayVariable):

    def __init__(self, sfmt, *lst, **kw):
        tmp = lambda: sfmt.format(*lst, **kw)
        super(DelayFormat, self).__init__(tmp)
