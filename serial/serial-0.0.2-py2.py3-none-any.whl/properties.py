from __future__ import nested_scopes, generators, division, absolute_import, with_statement, print_function,\
    unicode_literals
from future import standard_library
standard_library.install_aliases()
from builtins import *
from future.utils import native_str

from base64 import b64decode, b64encode
from collections import Mapping, Sequence, Set, Iterable, Callable
from copy import copy, deepcopy
from datetime import date, datetime
from numbers import Real

import iso8601

from serial import meta, model

try:
    import typing
except ImportError:
    typing = None

NoneType = type(None)


class Null(object):
    """
    Instances of this class represent an *explicit* null value, rather than the absence of a
    property/attribute/element, as is inferred from a value of ``None``.
    """

    def __bool__(self):
        return False

    def __eq__(self, other):
        return True if (other is None) or isinstance(other, self.__class__) else False

    def __hash__(self):
        return 0

    def __str__(self):
        return 'null'

    def _marshal(self):
        return None

    def __repr__(self):
        t = type(self)
        if t.__module__ in ('__main__', '__builtin__', 'builtins'):
            return '%s()' % t.__name__
        else:
            return '%s.%s()' % (t.__module__, t.__name__)


NULL = Null()


class Property(object):
    """
    This is the base class for defining a property.

    Properties

        - value_types ([type|Property]): One or more expected value_types or `Property` instances. Values are checked,
          sequentially, against each type or ``Property`` instance, and the first appropriate match is used.

        - required (bool): If ``True``--dumping the json_object will throw an error if this value is ``None``.

        - versions ([str]|{str:Property}): The property should be one of the following:

            - A set/tuple/list of version numbers to which this property applies.
            - A mapping of version numbers to an instance of `Property` applicable to that version.

          Version numbers prefixed by "<" indicate any version less than the one specified, so "<3.0" indicates that
          this property is available in versions prior to 3.0. The inverse is true for version numbers prefixed by ">".
          ">=" and "<=" have similar meanings, but are inclusive.

          Versioning can be applied to an json_object by calling ``serial.model.set_version`` in the ``__init__`` method of
          an ``serial.model.Object`` sub-class. For an example, see ``serial.model.OpenAPI.__init__``.

        - name (str): The name of the property when loaded from or dumped into a JSON/YAML/XML json_object. Specifying a
          ``name`` facilitates mapping of PEP8 compliant property to JSON or YAML attribute names, or XML element names,
          which are either camelCased, are python keywords, or otherwise not appropriate for usage in python code.

    (XML Only)

        - attribute (bool): Should this property be interpreted as an attribute (as opposed to a child element) when
          dumped as XML.

        - prefix (str): The XML prefix.

        - name_space (str): The URI of an XML name space.

    """

    def __init__(
        self,
        types=None,  # type: typing.Sequence[Union[type, Property]]
        name=None,  # type: Optional[str]
        required=False,  # type: bool
        versions=None,  # type: Optional[Sequence[Union[str, Version]]]
        name_space=None,  # type: Optional[str]
        prefix=None,  # type: Optional[str]
        attribute=False,  # type: bool
    ):
        if isinstance(types, (type, Property)):
            types = (types,)
        else:
            types = deepcopy(types)
        self.types = types  # type: Optional[Sequence[type]]
        self.name = name
        self.required = required
        self._versions = None  # type: Optional[Union[Mapping[str, Optional[Property]], Set[Union[str, Number]]]]
        self.versions = versions  # type: Optional[Union[Mapping[str, Optional[Property]], Set[Union[str, Number]]]]
        self.name_space = name_space  # type: Optional[str]
        self.prefix = prefix  # type: Optional[str]
        self.attribute = attribute  # type: Optional[str]

    @property
    def versions(self):
        # type: () -> Optional[Sequence[Version]]
        return self._versions

    @versions.setter
    def versions(
        self,
        versions  # type: Optional[Sequence[Union[str, Version]]]
    ):
        # type: (...) -> Optional[Union[Mapping[str, Optional[Property]], Set[Union[str, Number]]]]
        if versions is not None:
            if isinstance(versions, (str, Number, meta.Version)):
                versions = (versions,)
            if isinstance(versions, Iterable):
                versions = tuple(
                    (v if isinstance(v, meta.Version) else meta.Version(v))
                    for v in versions
                )
            else:
                raise TypeError(
                    '``Property.versions`` requires a sequence of version strings or ' +
                    '``serial.properties.metadata.Version`` instances, not ' +
                    '``%s``.' % type(versions).__name__
                )
        self._versions = versions

    def unmarshal(self, data):
        # type: (typing.Any) -> typing.Any
        # return data if self.types is None else unmarshal(data, types=self.types)
        return model.unmarshal(data, types=self.types)

    def marshal(self, data):
        # type: (typing.Any) -> typing.Any
        return model.marshal(data)  #, types=self.types, value_types=self.value_types)

    def __repr__(self):
        t = type(self)
        representation = ['%s.%s(' % (t.__module__, t.__name__)]
        for p in dir(self):
            if p[0] != '_':
                v = getattr(self, p)
                if (v is not None) and not isinstance(v, Callable):
                    if isinstance(v, Sequence) and not isinstance(v, (str, bytes)):
                        rvs = ['(']
                        for i in v:
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
                                for ril in rils[1:]:
                                    ris.append('        ' + ril)
                                ri = '\n'.join(ris)
                            rvs.append('        %s,' % ri)
                        if len(v) > 1:
                            rvs[-1] = rvs[-1][:-1]
                        rvs.append('    )')
                        rv = '\n'.join(rvs)
                    else:
                        rv = (
                            (
                                v.__name__
                                if v.__module__ in ('__main__', '__builtin__', 'builtins') else
                                '%s.%s' % (v.__module__, v.__name__)
                            ) if isinstance(v, type) else
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

    def __copy__(self):
        new_instance = self.__class__()
        for a in dir(self):
            if a[0] != '_' and a != 'data':
                v = getattr(self, a)
                if not isinstance(v, Callable):
                    setattr(new_instance, a, v)
        return new_instance

    def __deepcopy__(self, memo=None):
        # type: (dict) -> Memo
        new_instance = self.__class__()
        for a in dir(self):
            if a[0] != '_':
                v = getattr(self, a)
                if not isinstance(v, Callable):
                    setattr(new_instance, a, deepcopy(v, memo=memo))
        return new_instance


class String(Property):
    """
    See ``serial.model.Property`` for details.

    Properties:

        - name (str)
        - required (bool)
        - versions ([str]|{str:Property})
    """

    def __init__(
        self,
        name=None,  # type: Optional[str]
        required=False,  # type: bool
        versions=None,  # type: Optional[typing.Collection]
        name_space=None,  # type: Optional[str]
        prefix=None,  # type: Optional[str]
        attribute=False,  # type: bool
    ):
        super().__init__(
            types=(str,),
            name=name,
            required=required,
            versions=versions,
            attribute=attribute,
            name_space=name_space,
            prefix=prefix,
        )


class Date(Property):
    """
    See ``serial.model.Property``

    Additional Properties:

        - marshal (collections.Callable): A function, taking one argument (a python ``date`` json_object), and returning
          a date string in the desired format. The default is ``date.isoformat``--returning an iso8601 compliant date
          string.

        - unmarshal (collections.Callable): A function, taking one argument (a date string), and returning a python
          ``date`` json_object. By default, this is ``iso8601.parse_date``.
    """

    def __init__(
        self,
        name=None,  # type: Optional[str]
        required=False,  # type: bool
        versions=None,  # type: Optional[typing.Collection]
        name_space=None,  # type: Optional[str]
        prefix=None,  # type: Optional[str]
        attribute=False,  # type: bool
        date2str=date.isoformat,  # type: Optional[Callable]
        str2date=iso8601.parse_date  # type: Callable
    ):
        super().__init__(
            types=(date,),
            name=name,
            required=required,
            versions=versions,
            attribute=attribute,
            name_space=name_space,
            prefix=prefix,
        )
        self.date2str = date2str
        self.str2date = str2date

    def unmarshal(self, data):
        # type: (Optional[str]) -> Union[date, NoneType]
        if (data is None) and (not self.required):
            return data
        else:
            d = data if isinstance(data, date) else self.str2date(data)
            if isinstance(d, date):
                return d
            else:
                raise TypeError(
                    '"%s" is not a properly formatted date string.' % data
                )

    def marshal(self, data):
        # type: (Optional[date]) -> Optional[str]
        if (data is None) and (not self.required):
            return data
        else:
            ds = self.date2str(data)
            if not isinstance(ds, str):
                if isinstance(ds, native_str):
                    ds = str(ds)
                else:
                    raise TypeError(
                        'The date2str function should return a ``str``, not a ``%s``: %s' % (
                            type(ds).__name__,
                            repr(ds)
                        )
                    )
        return ds


class DateTime(Property):
    """
    See ``serial.model.Property``

    Additional Properties:

        - marshal (collections.Callable): A function, taking one argument (a python ``datetime`` json_object), and returning
          a date-time string in the desired format. The default is ``datetime.isoformat``--returning an iso8601 compliant
          date-time string.

        - unmarshal (collections.Callable): A function, taking one argument (a datetime string), and returning a python
          ``datetime`` json_object. By default, this is ``iso8601.parse_date``.
    """

    def __init__(
        self,
        name=None,  # type: Optional[str]
        required=False,  # type: bool
        versions=None,  # type: Optional[typing.Collection]
        name_space=None,  # type: Optional[str]
        prefix=None,  # type: Optional[str]
        attribute=False,  # type: bool
        datetime2str=datetime.isoformat,  # type: Optional[Callable]
        str2datetime=iso8601.parse_date  # type: Callable
    ):
        self.datetime2str = datetime2str
        self.str2datetime = str2datetime
        super().__init__(
            types=(datetime,),
            name=name,
            required=required,
            versions=versions,
            attribute=attribute,
            name_space=name_space,
            prefix=prefix,
        )

    def unmarshal(self, data):
        # type: (Optional[str]) -> Union[datetime, NoneType]
        if (data is None) and (not self.required):
            return data
        else:
            dt = data if isinstance(data, datetime) else self.str2datetime(data)
            if isinstance(dt, datetime):
                return dt
            else:
                raise TypeError(
                    '"%s" is not a properly formatted date-time string.' % data
                )

    def marshal(self, data):
        # type: (Optional[datetime]) -> Optional[str]
        if (data is None) and (not self.required):
            return data
        else:
            dts = self.datetime2str(data)
            if not isinstance(dts, str):
                if isinstance(dts, native_str):
                    dts = str(dts)
                else:
                    raise TypeError(
                        'The datetime2str function should return a ``str``, not a ``%s``: %s' % (
                            type(dts).__name__,
                            repr(dts)
                        )
                    )
            return dts


class Bytes(Property):
    """
    See ``serial.model.Property`` for details.

    Properties:

        - name (str)
        - required (bool)
        - versions ([str]|{str:Property})
    """

    def __init__(
        self,
        name=None,  # type: Optional[str]
        required=False,  # type: bool
        versions=None,  # type: Optional[typing.Collection]
        name_space=None,  # type: Optional[str]
        prefix=None,  # type: Optional[str]
        attribute=False,  # type: bool
    ):
        super().__init__(
            types=(bytes, bytearray),
            name=name,
            required=required,
            versions=versions,
            name_space=name_space,
            prefix=prefix,
            attribute=attribute
        )

    def unmarshal(self, data):
        # type: (str) -> bytes
        return data if data is None else b64decode(data) if isinstance(data, str) else data

    def marshal(self, data):
        # type: (bytes) -> str
        return data if data is None or isinstance(data, str) else str(b64encode(data), 'ascii')


class Enum(Property):
    """
    See ``serial.model.Property`` for additional details.

    Properties:

        - value_types ([type|Property])

        - values ([Any]):  A list of possible values. If ``value_types`` are specified--typing is applied prior to
          validation.

        - name (str)

        - required (bool)

        - versions ([str]|{str:Property})
    """

    def __init__(
        self,
        types=None,  # type: Optional[Sequence[Union[type, Property]]]
        values=None,  # type: Optional[Union[typing.Sequence, typing.Set]]
        name=None,  # type: Optional[str]
        required=False,  # type: bool
        versions=None,  # type: Optional[typing.Collection]
        name_space=None,  # type: Optional[str]
        prefix=None,  # type: Optional[str]
        attribute=False,  # type: bool
    ):
        super().__init__(
            types=types,
            name=name,
            required=required,
            versions=versions,
            name_space=name_space,
            prefix=prefix,
            attribute=attribute
        )
        self._values = None
        self.values = values  # type: Optional[typing.Sequence]

    @property
    def values(self):
        # type: () -> Optional[Tuple]
        return self._values

    @values.setter
    def values(self, values):
        # type: (Iterable) -> None
        if (values is not None) and (not isinstance(values, (Sequence, Set))):
            t = type(values)
            raise TypeError(
                '`values` must be a finite set or sequence, not `%s.%s`.' % (
                    t.__module__,
                    t.__name__
                )
            )
        if values is not None:
            tuple(model.unmarshal(v, types=self.types) for v in values)
        self._values = values

    def unmarshal(self, data):
        # type: (typing.Any) -> typing.Any
        if self.types is not None:
            data = model.unmarshal(data, types=self.types)
        if (
            ((self.values is not None) and (data not in self.values))
            and not ((data is None) and (not self.required))
        ):
            raise ValueError(
                'The value provided is not a valid option:\n%s\n\n' % repr(data) +
                'Valid options include:\n%s' % (
                    ','.join(repr(t) for t in self.values)
                )
            )
        return data


class Number(Property):
    """
    See ``serial.model.Property`` for details.

    Properties:

        - name (str)
        - required (bool)
        - versions ([str]|{str:Property})
    """

    def __init__(
        self,
        name=None,  # type: Optional[str]
        required=False,  # type: bool
        versions=None,  # type: Optional[typing.Collection]
        name_space=None,  # type: Optional[str]
        prefix=None,  # type: Optional[str]
        attribute=False,  # type: bool
    ):
        # type: (...) -> None
        super().__init__(
            types=(Real,),
            name=name,
            required=required,
            versions=versions,
            name_space=name_space,
            prefix=prefix,
            attribute=attribute
        )


class Integer(Property):
    """
    See ``serial.model.Property`` for details.

    Properties:

        - name (str)
        - required (bool)
        - versions ([str]|{str:Property})
    """

    def __init__(
        self,
        name=None,  # type: Optional[str]
        required=False,  # type: bool
        versions=None,  # type: Optional[typing.Collection]
        name_space=None,  # type: Optional[str]
        prefix=None,  # type: Optional[str]
        attribute=False,  # type: bool
    ):
        super().__init__(
            types=(int,),
            name=name,
            required=required,
            versions=versions,
            name_space=name_space,
            prefix=prefix,
            attribute=attribute
        )

    def unmarshal(self, data):
        # type: (typing.Any) -> typing.Any
        if (data is None) and (not self.required):
            return data
        else:
            return int(data)

    def marshal(self, data):
        # type: (typing.Any) -> typing.Any
        if (data is None) and (not self.required):
            return data
        else:
            return int(data)


class Boolean(Property):
    """
    See ``serial.model.Property`` for details.

    Properties:

        - name (str)
        - required (bool)
        - versions ([str]|{str:Property})
    """

    def __init__(
        self,
        name=None,  # type: Optional[str]
        required=False,  # type: bool
        versions=None,  # type: Optional[typing.Collection]
        name_space=None,  # type: Optional[str]
        prefix=None,  # type: Optional[str]
        attribute=False,  # type: bool
    ):
        # type: (...) -> None
        super().__init__(
            types=(bool,),
            name=name,
            required=required,
            versions=versions,
            name_space=name_space,
            prefix=prefix,
            attribute=attribute
        )

    def unmarshal(self, data):
        # type: (typing.Any) -> typing.Any
        return data if data is None or data is NULL else bool(data)

    def marshal(self, data):
        # type: (typing.Any) -> typing.Any
        return data if data is None or data is NULL else bool(data)


class Array(Property):
    """
    See ``serial.model.Property`` for details.

    Properties:

        - item_types (type|Property|[type|Property]): The type(s) of values/objects contained in the array. Similar to
          ``serial.model.Property().value_types``, but applied to items in the array, not the array itself.

        - name (str)

        - required (bool)

        - versions ([str]|{str:Property})
    """

    def __init__(
        self,
        item_types=None,  # type: Optional[Union[type, typing.Sequence[Union[type, Property]]]]
        name=None,  # type: Optional[str]
        required=False,  # type: bool
        versions=None,  # type: Optional[typing.Collection]
        name_space=None,  # type: Optional[str]
        prefix=None,  # type: Optional[str]
    ):
        if isinstance(item_types, (type, Property)):
            item_types = (item_types,)
        self.item_types = item_types  # type: Optional[typing.Sequence[Union[type, Property]]]
        super().__init__(
            types=(model.Array,),
            name=name,
            required=required,
            versions=versions,
            name_space=name_space,
            prefix=prefix,
            attribute=False
        )

    def unmarshal(self, data):
        # type: (typing.Any) -> typing.Any
        return model.unmarshal(data, item_types=self.item_types)


class Object(Property):

    pass


class Dictionary(Property):
    """
    See ``serial.model.Property``

    + Properties:

        - value_types (type|Property|[type|Property]): The type(s) of values/objects comprising the mapped
          values. Similar to ``serial.model.Property().value_types``, but applies to *values* in the dictionary
          json_object, not the json_object itself.
    """

    def __init__(
        self,
        value_types=None,  # type: Optional[Union[type, Sequence[Union[type, Property]]]]
        name=None,  # type: Optional[str]
        required=False,  # type: bool
        versions=None,  # type: Optional[Collection]
        name_space=None,  # type: Optional[str]
        prefix=None,  # type: Optional[str]
    ):
        # type: (...) -> None
        if value_types is not None:
            if isinstance(value_types, (type, Property)):
                value_types = (value_types,)
        self.value_types = value_types
        super().__init__(
            types=(model.Dictionary,),
            name=name,
            required=required,
            versions=versions,
            name_space=name_space,
            prefix=prefix,
            attribute=False
        )

    def unmarshal(self, data):
        # type: (typing.Any) -> typing.Any
        return model.unmarshal(data, types=self.types, value_types=self.value_types)