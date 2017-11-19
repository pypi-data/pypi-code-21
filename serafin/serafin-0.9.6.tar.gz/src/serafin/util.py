# -*- coding: utf-8 -*-
""" Various helpers used by the serialization library. """
from __future__ import absolute_import, print_function, unicode_literals

# stdlib imports
import types

# 3rd party imports
from six import string_types


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


def is_file(obj):
    """ Check if the given object is file-like. """
    return hasattr(obj, 'flush') and hasattr(obj, 'readline')
