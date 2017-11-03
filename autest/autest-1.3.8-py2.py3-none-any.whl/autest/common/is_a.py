from __future__ import absolute_import, division, print_function
from builtins import int
from future.utils import native_str


def List(obj):
    return isinstance(obj, list)


def Tuple(obj):
    return isinstance(obj, tuple)


def OrderedSequence(obj):
    return List(obj) or Tuple(obj)


def String(obj):
    return isinstance(obj, native_str)


def Int(obj):
    return isinstance(obj, int)


def Number(obj):
    return not isinstance(obj, bool) and (isinstance(obj, int) or isinstance(
        obj, float))


def Dictionary(obj):
    return isinstance(obj, dict)


def Dict(obj):
    return isinstance(obj, dict)
