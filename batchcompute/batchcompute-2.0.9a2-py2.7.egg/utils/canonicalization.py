'''
Functions and classes to make interfaces or keys canonicalization.
'''
import re
from datetime import timedelta
from weakref import WeakSet

from .functions import (
    partial, timestamp_datetime, import_json, timediff, str2datetime,
    utc2local
)
from .constants import STATE_MAP, PY2, PY3, STRING
# from batchcompute.core.exceptions import JsonError

json = import_json()

class _C: pass
_InstanceType = type(_C())

class ABCMeta(type):

    """Metaclass for defining Abstract Base Classes (ABCs).

    Use this metaclass to create an ABC.  An ABC can be subclassed
    directly, and then acts as a mix-in class.  You can also register
    unrelated concrete classes (even built-in classes) and unrelated
    ABCs as 'virtual subclasses' -- these and their descendants will
    be considered subclasses of the registering ABC by the built-in
    issubclass() function, but the registering ABC won't show up in
    their MRO (Method Resolution Order) nor will method
    implementations defined by the registering ABC be callable (not
    even via super()).

    """

    # A global counter that is incremented each time a class is
    # registered as a virtual subclass of anything.  It forces the
    # negative cache to be cleared before its next use.
    _abc_invalidation_counter = 0

    def __new__(mcls, name, bases, namespace):
        cls = super(ABCMeta, mcls).__new__(mcls, name, bases, namespace)
        # Compute set of abstract method names
        abstracts = set(name
                     for name, value in namespace.items()
                     if getattr(value, "__isabstractmethod__", False))
        for base in bases:
            for name in getattr(base, "__abstractmethods__", set()):
                value = getattr(cls, name, None)
                if getattr(value, "__isabstractmethod__", False):
                    abstracts.add(name)
        cls.__abstractmethods__ = frozenset(abstracts)
        # Set up inheritance registry
        cls._abc_registry = WeakSet()
        cls._abc_cache = WeakSet()
        cls._abc_negative_cache = WeakSet()
        cls._abc_negative_cache_version = ABCMeta._abc_invalidation_counter
        return cls

    def register(cls, subclass):
        """Register a virtual subclass of an ABC."""
        if not isinstance(subclass, (type, types.ClassType)):
            raise TypeError("Can only register classes")
        if issubclass(subclass, cls):
            return  # Already a subclass
        # Subtle: test for cycles *after* testing for "already a subclass";
        # this means we allow X.register(X) and interpret it as a no-op.
        if issubclass(cls, subclass):
            # This would create a cycle, which is bad for the algorithm below
            raise RuntimeError("Refusing to create an inheritance cycle")
        cls._abc_registry.add(subclass)
        ABCMeta._abc_invalidation_counter += 1  # Invalidate negative cache

    def _dump_registry(cls, file=None):
        """Debug helper to print the ABC registry."""
        print >> file, "Class: %s.%s" % (cls.__module__, cls.__name__)
        print >> file, "Inv.counter: %s" % ABCMeta._abc_invalidation_counter
        for name in sorted(cls.__dict__.keys()):
            if name.startswith("_abc_"):
                value = getattr(cls, name)
                print >> file, "%s: %r" % (name, value)

    def __instancecheck__(cls, instance):
        return cls.__simplecheck__(instance) or cls.__detailcheck__(instance)

    def __detailcheck__(cls, instance):
        if hasattr(cls, "__instancehook__"):
            return cls.__instancehook__(instance)
        return False

    def __simplecheck__(cls, instance):
        """Override for isinstance(instance, cls)."""
        # Inline the cache checking when it's simple.
        subclass = getattr(instance, '__class__', None)
        if subclass is not None and subclass in cls._abc_cache:
            return True

        subtype = type(instance)
        # Old-style instances
        if subtype is _InstanceType:
            subtype = subclass
        if subtype is subclass or subclass is None:
            if (cls._abc_negative_cache_version ==
                ABCMeta._abc_invalidation_counter and
                subtype in cls._abc_negative_cache):
                return False
            # Fall back to the subclass check.
            return cls.__subclasscheck__(subtype)
        return (cls.__subclasscheck__(subclass) or
                cls.__subclasscheck__(subtype))


    def __subclasscheck__(cls, subclass):
        """Override for issubclass(subclass, cls)."""
        # Check cache
        if subclass in cls._abc_cache:
            return True
        # Check negative cache; may have to invalidate
        if cls._abc_negative_cache_version < ABCMeta._abc_invalidation_counter:
            # Invalidate the negative cache
            cls._abc_negative_cache = WeakSet()
            cls._abc_negative_cache_version = ABCMeta._abc_invalidation_counter
        elif subclass in cls._abc_negative_cache:
            return False
        # Check the subclass hook
        ok = cls.__subclasshook__(subclass)
        if ok is not NotImplemented:
            assert isinstance(ok, bool)
            if ok:
                cls._abc_cache.add(subclass)
            else:
                cls._abc_negative_cache.add(subclass)
            return ok
        # Check if it's a direct subclass
        if cls in getattr(subclass, '__mro__', ()):
            cls._abc_cache.add(subclass)
            return True
        # Check if it's a subclass of a registered class (recursive)
        for rcls in cls._abc_registry:
            if issubclass(subclass, rcls):
                cls._abc_cache.add(subclass)
                return True
        # Check if it's a subclass of a subclass (recursive)
        for scls in cls.__subclasses__():
            if issubclass(subclass, scls):
                cls._abc_cache.add(subclass)
                return True
        # No dice; update negative cache
        cls._abc_negative_cache.add(subclass)
        return False


class CamelCasedClass(ABCMeta):
    '''
    MetaClass for all classes which expected supply lower-camel-case methods
    instead of methods with `_` joined lower cases.

    Mainly add descriptor for each property descripted in description dict.

    e.g.:
        You can get JobId of a job status 'j' through both j.jobId and
        j.getJobId(), and the like.

    '''
    def __new__(cls, nm, parents, attrs):
        super_new = super(CamelCasedClass, cls).__new__

        tmp_dct = dict()
        for name, value in attrs.items():
            if not name.startswith('__') and not name.endswith('__'):
                tmp_dct[name] = value
        attrs.update(tmp_dct)

        # Create property for each key in `description_map` dict.
        # Besides, if `descriptor_type` is data descriptor, a `getxxx` and
        # a `setxxx` method also will be added to `cls`, if `descriptor_type`
        # is non data descriptor, only a `getxxx` method added.
        if 'descriptor_map' in attrs:
            for attr in attrs['descriptor_map']:
                # Definition of getter and setter method for properties.
                def get_attr(attr, self):
                    return self.getproperty(attr)
                def set_attr(attr, self, value):
                    self.setproperty(attr, value)

                property_name = attr
                getter = partial(get_attr, attr)
                setter = partial(set_attr, attr)
                # Add property to class.
                if attrs['descriptor_type'] == 'data descriptor':
                    # data descriptor.
                    attrs[property_name] = property(getter, setter, None, attr)
                else:
                    # non data descriptor.
                    attrs[property_name] = property(getter, None, None, attr)
        return super_new(cls, nm, parents, attrs)


def remap(container, human_readable=False):
    '''
    Canonicalize keys in container to standard names.

    `container` must be a list, dict or string.
    '''

    if not container:
        if isinstance(container, STRING):
            return dict()
        else:
            return container

    from batchcompute.core.exceptions import JsonError
    s = ""
    try:
        if PY2:
            if isinstance(container, str):
                s = container.strip()
                container = json.loads(s) if s else dict()
        else:
            # For Python 3 compatibility.
            if isinstance(container, bytes):
                s = str(container, encoding='utf-8').strip()
                container = json.loads(s) if s else dict()
    except Exception:
        raise JsonError(s)

    new_container = type(container)()
    if isinstance(container, dict):
        new_container.update(container)
    else:
        new_container = container

    get_iter = lambda c: c.items() if isinstance(c, dict) else enumerate(c)
    # Make all keys canonical recursively.
    for key, value in get_iter(new_container):
        # XXX maybe unicode
        if isinstance(key, STRING) and key.endswith('Time'):
            # Convert epoch time to human readable time format.
            new_value = utc2local(str2datetime(value))
        elif isinstance(value, (list, dict)):
            # Only for ListResponse.
            new_value = remap(value, human_readable) 
        else:
            new_value = value
        new_container[key] = new_value
    return new_container
