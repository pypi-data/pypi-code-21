from __future__ import nested_scopes, generators, division, absolute_import, with_statement, print_function,\
    unicode_literals

from future import standard_library
from future.utils import native_str

from serial.utilities import qualified_name

standard_library.install_aliases()
from builtins import *
#

import collections
import json
from base64 import b64encode
from collections import OrderedDict, Callable, Set, Sequence
from copy import deepcopy, copy
from io import IOBase, UnsupportedOperation
from itertools import chain

import serial

try:
    import typing
    from typing import Union, Any, AnyStr
except ImportError:
    typing = Union = Any = AnyStr = None

import yaml

if hasattr(collections, 'Generator'):
    Generator = collections.Generator
else:
    Generator = type(n for n in (1, 2, 3))


def marshal(data, types=None, value_types=None, item_types=None):
    # type: (Any, Optional[typing.Sequence[Union[type, serial.properties.Property]]]) -> Any
    """
    Recursively converts instances of ``serial.model.Object`` into JSON/YAML serializable objects.
    """
    if hasattr(data, '_marshal'):
        return data._marshal()
    elif data is None:
        return data
    if isinstance(types, Callable):
        types = types(data)
    if types is not None:
        if (str in types) and (native_str is not str) and (native_str not in types):
            types = tuple(chain(*(
                ((t, native_str)  if (t is str) else (t,))
                for t in types
            )))
        matched = False
        for t in types:
            if isinstance(t, serial.properties.Property):
                try:
                    data = t.marshal(data)
                    matched = True
                    break
                except TypeError:
                    pass
            elif isinstance(t, type) and isinstance(data, t):
                matched = True
                break
        if not matched:
            raise TypeError(
                '%s cannot be interpreted as any of the designated types: %s' % (
                    repr(data),
                    repr(types)
                )
            )
    if isinstance(data, native_str):
        return data
    elif isinstance(data, (bytes, bytearray)):
        return str(b64encode(data), 'ascii')
    elif hasattr(data, '__bytes__'):
        return str(b64encode(bytes(data)), 'ascii')
    else:
        return data


def unmarshal(data, types=None, value_types=None, item_types=None):
    # type: (Any, Optional[typing.Sequence[Union[type, serial.properties.Property]]]) -> typing.Any
    """
    Convert ``data`` into ``serial.model`` representations of same.
    """
    if data is None:
        return data
    if isinstance(types, Callable):
        types = types(data)
    if isinstance(data, Generator):
        data = tuple(data)
    if types is None:
        if isinstance(data, (dict, OrderedDict)) and not isinstance(data, Dictionary):
            data = Dictionary(data, value_types=value_types)
        elif isinstance(data, (Set, Sequence)) and (not isinstance(data, (str, bytes, Array))):
            data = Array(data, item_types=item_types)
        return data
    elif (str in types) and (native_str is not str) and (native_str not in types):
        types = tuple(chain(*(
            ((t, native_str)  if (t is str) else (t,))
            for t in types
        )))
    matched = False
    error = None
    for t in types:
        if isinstance(
            t,
            serial.properties.Property
        ):
            try:
                data = t.unmarshal(data)
                matched = True
                break
            except (AttributeError, KeyError, TypeError, ValueError) as e:
                error = e
                continue
        elif isinstance(t, type):
            if issubclass(t, Object) and isinstance(data, (dict, OrderedDict)):
                try:
                    data = t(data)
                    matched = True
                    break
                except (AttributeError, KeyError, TypeError, ValueError) as e:
                    error = e
                    pass
            elif isinstance(data, (dict, OrderedDict, Dictionary)) and issubclass(t, (dict, OrderedDict, Dictionary)):
                data = Dictionary(data, value_types=value_types)
                matched = True
                break
            elif (
                isinstance(data, (Set, Sequence, Generator)) and
                (not isinstance(data, (str, bytes))) and
                issubclass(t, (Set, Sequence)) and
                (not issubclass(t, (str, bytes)))
            ):
                data = Array(data, item_types=item_types)
                matched = True
                break
            elif isinstance(data, t):
                matched = True
                break
    if not matched:
        if not matched:
            if len(types) == 1 and (error is not None):
                raise error
            else:
                raise TypeError(
                    '\n   The data provided does not fit any of the types indicated:\n' +
                    '     - data: %s\n' % serialize(data) +
                    '     - types: %s' % repr(types)
                )
    return data


def serialize(data, data_format='json'):
    # type: (Any, str) -> str
    """
    Serializes instances of ``serial.model.Object`` as JSON or YAML.
    """
    h = None
    if isinstance(data, (Object, Dictionary, Array)):
        h = data._hooks or type(data)._hooks
        if (h is not None) and (h.before_serialize is not None):
            data = h.before_serialize(data)
    if data_format not in ('json', 'yaml'):
        data_format = data_format.lower()
        if data_format not in ('json', 'yaml'):
            raise ValueError(
                'Supported `serial.model.serialize()` `format_` values include "json" and "yaml" (not "%s").' % data_format
            )
    if data_format == 'json':
        data = json.dumps(marshal(data))
    elif data_format == 'yaml':
        data = yaml.dump(marshal(data))
    if (h is not None) and (h.after_serialize is not None):
        data = h.after_serialize(data)
    return data


def deserialize(data):
    if isinstance(data, IOBase):
        try:
            data.seek(0)
        except UnsupportedOperation:
            pass
        if hasattr(data, 'readall'):
            data = data.readall()
        else:
            data = data.read()
    if isinstance(data, bytes):
        data = str(data, encoding='utf-8')
    if isinstance(data, str):
        try:
            data = json.loads(data, object_hook=OrderedDict, object_pairs_hook=OrderedDict)
        except ValueError:
            data = yaml.load(data)
    return data


def validate(data, types=None):
    # type: (Union[Object, Array, Dictionary], Optional[Union[type, serial.properties.Property, Object]]) -> None
    if types is not None:
        if isinstance(types, collections.Callable):
            types = types(data)
        if (str in types) and (native_str is not str) and (native_str not in types):
            types = tuple(chain(*(
                ((t, native_str)  if (t is str) else (t,))
                for t in types
            )))
        valid = False
        for t in types:
            if isinstance(t, type) and isinstance(data, t):
                valid = True
                break
            elif isinstance(t, serial.properties.Property):
                if t.types is None:
                    valid = True
                    break
                try:
                    validate(data, t.types)
                    valid = True
                    break
                except serial.errors.ValidationError:
                    continue
        if not valid:
            raise serial.errors.ValidationError(
                '\n`data` is invalid:\n%s\n`data` must be one of the following types:\n%s.' % (
                    '\n'.join('   ' + l for l in repr(data).split('\n')),
                    '\n'.join(
                        repr(Array(types)).split('\n')[1:-1]
                    )
                )
            )
    if ('_validate' in dir(data)) and isinstance(data._validate, collections.Callable):
        data._validate()


def version(data, specification, version_number):
    # type: (Any, str, Union[str, int, typing.Sequence[int]]) -> Any
    """
    Recursively alters instances of ``serial.model.Object`` according to version_number metadata associated with that
    object's serial.properties.

    Arguments:

        - data

        - specification (str): The specification to which the ``version_number`` argument applies.

        - version_number (str|int|[int]): A version number represented as text (in the form of integers separated by
          periods), an integer, or a sequence of integers.
    """
    if isinstance(data, Object):
        im = data._meta
        cm = im or type(data)._meta
        for n, p in tuple((im or cm).properties.items()):
            if p.versions is not None:
                version_match = False
                specification_match = False
                for v in p.versions:
                    if v.specification == specification:
                        specification_match = True
                        if v == version_number:
                            version_match = True
                            break
                if specification_match and (not version_match):
                    if im is None:
                        im = serial.meta.get(data)
                    v = getattr(data, n)
                    if v is not None:
                        raise serial.errors.VersionError(
                            '%s - the property `%s` is not applicable in %s version %s:\n%s' % (
                                qualified_name(type(data)),
                                n,
                                specification,
                                version_number,
                                str(data)
                            )
                        )
                    del im.properties[n]
        for n, p in (im or cm).properties.items():
            version(getattr(data, n), specification, version_number)
    elif isinstance(data, (collections.Set, collections.Sequence)) and not isinstance(data, (str, bytes)):
        for d in data:
            version(d, specification, version_number)
    elif isinstance(data, (dict, OrderedDict)):
        for k, v in data.items():
            version(v, specification, version_number)


class Object(object):

    _meta = None  # type: Optional[serial.meta.Object]
    _hooks = None  # type: Optional[serial.hooks.Object]

    def __init__(
        self,
        _=None,  # type: Optional[Union[AnyStr, typing.Mapping, typing.Sequence, typing.IO]]
    ):
        self._meta = None
        self._hooks = None
        if _ is not None:
            if isinstance(_, Object):
                if _._meta or (type(_)._meta is not type(self)._meta):
                    self._meta = deepcopy(_._meta or type(_)._meta)
                if _._hooks or (type(_)._hooks is not type(self)._hooks):
                    self._hooks = deepcopy(_._hooks or type(_)._hooks)
                m = self._meta or type(self)._meta
                for k in m.properties.keys():
                    try:
                        setattr(self, k, getattr(_, k))
                    except TypeError as e:
                        label = '\n - %s.%s: ' % (qualified_name(type(self)), k)
                        if e.args:
                            e.args = tuple(
                                chain(
                                    (label + e.args[0],),
                                    e.args[1:]
                                )
                            )
                        else:
                            e.args = (label + serialize(_),)
                        raise e
            else:
                if isinstance(_, IOBase):
                    if hasattr(_, 'url'):
                        serial.meta.get(self).url = _.url
                    elif hasattr(_, 'name'):
                        serial.meta.get(self).path = _.name
                _ = deserialize(_)
                if isinstance(_, dict):
                    for k, v in _.items():
                        try:
                            self[k] = v
                        except KeyError as e:
                            if e.args and len(e.args) == 1:
                                e.args = (
                                    r'%s.%s: %s' % (qualified_name(type(self)), e.args[0], json.dumps(_)),
                                )
                            raise e
                else:
                    _dir = tuple(p for p in dir(_) if p[0] != '_')
                    for p in serial.meta.get(self.__class__).properties.keys():
                        if p in _dir:
                            setattr(self, getattr(_, p))

    def __setattr__(self, property_name, value):
        # type: (Object, str, Any) -> properties_.NoneType
        if property_name[0] != '_':
            try:
                property_definition = serial.meta.get(self).properties[property_name]
                try:
                    value = property_definition.unmarshal(value)
                    if isinstance(value, Generator):
                        value = tuple(value)
                except (TypeError, ValueError) as e:
                    message = '\n - %s.%s: ' % (
                        qualified_name(type(self)),
                        property_name
                    )
                    if e.args and isinstance(e.args[0], str):
                        e.args = tuple(
                            chain(
                                (message + e.args[0],),
                                e.args[1:]
                            )
                        )
                    else:
                        e.args = (message + repr(value),)
                    raise e
            except KeyError as e:
                if value is not None:
                    raise e
        super().__setattr__(property_name, value)

    def __setitem__(self, key, value):
        # type: (str, str) -> None
        m = self._meta or type(self)._meta
        if key in m.properties:
            property_name = key
        else:
            property_name = None
            for pn, pd in m.properties.items():
                if key == pd.name:
                    property_name = pn
                    break
            if property_name is None:
                raise KeyError(
                    '`%s` has no property mapped to the name "%s"' % (
                        qualified_name(type(self)),
                        key
                    )
                )
        setattr(self, property_name, value)

    def __getitem__(self, key):
        # type: (str, str) -> None
        m = self._meta or type(self)._meta
        if key in m.properties:
            property_name = key
        else:
            property_definition = None
            property_name = None
            for pn, pd in m.properties.items():
                if key == pd.name:
                    property_name = pn
                    property_definition = pd
                    break
            if property_definition is None:
                raise KeyError(
                    '`%s` has no property mapped to the name "%s"' % (
                        qualified_name(type(self)),
                        key
                    )
                )
        return getattr(self, property_name)

    def __copy__(self):
        # type: () -> Object
        return self.__class__(self)

    def __deepcopy__(self, memo=None):
        # type: (Optional[dict]) -> Object
        new_instance = self.__class__()
        if self._meta is None:
            m = type(self)._meta
        else:
            m = new_instance._meta = deepcopy(self._meta)  # type: serial.meta.Object
        if self._hooks is not None:
            new_instance._hooks = deepcopy(self._hooks)  # type: serial.hooks.Hooks
        if m is not None:
            for k in m.properties.keys():
                try:
                    v = getattr(self, k)
                    if v is not None:
                        if not isinstance(v, Callable):
                            v = deepcopy(v, memo=memo)
                            setattr(new_instance, k, v)
                except TypeError as e:
                    label = '%s.%s: ' % (qualified_name(type(self)), k)
                    if e.args:
                        e.args = tuple(
                            chain(
                                (label + e.args[0],),
                                e.args[1:]
                            )
                        )
                    else:
                        e.args = (label + serialize(self),)
                    raise e
        return new_instance

    def _marshal(self):
        o = self
        h = self._hooks or type(self)._hooks
        if (h is not None) and (h.before_marshal is not None):
            o = h.before_marshal(o)
        data = OrderedDict()
        m = self._meta or type(o)._meta
        for pn, p in m.properties.items():
            v = getattr(o, pn)
            if v is not None:
                k = p.name or pn
                data[k] = p.marshal(v)
        if (h is not None) and (h.after_marshal is not None):
            data = h.after_marshal(data)
        return data

    def __str__(self):
        return serialize(self)

    def __repr__(self):
        representation = [
            '%s(' % qualified_name(type(self))
        ]
        m = self._meta or type(self)._meta
        for p in m.properties.keys():
            v = getattr(self, p)
            if v is not None:
                rv = (
                    qualified_name(v)
                    if isinstance(v, type) else
                    repr(v)
                )
                rvls = rv.split('\n')
                if len(rvls) > 2:
                    rvs = [rvls[0]]
                    for rvl in rvls[1:]:
                        rvs.append('    ' + rvl)
                    rv = '\n'.join(rvs)
                representation.append(
                    '    %s=%s,' % (p, rv)
                )
        representation.append(')')
        if len(representation) > 2:
            return '\n'.join(representation)
        else:
            return ''.join(representation)

    def __eq__(self, other):
        # type: (Any) -> bool
        if type(self) is not type(other):
            return False
        m = self._meta or type(self)._meta
        om = other._meta or type(other)._meta
        self_properties = set(m.properties.keys())
        other_properties = set(om.properties.keys())
        for p in self_properties|other_properties:
            v = getattr(self, p)
            ov = getattr(other, p)
            if v != ov:
                return False
        return True

    def __ne__(self, other):
        # type: (Any) -> bool
        return False if self == other else True

    def __iter__(self):
        m = self._meta or type(self)._meta
        for k in m.properties.keys():
            yield k

    def _validate(self):
        o = self
        h = self._hooks or type(self)._hooks
        if (h is not None) and (h.before_validate is not None):
            o = h.before_validate(o)
        m = o._meta or type(o)._meta
        for pn, p in m.properties.items():
            v = getattr(o, pn)
            if v is None:
                if isinstance(p.required, Callable):
                    required = p.required(o)
                else:
                    required = p.required
                if required:
                    raise serial.errors.ValidationError(
                        'The property `%s` is required for `%s`.' % (pn, qualified_name(type(o)))
                    )
            else:
                if v is serial.properties.NULL:
                    types = p.types
                    if isinstance(types, collections.Callable):
                        types = types(v)
                    if types is None:
                        raise TypeError(
                            'Null values are not allowed in `%s.%s`.' % (qualified_name(type(o)), pn)
                        )
                    else:
                        if (str in types) and (native_str is not str) and (native_str not in types):
                            types = tuple(chain(*(
                                ((t, native_str) if (t is str) else (t,))
                                for t in types
                            )))
                        if serial.properties.Null not in types:
                            raise TypeError(
                                'Null values are not allowed in `%s.%s`.' % (qualified_name(type(o)), pn)
                            )
                else:
                    try:
                        validate(v, p.types)
                    except serial.errors.ValidationError as e:
                        message = '%s.%s:\n' % (qualified_name(type(o)), pn)
                        if e.args:
                            e.args = tuple(chain(
                                (e.args[0] + message,),
                                e.args[1:]
                            ))
                        else:
                            e.args = (
                                message,
                            )
        if (h is not None) and (h.after_validate is not None):
            o = h.after_validate(o)


class Array(list):

    _hooks = None  # type: Optional[serial.hooks.Array]
    _meta = None  # type: Optional[serial.meta.Array]

    def __init__(
        self,
        items=None,  # type: Optional[Union[Sequence, Set]]
        item_types=(
            None
        ),  # type: Optional[Union[Sequence[Union[type, serial.properties.Property]], type, serial.properties.Property]]
    ):
        self._hooks = None
        self._meta = None
        if isinstance(items, IOBase):
            if hasattr(items, 'url'):
                serial.meta.get(self).url = items.url
            elif hasattr(items, 'name'):
                serial.meta.get(self).path = items.name
        items = deserialize(items)
        # self._item_types = None
        if item_types is None:
            if isinstance(items, Array):
                if items._meta or (type(items) is not type(self)):
                    self._meta = deepcopy(items._meta or type(items)._meta)
        else:
            serial.meta.get(self).item_types = item_types
        super().__init__()
        if items is not None:
            for item in items:
                self.append(item)

    def __setitem__(
        self,
        index,  # type: int
        value,  # type: Any
    ):
        m = self._meta or type(self)._meta
        if m is None:
            item_types = None
        else:
            item_types = m.item_types
        super().__setitem__(index, unmarshal(value, types=item_types))

    def append(self, value):
        # type: (Any) -> None
        m = self._meta or type(self)._meta
        if m is None:
            item_types = None
        else:
            item_types = m.item_types
        super().append(unmarshal(value, types=item_types))

    def __copy__(self):
        # type: () -> Array
        return self.__class__(self)

    def __deepcopy__(self, memo=None):
        # type: (Optional[dict]) -> Array
        new_instance = self.__class__()
        if self._meta:
            new_instance._meta = deepcopy(self._meta)
        for i in self:
            new_instance.append(deepcopy(i, memo=memo))
        return new_instance

    def _marshal(self):
        a = self
        h = a._hooks or type(a)._hooks
        if (h is not None) and (h.before_marshal is not None):
            a = h.before_marshal(a)
        m = a._meta or type(a)._meta
        a = tuple(
            marshal(i, types=m.item_types) for i in a
        )
        if (h is not None) and (h.after_marshal is not None):
            a = h.after_marshal(a)
        return a

    def _validate(self):
        a = self
        h = a._hooks or type(a)._hooks
        if (h is not None) and (h.before_validate is not None):
            a = h.before_validate(a)
        m = a._meta or type(a)._meta
        if m.item_types is not None:
            for i in a:
                validate(i, m.item_types)
        if (h is not None) and (h.after_validate is not None):
            h.after_validate(a)

    def __repr__(self):
        representation = [
            qualified_name(type(self)) + '('
        ]
        if len(self) > 0:
            representation.append('    [')
            for i in self:
                ri = (
                    qualified_name(i) if isinstance(i, type) else
                    repr(i)
                )
                rils = ri.split('\n')
                if len(rils) > 1:
                    ris = [rils[0]]
                    ris += [
                        '        ' + rvl
                        for rvl in rils[1:]
                    ]
                    ri = '\n'.join(ris)
                representation.append(
                    '        %s,' % ri
                )
            representation.append(
                '    ]' + (''
                if self._meta is None or self._meta.item_types is None
                else ',')
            )
        if self._meta:
            if self._meta.item_types:
                representation.append(
                    '    item_types=(',
                )
                for it in self.item_types:
                    ri = (
                        qualified_name(it) if isinstance(it, type) else
                        repr(it)
                    )
                    rils = ri.split('\n')
                    if len(rils) > 2:
                        ris = [rils[0]]
                        ris += [
                            '        ' + rvl
                            for rvl in rils[1:-1]
                        ]
                        ris.append('        ' + rils[-1])
                        ri = '\n'.join(ris)
                    representation.append('        %s,' % ri)
                if len(self._meta.item_types) > 1:
                    representation[-1] = representation[-1][:-1]
                representation.append('    )')
        representation.append(')')
        if len(representation) > 2:
            return '\n'.join(representation)
        else:
            return ''.join(representation)

    def __eq__(self, other):
        # type: (Any) -> bool
        if type(self) is not type(other):
            return False
        length = len(self)
        if length != len(other):
            return False
        for i in range(length):
            if self[i] != other[i]:
                return False
        return True

    def __ne__(self, other):
        # type: (Any) -> bool
        if self == other:
            return False
        else:
            return True

    def __str__(self):
        return serialize(self)


class Dictionary(OrderedDict):

    _hooks = None  # type: Optional[serial.hooks.Dictionary]
    _meta = None  # type: Optional[serial.meta.Dictionary]

    def __init__(
        self,
        items=None,  # type: Optional[typing.Mapping]
        value_types=(
            None
        ),  # type: Optional[Union[Sequence[Union[type, serial.properties.Property]], type, serial.properties.Property]]
    ):
        self._hooks = None
        self._meta = None
        if isinstance(items, IOBase):
            if hasattr(items, 'url'):
                serial.meta.get(self).url = items.url
            elif hasattr(items, 'name'):
                serial.meta.get(self).path = items.name
        items = deserialize(items)
        # self._value_types = None
        if value_types is None:
            if isinstance(items, Dictionary):
                if items._meta or (type(items) is not type(self)):
                    self._meta = deepcopy(items._meta or type(items)._meta)
        else:
            serial.meta.get(self).value_types = value_types
        super().__init__()
        if items is None:
            super().__init__()
        else:
            if isinstance(items, (OrderedDict, Dictionary)):
                items = items.items()
            elif isinstance(items, dict):
                items = sorted(items.items(), key=lambda kv: kv)
            super().__init__(items)

    def __setitem__(
        self,
        key,  # type: int
        value,  # type: Any
    ):
        m = self._meta or type(self)._meta
        if m is None:
            value_types = None
        else:
            value_types = m.value_types
        try:
            super().__setitem__(
                key,
                unmarshal(value, types=value_types)
            )
        except TypeError as e:
            message = "\n - %s['%s']: " % (
                qualified_name(type(self)),
                key
            )
            if e.args and isinstance(e.args[0], str):
                e.args = tuple(
                    chain(
                        (message + e.args[0],),
                        e.args[1:]
                    )
                )
            else:
                e.args = (message + repr(value),)
            raise e

    def __copy__(self):
        # type: (Dictionary) -> Dictionary
        if self._meta is None:
            value_types = None
        else:
            value_types = self._meta.value_types
        return self.__class__(
            self,
            value_types=value_types
        )

    def __deepcopy__(self, memo=None):
        # type: (dict) -> Dictionary
        if self._meta is None:
            value_types = None
        else:
            value_types = deepcopy(self._meta.value_types)
        return self.__class__(
            [
                (
                    k,
                    deepcopy(v, memo=memo)
                ) for k, v in self.items()
            ],
            value_types=value_types
        )

    def _marshal(self):
        d = self
        h = d._hooks or type(d)._hooks
        if (h is not None) and (h.before_marshal is not None):
            d = h.before_marshal(d)
        m = d._meta or type(d)._meta
        if m is None:
            value_types = None
        else:
            value_types = m.value_types
        d = OrderedDict(
            [
                (
                    k,
                    marshal(v, types=value_types)
                ) for k, v in d.items()
            ]
        )
        if (h is not None) and (h.after_marshal is not None):
            d = h.after_marshal(d)
        return d

    def _validate(self):
        d = self
        h = d._hooks or type(d)._hooks
        if (h is not None) and (h.before_validate is not None):
            d = h.before_validate(d)
        m = d._meta or type(d)._meta
        if m is None:
            value_types = None
        else:
            value_types = m.value_types
        if value_types is not None:
            for k, v in d.items():
                validate(v, value_types)
        if (h is not None) and (h.after_validate is not None):
            h.after_validate(d)

    def __repr__(self):
        representation = [
            qualified_name(type(self)) + '('
        ]
        items = tuple(self.items())
        if len(items) > 0:
            representation.append('    [')
            for k, v in items:
                rv = (
                    qualified_name(v) if isinstance(v, type) else
                    repr(v)
                )
                rvls = rv.split('\n')
                if len(rvls) > 1:
                    rvs = [rvls[0]]
                    for rvl in rvls[1:]:
                        rvs.append('            ' + rvl)
                    # rvs.append('            ' + rvs[-1])
                    rv = '\n'.join(rvs)
                    representation += [
                        '        (',
                        '            %s,' % repr(k),
                        '            %s' % rv,
                        '        ),'
                    ]
                else:
                    representation.append(
                        '        (%s, %s),' % (repr(k), rv)
                    )
            representation[-1] = representation[-1][:-1]
            representation.append(
                '    ]'
                if self._meta is None or self._meta.value_types is None else
                '    ],'
            )
        if self._meta:
            if self._meta.value_types:
                representation.append(
                    '    value_types=(',
                )
                for vt in self._meta.value_types:
                    rv = (
                        qualified_name(vt) if isinstance(vt, type) else
                        repr(vt)
                    )
                    rvls = rv.split('\n')
                    if len(rvls) > 1:
                        rvs = [rvls[0]]
                        rvs += [
                            '        ' + rvl
                            for rvl in rvls[1:]
                        ]
                        rv = '\n'.join(rvs)
                    representation.append('        %s,' % rv)
                if len(self._meta.value_types) > 1:
                    representation[-1] = representation[-1][:-1]
                representation.append('    )')
        representation.append(')')
        if len(representation) > 2:
            return '\n'.join(representation)
        else:
            return ''.join(representation)

    def __eq__(self, other):
        # type: (Any) -> bool
        if type(self) is not type(other):
            return False
        keys = tuple(self.keys())
        other_keys = tuple(other.keys())
        if keys != other_keys:
            return False
        for k in keys:
            if self[k] != other[k]:
                return False
        return True

    def __ne__(self, other):
        # type: (Any) -> bool
        if self == other:
            return False
        else:
            return True

    def __str__(self):
        return serialize(self)