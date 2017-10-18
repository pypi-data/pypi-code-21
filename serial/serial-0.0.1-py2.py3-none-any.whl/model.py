from __future__ import nested_scopes, generators, division, absolute_import, with_statement, print_function,\
    unicode_literals

from future import standard_library
standard_library.install_aliases()
from builtins import *

import collections
import json
from base64 import b64encode
from collections import OrderedDict, Callable, Set, Sequence
from copy import deepcopy, copy
from http.client import HTTPResponse
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
    if isinstance(data, (bytes, bytearray)):
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
    matched = False
    for t in types:
        if isinstance(
            t,
            serial.properties.Property
        ):
            try:
                data = t.unmarshal(data)
                matched = True
                break
            except (AttributeError, KeyError, TypeError, ValueError):
                continue
        elif isinstance(t, type):
            if issubclass(t, Object) and isinstance(data, (dict, OrderedDict)):
                try:
                    data = t(data)
                    matched = True
                    break
                except (AttributeError, KeyError, TypeError, ValueError):
                    pass
            elif isinstance(data, (dict, OrderedDict)) and issubclass(t, (dict, OrderedDict, Dictionary)):
                data = Dictionary(data, value_types=value_types)
                matched = True
                break
            elif (
                isinstance(data, (Set, Sequence, Generator)) and
                (not isinstance(data, (str, bytes))) and
                issubclass(t, (Set, Sequence)) and
                (not issubclass(t, (str, bytes))) # Array
            ):
                data = Array(data, item_types=item_types)
                matched = True
                break
            elif isinstance(data, t):
                matched = True
                break
    if not matched:
        if not matched:
            raise TypeError(
                '\n   The data provided does not fit any of the types indicated:\n' +
                '     - data: %s(%s)\n' % (type(data).__name__, serialize(data)) +
                '     - types: %s' % repr(types)
            )
    return data


def serialize(data, data_format='json'):
    # type: (Any, str) -> str
    """
    Serializes instances of ``serial.model.Object`` as JSON or YAML.
    """
    if data_format not in ('json', 'yaml'):
        data_format = data_format.lower()
        if data_format not in ('json', 'yaml'):
            raise ValueError(
                'Supported `serial.model.serialize()` `format_` values include "json" and "yaml" (not "%s").' % data_format
            )
    if data_format == 'json':
        return json.dumps(marshal(data))
    elif data_format == 'yaml':
        return yaml.dump(marshal(data))


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
        except json.JSONDecodeError as e:
            data = yaml.load(data)
    return data


def validate(data, types=None):
    # type: (Union[Object, Array, Dictionary], Optional[Union[type, serial.properties.Property, Object]]) -> None
    if types is not None:
        if isinstance(types, collections.Callable):
            types = types(data)
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
                '%s is invalid. Data must be one of the following types: %s.' % (
                    repr(data),
                    repr(types)
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
        m = serial.meta.get(data)
        for n, p in tuple(m.properties.items()):
            if p.versions is not None:
                version_match = False
                specification_match = False
                for v in p.versions:
                    if v.specification == specification:
                        specification_match = True
                        if v == version_number:
                            version_match = True
                            if v.types is not None:
                                m.properties[n].types = v.types
                            break
                if specification_match and (not version_match):
                    del m.properties[n]
        for n, p in m.properties.items():
            version(getattr(data, n), specification, version_number)
    elif isinstance(data, (collections.Set, collections.Sequence)) and not isinstance(data, (str, bytes)):
        for d in data:
            version(d, specification, version_number)
    elif isinstance(data, (dict, OrderedDict)):
        for k, v in data.items():
            version(v, specification, version_number)


class Object(object):

    _meta = None  # type: Optional[serial.meta.Meta]

    def __init__(
        self,
        _=None,  # type: Optional[Union[AnyStr, typing.Mapping, typing.Sequence, typing.IO]]
    ):
        self._meta = None
        if _ is not None:
            if isinstance(_, Object):
                m = serial.meta.get(_)
                self._meta = deepcopy(m)
                self._meta.data = self
                for k in m.properties.keys():
                    try:
                        setattr(self, k, getattr(_, k))
                    except TypeError as e:
                        t = type(self)
                        label = '\n - %s.%s.%s: ' % (t.__module__, t.__name__, k)
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
                if isinstance(_, HTTPResponse):
                    serial.meta.get(self).url = _.url
                _ = deserialize(_)
                if isinstance(_, dict):
                    for k, v in _.items():
                        try:
                            self[k] = v
                        except KeyError as e:
                            if e.args and len(e.args) == 1:
                                t = type(self)
                                e.args = (
                                    r'%s.%s.%s: %s' % (t.__module__, t.__name__, e.args[0], json.dumps(_)),
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
            property_definition = serial.meta.get(self).properties[property_name]
            try:
                value = property_definition.unmarshal(value)
                if isinstance(value, Generator):
                    value = tuple(value)
            except (TypeError, ValueError) as e:
                t = type(self)
                message = '\n - %s%s.%s: ' % (
                    (
                        ''
                        if t.__module__ in ('__main__', '__builtin__', 'builtins')
                        else t.__module__ + '.'
                    ),
                    t.__name__,
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
        super().__setattr__(property_name, value)

    def __setitem__(self, key, value):
        # type: (str, str) -> None
        try:
            property_definition = serial.meta.get(self).properties[key]
            property_name = key
        except KeyError:
            property_definition = None
            property_name = None
            for pn, pd in serial.meta.get(self).properties.items():
                if key == pd.name:
                    property_name = pn
                    property_definition = pd
                    break
            if property_name is None:
                t = type(self)
                raise KeyError(
                    '`%s` has no property mapped to the name "%s"' % (
                        '%s.%s' % (t.__module__, t.__name__),
                        key
                    )
                )
        if (
            (value is None) and
            property_definition.required and
            (
                serial.properties.NoneType not in (
                    property_definition.types(value)
                    if isinstance(property_definition.types, collections.Callable)
                    else property_definition.types
                )
            )
        ):
            t = type(self)
            raise serial.errors.ValidationError(
                'The property `%s` is required for `serial.model.%s.%s`.' % (
                    property_name,
                    '%s.%s' % (t.__module__, t.__name__)
                )
            )
        setattr(self, property_name, value)
        return None

    def __getitem__(self, key):
        # type: (str, str) -> None
        m = serial.meta.get(self)
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
                t = type(self)
                raise KeyError(
                    '`%s.%s` has no property mapped to the name "%s"' % (
                        t.__module__,
                        t.__name__,
                        key
                    )
                )
        return getattr(self, property_name)

    def __copy__(self):
        # type: () -> Object
        m = serial.meta.get(self)
        return self.__class__(self)
        new_instance._meta = deepcopy(m)
        new_instance._meta.data = new_instance
        for k in m.properties.keys():
            try:
                setattr(new_instance, k, getattr(self, k))
            except TypeError as e:
                t = type(self)
                label = '\n - %s.%s.%s: ' % (t.__module__, t.__name__, k)
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

    def __deepcopy__(self, memo=None):
        # type: (Optional[dict]) -> Object
        m = serial.meta.get(self)
        new_instance = self.__class__()
        new_instance._meta = deepcopy(m)  # type: serial.meta.Meta
        new_instance._meta.data = new_instance  # type: Object
        for k in m.properties.keys():
            try:
                v = getattr(self, k)
                if v is not None:
                    if not isinstance(v, Callable):
                        v = deepcopy(v, memo=memo)
                        setattr(new_instance, k, v)
            except TypeError as e:
                t = type(self)
                label = '%s.%s.%s: ' % (t.__module__, t.__name__, k)
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
        data = OrderedDict()
        for pn, p in serial.meta.get(self).properties.items():
            v = getattr(self, pn)
            if v is None:
                if p.required:
                    t = type(self)
                    raise serial.errors.ValidationError(
                        'The property `%s` is required for `%s.%s`.' % (pn, t.__module__, t.__name__)
                    )
            else:
                k = p.name or pn
                if v is serial.properties.NULL:
                    types = p.types
                    if isinstance(types, collections.Callable):
                        types = types(v)
                    if serial.properties.Null not in types:
                        t = type(self)
                        raise TypeError(
                            'Null values are not allowed in `%s.%s.%s`.' % (t.__module__, t.__name__, pn)
                        )
                data[k] = p.marshal(v)
        return data

    def __str__(self):
        return serialize(self)

    def __repr__(self):
        t = type(self)
        representation = [
            t.__name__ + '('
            if t.__module__ in ('__main__', '__builtin__', 'builtins') else
            '%s.%s(' % (t.__module__, t.__name__)
        ]
        for p in serial.meta.get(self).properties.keys():
            v = getattr(self, p)
            if v is not None:
                rv = (
                    '%s.%s' % (v.__module__, v.__name__)
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
        self_properties = set(serial.meta.get(self).properties.keys())
        other_properties = set(serial.meta.get(other).properties.keys())
        for p in self_properties|other_properties:
            if getattr(self, p) != getattr(other, p):
                return False
        return True

    def __ne__(self, other):
        # type: (Any) -> bool
        return False if self == other else True

    def __iter__(self):
        for k in serial.meta.get(self).properties.keys():
            yield k

    def _validate(self):
        for pn, p in serial.meta.get(self).properties.items():
            v = getattr(self, pn)
            if v is None:
                if p.required:
                    t = type(self)
                    raise serial.errors.ValidationError(
                        'The property `%s` is required for `%s.%s`.' % (pn, t.__module__, t.__name__)
                    )
            else:
                if v is serial.properties.NULL:
                    types = p.types
                    if isinstance(types, collections.Callable):
                        types = types(v)
                    if serial.properties.Null not in types:
                        t = type(self)
                        raise TypeError(
                            'Null values are not allowed in `%s.%s.%s`.' % (t.__module__, t.__name__, pn)
                        )
                else:
                    validate(v, p.types)


class Array(list):

    def __init__(
        self,
        items=None,  # type: Optional[Union[Sequence, Set]]
        item_types=(
            None
        ),  # type: Optional[Union[Sequence[Union[type, serial.properties.Property]], type, serial.properties.Property]]
    ):
        items = deserialize(items)
        if item_types is None:
            if isinstance(items, Array):
                item_types = deepcopy(items.item_types)
        else:
            if isinstance(item_types, (type, serial.properties.Property)):
                item_types = (item_types,)
            else:
                item_types = tuple(item_types)
        self.item_types = item_types
        for item in items:
            self.append(item)

    def __setitem__(
        self,
        index,  # type: int
        value,  # type: Any
    ):
        super().__setitem__(index, unmarshal(value, types=self.item_types))

    def append(self, value):
        # type: (Any) -> None
        super().append(unmarshal(value, types=self.item_types))

    def __copy__(self):
        # type: () -> Array
        return self.__class__(self)

    def __deepcopy__(self, memo=None):
        # type: (Optional[dict]) -> Array
        return self.__class__(
            tuple(deepcopy(i, memo=memo) for i in self),
            item_types=self.item_types
        )

    def _marshal(self):
        return tuple(
            marshal(i, types=self.item_types) for i in self
        )

    def _validate(self):
        if self.item_types is not None:
            for i in self:
                validate(i, self.item_types)

    def __repr__(self):
        t = type(self)
        representation = [
            t.__name__ + '('
            if t.__module__ in ('__main__', '__builtin__', 'builtins') else
            '%s.%s(' % (t.__module__, t.__name__)
        ]
        if len(self) > 0:
            representation.append('    [')
            for i in self:
                ri = (
                    (
                        i.__name__
                        if i.__module__ in ('__main__', '__builtin__', 'builtins') else
                        '%s.%s' % (i.__module__, i.__name__)
                    ) if isinstance(i, type) else
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
            representation.append('    ]' + ('' if self.item_types is None else ','))
        if self.item_types is not None:
            representation.append(
                '    item_types=(',
            )
            for it in self.item_types:
                ri = (
                    (
                        it.__name__
                        if it.__module__ in ('__main__', '__builtin__', 'builtins') else
                        '%s.%s' % (it.__module__, it.__name__)
                    ) if isinstance(it, type) else
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
            if len(self.item_types) > 1:
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

    def __init__(
        self,
        items=None,  # type: Optional[typing.Mapping]
        value_types=(
            None
        ),  # type: Optional[Union[Sequence[Union[type, serial.properties.Property]], type, serial.properties.Property]]
    ):
        items = deserialize(items)
        if isinstance(value_types, (type, serial.properties.Property)):
            value_types = (value_types,)
        elif value_types is not None:
            if isinstance(value_types, collections.Iterable):
                if not isinstance(value_types, (collections.Sequence, collections.Set)):
                    value_types = list(value_types)
                for vt in value_types:
                    if not isinstance(vt, (type, serial.properties.Property)):
                        raise TypeError(value_types)
            else:
                raise TypeError(value_types)
        self.value_types = value_types
        if items is None:
            super().__init__()
        else:
            if isinstance(items, (OrderedDict, Dictionary)):
                items = items.items()
                # if sys.version_info[0] < 3:
                    # TODO: Find *proper* fix for `OrderedDict` sorting problems in Python 2x
                # items = sorted(items)
            elif isinstance(items, dict):
                items = sorted(items.items(), key=lambda kv: kv)
            super().__init__(items)

    def __setitem__(
        self,
        key,  # type: int
        value,  # type: Any
    ):
        try:
            super().__setitem__(
                key,
                unmarshal(value, types=self.value_types)
            )
        except TypeError as e:
            t = type(self)
            message = "\n - %s.%s['%s']: " % (
                t.__module__,
                t.__name__,
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
        return self.__class__(
            self,
            value_types=self.value_types
        )

    def __deepcopy__(self, memo=None):
        # type: (dict) -> Dictionary
        return self.__class__(
            [
                (
                    k,
                    deepcopy(v, memo=memo)
                ) for k, v in self.items()
            ],
            value_types=self.value_types
        )

    def _marshal(self):
        return OrderedDict(
            [
                (
                    k,
                    marshal(v, types=self.value_types)
                ) for k, v in self.items()
            ]
        )

    def _validate(self):
        if self.value_types is not None:
            for k, v in self.items():
                validate(v, self.value_types)

    def __repr__(self):
        t = type(self)
        representation = [
            t.__name__ + '('
            if t.__module__ in ('__main__', '__builtin__', 'builtins') else
            '%s.%s(' % (t.__module__, t.__name__)
        ]
        items = tuple(self.items())
        if len(items) > 0:
            representation.append('    [')
            for k, v in items:
                rv = (
                    (
                        v.__name__
                        if v.__module__ in ('__main__', '__builtin__', 'builtins') else
                        '%s.%s' % (v.__module__, v.__name__)
                    ) if isinstance(v, type) else
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
                if self.value_types is None else
                '    ],'
            )
        if self.value_types is not None:
            representation.append(
                '    value_types=(',
            )
            for vt in self.value_types:
                rv = (
                    (
                        vt.__name__
                        if vt.__module__ in ('__main__', '__builtin__', 'builtins') else
                        '%s.%s' % (vt.__module__, vt.__name__)
                    ) if isinstance(vt, type) else
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
            if len(self.value_types) > 1:
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