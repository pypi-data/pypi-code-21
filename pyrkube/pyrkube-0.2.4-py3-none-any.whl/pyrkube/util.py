"""
pyrkube.client
~~~~~~~~~~~~~~

Utility classes and functions for pyrkube.

:copyright: (c) 2017 by Joe Black.
:license: Apache2.
"""

import json
import time
import logging
from pprint import pformat


class cached_property(object):
    '''Decorator for read-only properties evaluated only once within TTL period.

    It can be used to create a cached property like this::

        import random

        # the class containing the property must be a new-style class
        class MyClass(object):
            # create property whose value is cached for ten minutes
            @cached_property(ttl=600)
            def randint(self):
                # will only be evaluated every 10 min. at maximum.
                return random.randint(0, 100)

    The value is cached  in the '_cache' attribute of the object instance that
    has the property getter method wrapped by this decorator. The '_cache'
    attribute value is a dictionary which has a key for every property of the
    object which is wrapped by this decorator. Each entry in the cache is
    created only when the property is accessed for the first time and is a
    two-element tuple with the last computed property value and the last time
    it was updated in seconds since the epoch.

    The default time-to-live (TTL) is 300 seconds (5 minutes). Set the TTL to
    zero for the cached value to never expire.

    To expire a cached property value manually just do::

        del instance._cache[<property name>]

    '''
    def __init__(self, ttl=300):
        self.ttl = ttl

    def __call__(self, fget, doc=None):
        self.fget = fget
        self.__doc__ = doc or fget.__doc__
        self.__name__ = fget.__name__
        self.__module__ = fget.__module__
        return self

    def __get__(self, inst, owner):
        now = time.time()
        try:
            value, last_update = inst._cache[self.__name__]
            if self.ttl > 0 and now - last_update > self.ttl:
                raise AttributeError
        except (KeyError, AttributeError):
            value = self.fget(inst)
            if value:
                try:
                    cache = inst._cache
                except AttributeError:
                    cache = inst._cache = {}
                cache[self.__name__] = (value, now)
        return value


class ReprMixin:
    """Provide repr and IPython pretty print repr based on public attrs."""
    def __repr__(self):
        return '%s(%s)' % (
            type(self).__name__,
            pformat({k: v for k, v in self.items() if not k.startswith('_')})
        )

    def _repr_pretty_(self, p, cycle):
        if not cycle:
            pretty_repr(p, self)


class PrivAttrKeyMixin:
    """Add methods that provide dictionary type functions that exclude
    all but public attributes.
    """
    def keys(self):
        """dict like keys method for only public attributes."""
        return (k for k in dict.keys(self) if not k.startswith('_'))

    def values(self):
        """dict like values method for only public attributes."""
        return (v for k, v in dict.items(self) if not k.startswith('_'))

    def items(self):
        """dict like items method for only public attributes."""
        return ((k, v) for k, v in dict.items(self) if not k.startswith('_'))

    def __iter__(self):
        return iter(self.keys())

    def __len__(self):
        return len(list(self.keys()))


# class adict(ReprMixin, PrivAttrKeyMixin, attrdict.AttrDict):
#     """Customized attribute dictionary type."""
#     def __init__(self, *args, **kwargs):
#         def convert(o):
#             """Recursor for recursively converting object to adict."""
#             if isinstance(o, dict):
#                 return adict((k, convert(v)) for k, v in o.items())
#             elif isinstance(o, (list, tuple)):
#                 return type(o)(convert(v) for v in o)
#             return o

#         if args:
#             obj, *args = args
#         elif kwargs:
#             obj = kwargs
#         else:
#             obj = {}

#         if not isinstance(obj, types.GeneratorType):
#             obj = copy.deepcopy(obj)
#         attrdict.AttrDict.__init__(self, convert(obj), *args)

#     @classmethod
#     def _valid_name(cls, key):
#         return (
#             isinstance(key, six.string_types) and
#             re.match('^[A-Za-z_][A-Za-z0-9_]*$', key)
#         )
#         # and not hasattr(cls, key)

#     def __getattr__(self, key):
#         if key not in self or not self._valid_name(key):
#             raise AttributeError(
#                 "'{cls}' instance has no attribute '{name}'".format(
#                     cls=self.__class__.__name__, name=key
#                 )
#             )

#         return self[key]


class WrappedMapMixin:
    """Add dictionary accessor methods that wrap self._wrapped reference."""
    def __contains__(self, key):
        return key in self._wrapped

    def __getitem__(self, key):
        return self._wrapped[key]

    def __setitem__(self, key, value):
        self._wrapped[key] = value

    def __delitem__(self, key):
        del self._wrapped[key]

    def keys(self):
        """Return the wrapped object's keys method."""
        return self._wrapped.keys()

    def values(self):
        """Return the wrapped object's values method."""
        return self._wrapped.values()

    def items(self):
        """Return the wrapped object's items method."""
        return self._wrapped.items()

    def __iter__(self):
        return iter(self._wrapped)


def pretty_repr(p, obj):
    """Handles the ipython pretty printer repr object."""
    items = sorted(
        [(k, v) for k, v in obj.items() if not k.startswith('_')])

    with p.group(2, type(obj).__name__ + '(', ')'):
        p.breakable('')
        for index, (key, val) in enumerate(items):
            if index:
                p.text(",")
                p.breakable()
            with p.group(2, key + '=', ''):
                p.pretty(val)


def setup_logging(level):
    """This will setup logging for the module."""
    log = logging.getLogger('pyrkube')
    level = getattr(logging, level)
    log.setLevel(level)
    handler = logging.NullHandler()
    handler.setLevel(level)
    log.addHandler(handler)
    logging.raiseExceptions = False
    return log


def deserialize(value):
    """Safely attempt to deserialized a string."""
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value
