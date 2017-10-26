# -*- coding: utf-8 -*-
""" Various helpers used by the serialization library. """
from __future__ import absolute_import, print_function, unicode_literals

# stdlib imports
import types
from inspect import ismethod
from itertools import chain

# 3rd party imports
from six import string_types, integer_types


class EnumMetaclass(type):
    """Metaclass for enumerations.
    You must define the values using UPPERCASE names.

    Generates:
    cls.names - reverse dictionary mapping value to name
    cls.pairs - sorted list of (id, name) pairs suitable for model choices
    cls.values - list of values defined by the enumeration
    cls.trans_name - reverse dictionary mapping value to string ready for
    translation

    Example:

    >>> class X(object):
    >>>     __metaclass__ = EnumMetaclass
    >>>     A = 1
    >>>     B = 2
    >>>     C = 3

    >>> X.names
    {1: 'A', 2: 'B', 3: 'C'}

    >>> X.values
    [1, 2, 3]

    >>> X.pairs
    [(1, 'A'), (2, 'B'), (3, 'C')]

    >>> X.trans_names
    {1: 'X.A', 2: 'X.B', 3: 'X.C'}
    """
    allowed_types = tuple(chain(string_types, integer_types, [float]))

    def __new__(cls, name, bases, attrs):
        names = {}
        trans_names = {}
        str2val = {}

        def is_val(x):  # pylint: disable=missing-docstring
            return x.isupper() or x[0].isupper()

        for attr_name, attr_val in attrs.items():
            if is_val(attr_name) and isinstance(attr_val, cls.allowed_types):
                str2val[attr_name]    = attr_val
                names[attr_val]       = attr_name
                trans_names[attr_val] = name + u"." + attr_name

        attrs['names']       = names
        attrs['choices']     = sorted(names.items())
        attrs['str2val']     = str2val
        attrs['values']      = sorted(names.keys())
        attrs['trans_names'] = trans_names

        return type.__new__(cls, name, bases, attrs)


class Enum(object):
    """ Base class for enum.

    This exists so that you don't have to manually specify `EnumMetaclass` for
    all enums but can just derive from `Enum` instead. This way the magic
    is less exposed and the code is more readable.
    """
    __metaclass__ = EnumMetaclass


def iterable(collection):
    """Checks if the variable is not a basestring instance and can be
    enumerated.
    """
    # strings can be iterated - that's not what we want
    if isinstance(collection, string_types):
        return False

    # avoid opening a generator
    if isinstance(collection, types.GeneratorType):
        return True

    try:
        iter(collection)
    except TypeError:
        return False

    return True


def isstaticmethod(cls, name):
    """ Check whether a method with the given *name* is a static method.

    :param type cls:
        The class containing the method.
    :param str|unicode name:
        The name of the method to check.
    :return bool:
        **True** if the method is static.
    """
    method = getattr(cls, name)
    if ismethod(method) and method.__self__ is cls:
        return True
    return False


def methodtype(cls, name):
    """
    :return int:
        0 - Not a method
        1 - instance method
        2 - class method
    """
    method = getattr(cls, name)
    if ismethod(method):
        if method.__self__ is cls:
            return 2
        return 1
    return 0


def isfile(obj):
    """ Check if the given object is file-like. """
    return hasattr(obj, 'flush') and hasattr(obj, 'readline')
