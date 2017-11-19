# -*- coding: utf-8 -*-
"""
Built-in serializers for most basic uses cases.

Those are provided as they would have to be reimplemented time and time again
by each project. Having them as part of the library will also allow some
performance optimisation in the `Serializer` itself.
"""
from __future__ import absolute_import, unicode_literals

# stdlib imports
from datetime import date as Date, datetime as Datetime
from decimal import Decimal
from itertools import chain
from logging import getLogger

# 3rd party imports
from six import integer_types, string_types, binary_type

# local imports
from .core import serialize
from .util import is_file


L = getLogger(__name__)
PRIMITIVES = tuple(chain(
    integer_types,
    string_types,
    (float, binary_type, Date, Datetime, Decimal)
))


def serialize_dict(dct, spec, ctx):
    """ Serialize dictionary. """
    ret = {}

    if spec is True or spec.empty():
        return {}

    for name, value in dct.items():
        if name in spec:
            try:
                ret[name] = serialize.raw(value, spec[name], ctx)
            except ValueError:
                pass
    return ret


def serialize_primitive(obj, spec, ctx):
    """ Serialize a primitive value. """
    return ctx.dumpval('', obj)


def serialize_iterable(obj, spec, ctx):
    """ Serialize any iterable except a string.

    Since strings are a very special case of iterables, they are handled
    differently (otherwise they would be serialized as an array of chars).
    """
    ret = []
    for item in obj:
        ret.append(serialize.raw(item, spec, ctx))
    return ret


def serialize_file_handle(obj, spec, ctx):
    """ Serializer for file handles. """
    return '(file handle)'


def serialize_serializable(obj, spec, ctx):
    """ Serialize any class that defines a ``serialize`` method. """
    return obj.serafin_serialize(spec, ctx)


class ThirdPartySerializer(object):
    """ A serializer for integrating with 3rd party solutions.

    This will use a given method on the object to return the dict and then
    use `serialize_dict` to filter the results according to the specification.

    This will be slower than implementing a direct `serafin_serialize()` method
    but will work with things like AppEngine ndb models ``to_dict()`` method out
    of the box.
    """
    def __init__(self, method_name):
        self.method_name = method_name

    def __call__(self, obj, spec, ctx):
        method = getattr(obj, self.method_name)
        data = method()
        return serialize_dict(data, spec, ctx)


def serialize_object(obj, spec, ctx):
    """ Serialize any object.

    This should have the lowest priority as it will work for almost anything
    but it might be a bit slow. It's generally much better to use other,
    dedicated, serializers and leave this as a last resort. Having this makes
    the system very flexible but at the same time it might slow down the
    serialization time significantly.
    """
    if spec is True or spec.empty():
        return {}

    filters = [
        lambda n, v: not (n.startswith('__') or n.endswith('__')),
        lambda n, v: not callable(v),
        lambda n, v: not is_file(v),
    ]

    def is_val(attr_name, attr_value):
        """
        Check if the given attribute is a value that should be serialized.
        """
        try:
            return all(flt(attr_name, attr_value) for flt in filters)
        except:
            return False

    ret = {}
    for name in dir(obj):
        if not isinstance(name, string_types):
            pass
        if name in spec:
            try:
                value = getattr(obj, name)
            except Exception as ex:
                value = "({}: {})".format(ex.__class__.__name__, str(ex))
                if ctx.reraise:
                    raise

            if is_val(name, value):
                ret[name] = serialize.raw(
                    value, spec[name], ctx
                )
    return ret
