#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, CESNET, z. s. p. o.
# Use of this source is governed by an ISC license, see LICENSE file.

"""Simple typed collections library.

Defines TypedDict and TypedList, which enforce inserted types based on simple
type definition.
"""

__version__ = '0.1.10'
__author__ = 'Pavel Kácha <pavel.kacha@cesnet.cz>'

import collections
import abc


class KeyNotAllowed(LookupError):
    """ Raised when untyped key is inserted on type, which does not allow
        for untyped keys.
    """


class KeysRequired(LookupError):
    """ Raised when required keys are missing in dictionary (usually on the
        call of checkRequired method.
    """

class Discard(Exception):
    """ Sentinel class to signal expected dropping of the key.
        Can be returned or raised from type enforcing callable,
        and can itself be used as type enforcing callable.
    """

    @classmethod
    def __call__(cls, x=None):
        return cls

def Any(v):
    return v


def dictify_typedef(typedef):
    for key in typedef:
        tdef = typedef[key]
        if callable(tdef):
            typedef[key] = {"type": tdef}
        typedef[key].setdefault("type", Any)


class TypedDictMetaclass(abc.ABCMeta):
    """ Metaclass for TypedDict, allowing simplified typedefs - if typedef is
        callable, simple type object is assumed and correct dict is created.
        Metaclassed to be run just once for the class, not for each instance.
    """

    def __init__(cls, name, bases, dct):
        super(TypedDictMetaclass, cls).__init__(name, bases, dct)
        dictify_typedef(cls.typedef)


class TypedDictBase(collections.MutableMapping):
    """ Dictionary type abstract class, which supports checking of inserted
        types, based on simple type definition.

        Must be subclassed, and subclass must populate 'typedef' dict, and may
        also reassign allow_unknown and dict_class class attributes.

        typedef: dictionary with keys and their type definitions. Type definition
            may be simple callable (int, string, check_func,
            AnotherTypedDict), or dict with the following members:
                "type":
                    type enforcing callable. If callable returns, raises
                    or is Discard, key will be silently discarded
                "default":
                    new TypedDict subclass will be initialized with keys
                    with this value; deleted keys will also revert to it
                "required":
                    bool, checkRequired method will report the key if not present
                "description":
                    string, explaining field type in human readable terms
                    (will be used in exception explanations)
            Type enforcing callable must take one argument, and return value,
            coerced to expected type. Coercion may even be conversion, for example
            arbitrary date string, converted to DateTime.

        allow_unknown: boolean, specifies whether dictionary allows unknown keys,
            that means keys, which are not defined in 'typedef'

        dict_class: class or factory for underlying dict implementation
    """

    typedef = {}
    allow_unknown = False
    dict_class = dict

    def __init__(self, init_data=None):
        self.data = self.dict_class()
        self.clear()
        self.update(init_data or {})

    def clear(self):
        self.data.clear()
        for key in self.typedef.keys():
            self.initItemDefault(key)

    def initItemDefault(self, key):
        """ Sets 'key' to the default value from typedef (if defined) """
        tdef = self.getTypedef(key)
        try:
            default = tdef["default"]
        except KeyError:
            pass
        else:
            if default is Discard:
                return
            try:
                # Call if callable
                default = default()
            except Discard:
                return
            except TypeError:
                pass
            self[key] = default

    def getTypedef(self, key):
        """ Get type definition for 'key'.
            If key is not defined and allow_unknown is True, empty
            definition is returned, otherwise KeyNotAllowed gets raised.
        """
        tdef = {}
        try:
            tdef = self.typedef[key]
        except KeyError:
            if not self.allow_unknown:
                raise KeyNotAllowed(key)
        return tdef

    def checkRequired(self):
        """ The class does not check missing items by itself (we need it to
            be incomplete during creation and manipulation), so this checks
            and return list of missing required keys explicitly.

            Note that the check is not recursive (as instance dictionary
            may contain another subclasses of TypedDict), so care must
            be taken if there is such concern.
        """
        missing = ()
        for key, tdef in self.typedef.items():
            if tdef.get("required", False) and not key in self.data:
                missing = missing + (key,)
        if missing:
            raise KeysRequired(missing)

    def __setitem__(self, key, value):
        """ Setter with type coercion.
            Any exception, raised from type enforcing callable, will get
            modified - first .arg will be tuple of key hierarchy, last
            .arg will be message from "description" field in type definition
        """
        tdef = self.getTypedef(key)
        valuetype = tdef["type"]
        if valuetype is Discard:
            return
        try:
            fvalue = valuetype(value)
        except Discard:
            return
        except Exception as e:
            if isinstance(e.args[0], tuple):
                e.args = ((key,) + e.args[0],) + e.args[1:]
            else:
                e.args = ((key,),) + e.args
            if len(e.args) < 3:
                desc = tdef.get("description", None)
                if desc is not None:
                    e.args = e.args + (desc,)
            raise
        if fvalue is Discard:
            return
        self.data[key] = fvalue

    def __getitem__(self, key):
        return self.data[key]

    def __delitem__(self, key):
        """ Deleter with reverting to defaults """
        del self.data[key]
        self.initItemDefault(key)

    # Following definitions are not strictly necessary as MutableMapping
    # already defines them, however we can override them by calling to
    # possibly more optimized underlying implementations.
    def __iter__(self): return iter(self.data)

    def itervalues(self): return self.data.itervalues()

    def iteritems(self): return self.data.iteritems()

    def keys(self): return self.data.keys()

    def values(self): return self.data.values()

    def __len__(self): return len(self.data)

    def __str__(self): return "%s(%s)" % (type(self).__name__, str(self.data))

    def __repr__(self): return "%s(%s)" % (type(self).__name__, repr(self.data))


# Py 2 requires metaclassing by __metaclass__ attribute, whereas Py 3
# needs metaclass argument. What actually happens is the following,
# so we will do it explicitly, to be compatible with both versions.
TypedDict = TypedDictMetaclass("TypedDict", (TypedDictBase,), {})


class TypedefSetter(object):
    """ Setter for OpenTypedDict.typedef value, which forces typedef canonicalisation.
        Implemented as setter only class, as it does not intercept and slow down read
        access.
    """

    def __set__(self, obj, value):
        dictify_typedef(value)
        obj.__dict__["typedef"] = value


class OpenTypedDict(TypedDictBase):
    """ Dictionary type class, which supports checking of inserted types, based on
        simple type definition, which must be provided in constructor and is changeable
        by assigning instance.typedef variable.

        Note however that changing already populated OpenTypedDict's typedef to
        incompatible definition may lead to undefined results and data inconsistent
        with definition.
    """

    def __init__(self, init_data=None, typedef=None, allow_unknown=False, dict_class=dict):
        """ init_data: initial values

            typedef: dictionary with keys and their type definitions. Type definition
                may be simple callable (int, string, check_func,
                AnotherTypedDict), or dict with the following members:
                    "type":
                        type enforcing callable. If callable returns, raises
                        or is Discard, key will be silently discarded
                    "default":
                        new TypedDict subclass will be initialized with keys
                        with this value; deleted keys will also revert to it
                    "required":
                        bool, checkRequired method will report the key if not present
                    "description":
                        string, explaining field type in human readable terms
                        (will be used in exception explanations)
                Type enforcing callable must take one argument, and return value,
                coerced to expected type. Coercion may even be conversion, for example
                arbitrary date string, converted to DateTime.

            allow_unknown: boolean, specifies whether dictionary allows unknown keys,
                that means keys, which are not defined in 'typedef'

            dict_class: class or factory for underlying dict implementation
        """
        self.allow_unknown = allow_unknown
        self.dict_class = dict_class
        self.typedef = typedef or {}
        super(OpenTypedDict, self).__init__(init_data)

    typedef = TypedefSetter()

    def __call__(self, data):
        """ Instances are made callable so they can be used in nested "type"
            definitions. Note however that these classes are mutable, so
            assigning new values replaces old ones.
        """
        self.update(data)
        return self


class TypedList(collections.MutableSequence):
    """ List type abstract class, which supports checking of inserted items
        type.

        Must be subclassed, and subclass must populate 'item_type' class
        variable, and may also reassign list_class class attributes.

        item_type: type enforcing callable, wich must take one argument, and
            return value, coerced to expected type. Coercion may even be
            conversion, for example arbitrary date string, converted to
            DateTime. Because defined within class, Python authomatically
            makes it object method, so it must be wrapped in staticmethod(...)
            explicitly.
        list_class: class or factory for underlying list implementation
    """

    item_type = staticmethod(Any)
    list_class = list

    def __init__(self, iterable):
        self.data = self.list_class()
        self.extend(iterable)

    def __getitem__(self, val): return self.data[val]

    def __delitem__(self, val): del self.data[val]

    def __len__(self): return len(self.data)

    def __setitem__(self, idx, val):
        tval = self.item_type(val)
        self.data[idx] = tval

    def insert(self, idx, val):
        tval = self.item_type(val)
        self.data.insert(idx, tval)

    # Following definitions are not strictly necessary as MutableSequence
    # already defines them, however we can override them by calling to
    # possibly more optimized underlying implementations.

    def __contains__(self, val):
        tval = self.item_type(val)
        return tval in self.data

    def index(self, val):
        tval = self.item_type(val)
        return self.data.index(tval)

    def count(self, val):
        tval = self.item_type(val)
        return self.data.count(tval)

    def __iter__(self): return iter(self.data)

    def reverse(self): return self.data.reverse()

    def __reversed__(self): return reversed(self.data)

    def pop(self, index=-1): return self.data.pop(index)

    def __str__(self): return "%s(%s)" % (type(self).__name__, str(self.data))

    def __repr__(self): return "%s(%s)" % (type(self).__name__, repr(self.data))


def typed_list(name, item_type):
    """ Helper for oneshot type definition """
    return type(name, (TypedList,), dict(item_type=staticmethod(item_type)))


def typed_dict(name, allow_unknown, typedef):
    """ Helper for oneshot type definition """
    return type(name, (TypedDict,), dict(allow_unknown=allow_unknown, typedef=typedef))
