from __future__ import nested_scopes, generators, division, absolute_import, with_statement, print_function,\
    unicode_literals
from future import standard_library
standard_library.install_aliases()
from builtins import *

import operator
import re
from collections import Callable, OrderedDict
from copy import copy, deepcopy
from itertools import chain
from numbers import Number

try:
    import typing
    from typing import Optional
except ImportError:
    typing = Optional = None

import serial


UNDEFINED = object()


_DOT_SYNTAX_RE = re.compile(
    r'^\d+(\.\d+)*$'
)


class Version(object):

    def __init__(
        self,
        _=None,  # type: Optional[str]
        specification=None,  # type: Optional[Sequence[str]]
        equals=None,  # type: Optional[Sequence[Union[str, Number]]]
        not_equals=None,  # type: Optional[Sequence[Union[str, Number]]]
        less_than=None,  # type: Optional[Sequence[Union[str, Number]]]
        less_than_or_equal_to=None,  # type: Optional[Sequence[Union[str, Number]]]
        greater_than=None,  # type: Optional[Sequence[Union[str, Number]]]
        greater_than_or_equal_to=None,  # type: Optional[Sequence[Union[str, Number]]]
        types=None,  # type: typing.Sequence[Union[type, Property]]
    ):
        if isinstance(_, str) and (
            (specification is None) and
            (equals is None) and
            (not_equals is None) and
            (less_than is None) and
            (less_than_or_equal_to is None) and
            (greater_than is None) and
            (greater_than_or_equal_to is None)
        ):
            specification = None
            for s in _.split('&'):
                if '==' in s:
                    s, equals = s.split('==')
                elif '<=' in s:
                    s, less_than_or_equal_to = s.split('<=')
                elif '>=' in s:
                    s, greater_than_or_equal_to = s.split('>=')
                elif '<' in s:
                    s, less_than = s.split('<')
                elif '>' in s:
                    s, greater_than = s.split('>')
                elif '!=' in s:
                    s, not_equals = s.split('!=')
                elif '=' in s:
                    s, equals = s.split('=')
                if specification:
                    if s != specification:
                        raise ValueError(
                            'Multiple specifications cannot be associated with an instance of ``serial.meta.Version``: ' +
                            repr(_)
                        )
                elif s:
                    specification = s
            self.specification = specification
        self.equals = equals
        self.not_equals = not_equals
        self.less_than = less_than
        self.less_than_or_equal_to = less_than_or_equal_to
        self.greater_than = greater_than
        self.greater_than_or_equal_to = greater_than_or_equal_to
        self.types = types

    def __eq__(self, other):
        # type: (Any) -> bool
        compare_properties_functions = (
            ('equals', operator.eq),
            ('not_equals', operator.ne),
            ('less_than', operator.lt),
            ('less_than_or_equal_to', operator.le),
            ('greater_than', operator.gt),
            ('greater_than_or_equal_to', operator.ge),
        )
        if isinstance(other, str) and _DOT_SYNTAX_RE.match(other):
            other_components = tuple(int(n) for n in other.split('.'))
            for compare_property, compare_function in compare_properties_functions:
                compare_value = getattr(self, compare_property)
                if compare_value is not None:
                    compare_values = tuple(int(n) for n in compare_value.split('.'))
                    other_values = copy(other_components)
                    ld = len(other_values) - len(compare_values)
                    if ld < 0:
                        other_values = tuple(chain(other_values, [0] * (-ld)))
                    elif ld > 0:
                        compare_values = tuple(chain(compare_values, [0] * ld))
                    if not compare_function(other_values, compare_values):
                        return False
        else:
            for compare_property, compare_function in compare_properties_functions:
                compare_value = getattr(self, compare_property)
                if (compare_value is not None) and not compare_function(other, compare_value):
                    return False
        return True

    def __repr__(self):
        properties_values = []
        for p in dir(self):
            if p[0] != '_':
                v = getattr(self, p)
                if not isinstance(v, Callable):
                    properties_values.append((p, v))
        return ('\n'.join(
            ['Version('] +
            [
                '    %s=%s,' % (p, repr(v))
                for p, v in properties_values
            ] +
            [')']
        ))

    def __copy__(self):
        new_instance = self.__class__()
        for a in dir(self):
            if a[0] != '_':
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


# noinspection PyProtectedMember
class Meta(object):

    def __init__(
        self,
        data=None,  # type: Optional[Object]
        properties=(
            UNDEFINED
        ),  # Optional[Union[typing.Dict[str, properties.Property], Sequence[Tuple[str, properties.Property]]]]
        url=UNDEFINED,  # type: Optional[str]
    ):
        self.data = data
        self._properties = None  # type: Optional[Properties]
        if properties is not UNDEFINED:
            self.properties = properties
        self.url = None if url is UNDEFINED else url

    @property
    def properties(self):
        if not isinstance(self.data, type):
            if self._properties is None:
                self._properties = deepcopy(
                    get(type(self.data))._properties
                )
        # if self._properties is None:
        #     self._properties = Properties()
        return self._properties

    @properties.setter
    def properties(
        self,
        properties_
        # type: Optional[Union[typing.Dict[str, properties.Property], Sequence[Tuple[str, properties.Property]]]]
    ):
        if isinstance(properties_, Properties):
            properties_.meta = self
        else:
            properties_ = Properties(properties_, meta=self)
        self._properties = properties_

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
            if a[0] != '_' and (a not in ('data', 'properties')):
                v = getattr(self, a)
                if not isinstance(v, Callable):
                    setattr(new_instance, a, deepcopy(v, memo=memo))
        new_instance.properties = deepcopy(self.properties, memo=memo)
        new_instance.data = self.data
        return new_instance


class Properties(OrderedDict):

    def __init__(
        self,
        items=(
            None
        ),  # type: Optional[Union[typing.Dict[str, properties.Property], Sequence[Tuple[str, properties.Property]]]]
        meta=None  # type: Optional[Meta]Optional[
    ):
        self.meta = meta
        if items is None:
            super().__init__()
        else:
            if isinstance(items, OrderedDict):
                items = items.items()
            elif isinstance(items, dict):
                items = sorted(items.items(), key=lambda kv: kv)
            super().__init__(items)

    def __copy__(self):
        # type: () -> Properties
        return self.__class__(self, meta=self.meta)

    def __deepcopy__(self, memo=None):
        # type: (dict) -> Properties
        return self.__class__(
            tuple(
                (k, deepcopy(v, memo=memo))
                for k, v in self.items()
            ),
            meta=self.meta
        )

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
                if self.meta is None else
                '    ],'
            )
        if self.meta is not None:
            rv = repr(self.meta)
            rvls = rv.split('\n')
            if len(rvls) > 1:
                rvs = [rvls[0]]
                rvs += [
                    '    ' + rvl
                    for rvl in rvls[1:]
                ]
                rv = '\n'.join(rvs)
            representation.append(
                '    meta=%s' % rv
            )
        representation.append(')')
        if len(representation) > 2:
            return '\n'.join(representation)
        else:
            return ''.join(representation)


def get(
    o  # type: Union[type, serial.model.Object]
):
    # type: (...) -> Union[Meta, typing.Mapping, str]
    if isinstance(o, type):
        # noinspection PyProtectedMember
        if o._meta is None:
            o._meta = Meta(data=o)
        return o._meta
    else:
        if o._meta is None:
            o._meta = deepcopy(get(type(o)))
    return o._meta


