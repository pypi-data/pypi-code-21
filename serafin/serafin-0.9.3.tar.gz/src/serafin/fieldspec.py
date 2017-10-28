# -*- coding: utf-8 -*-
""" Serialization field spec implementation.

This is what makes the serialization so flexible as it allows to cherry-pick
what is actually serialized. This module just implements the serialization field
specification itself and the rest of the system uses it to define/decide what
is being included in the resulting data.

This module **has** to be really well tested as everything else depends on it
and the implementation itself is a bit tricky.
"""
from __future__ import absolute_import, unicode_literals

# stdlib imports
import sys
import re
from copy import deepcopy
from collections import OrderedDict
if sys.version_info >= (3, 0):
    from urllib.parse import parse_qsl
else:
    from urlparse import parse_qsl

# 3rd party imports
from six import string_types, iteritems     # noqa


kFieldPtrn = re.compile(r'{name}(\({members}\))?'.format(
    name=r'(?P<name>-?[\w\d_*]+)',
    members=r'(?P<members>[\w\d_\-,*)(]+)'
))


class Fieldspec(object):
    """
    ``Fieldspec`` represents field specification for REST queries. It describes
    the format in which the query result will be returned. What model fields
    should be present and which of them should be expanded. Expansion works
    for foreign keys, where instead of object key, we can insert the object
    itself (with all, or selected members).

    For usage examples see ``restapi.serialize.serialize()``.

    **Simple tests**

    >>> fs = Fieldspec('field1,field2(sub1,sub2),field3(*)')
    >>> fs
    <Fieldspec: field1,field2,field3>

    Easily check if the field is matched by the spec:
    >>> 'field1' in fs
    True
    >>> fs['field1']
    True
    >>> 'field7' in fs
    False

    Supports nested specifications:
    >>> fs['field2']
    <Fieldspec: sub1,sub2>
    >>> 'sub1' in fs['field2']
    True
    >>> fs['field2']['sub2']
    True

    And wildcards
    >>> 'asdf' in fs['field2']
    False
    >>> 'asdf' in fs['field3']
    True
    >>> fs['field3']['asdf']
    True

    Exclude
    >>> fs = Fieldspec('*,-field1')
    >>> 'asdf' in fs
    True
    >>> 'field1' in fs
    False

    **Implementation**

    Fieldspec has 2 main variables that hold the spec. The ``fields`` and
    ``exclude``. Exclude is much simpler, because it's just a list of strings
    with field names that should be excluded at this level.

    The ``fields`` member is a list of tuples ``(name, members)`` where name
    is the fields name and members is the optional member spec **members** can
    be one of:
        - None
        - ``True`` if the subfield spec is just the field name, ie ``field``.
        - ``Fieldspec`` if the subfield has a field spec defined, ie
         ``field(sub1,sub2)``.

    If the field spec contains ``*`` it means at that level all fields are
    included by default. You can still exclude them using ``-`` but by default
    all fields within an object are included.

    The special field spec `**` can be used and it means the same thing as ``*``
    but is applied recursively to all objects. **Be very careful with using it
    as it will try to serialize EVERYTHING and in many cases you will run into
    problems.

    TODO:
        - Ability to specify max depth.
        - Merging two specs together (union).
        - Restricting one spec by another (intersection).
    """
    def __init__(self, spec='*'):
        self.fields = OrderedDict()
        self.exclude = OrderedDict()
        self.spec = spec
        self.all = False

        if isinstance(spec, Fieldspec):
            # Clone
            self.fields = deepcopy(spec.fields)
            self.exclude = deepcopy(spec.exclude)
            self.all = spec.all
            self.spec = spec.spec

        elif isinstance(spec, string_types):
            self._parse(spec)

        elif spec not in (None, True):
            raise ValueError('Invalid field specification')

    def empty(self):
        """ Return **True** if the current spec is empty.

        :return bool:
            **True** if nothing represented by this field spec should be
            included as part of the serialization result.
        """
        return len(self.fields) == 0 and not self.all

    def __contains__(self, name):
        if name in self.exclude:
            return False

        if self.all:
            return True

        try:
            return self.fields[name]
        except KeyError:
            return None

    def __getitem__(self, name):
        if name in self.exclude:
            return None

        if self.spec == '**':
            return Fieldspec(self)

        try:
            return self.fields[name]
        except KeyError:
            return self.all or None

    def __repr__(self):
        include = ','.join(name for name in self.fields.keys())
        exclude = ''
        if self.exclude:
            exclude = ','.join('-' + n for n, m in self.exclude)

        return "<Fieldspec: {}{}>".format(include, exclude)

    def _parse(self, string):
        """ Parse the spec string.
        Args:
            string (str):   A string representation of the field spec.

        The string is split on the high level by commas and then processed.
        The parser will take into account the parenthesis and skip them when
        looking for comas. The members are parsed recursively.
        """
        fields  = self._splitfields(string)
        for field in fields:
            m = kFieldPtrn.match(field)
            if not m:
                raise ValueError("Invalid field specification")

            name = m.group('name')
            if name[0] == '-':
                name    = name[1:]
                group   = self.exclude
            else:
                group   = self.fields

            membstr = m.group('members')
            members = True if membstr is None else Fieldspec(membstr)
            if name in ('*', '**'):
                self.all = True
            else:
                group[name] = members

    def _splitfields(self, string):
        """
        Split field list into separate fields. Takes into account nesting
        specification (inside parenthesis) by ignoring commas inside it.

        >>> fs = Fieldspec()
        >>> fs._splitfields('one,two,three')
        ['one', 'two', 'three']

        >>> fs._splitfields('one(mem1,mem2),two,three')
        ['one(mem1,mem2)', 'two', 'three']

        """
        fields = []
        append = fields.append
        start = 0
        numparen = 0

        for i, ch in enumerate(string):
            if ch == ',':
                if i != start and numparen == 0:
                    append(string[start:i])
                    start = i + 1
            elif ch == '(':
                numparen += 1
            elif ch == ')':
                numparen -= 1

        if numparen != 0:
            raise ValueError("Unmatched parenthesis")

        fields.append(string[start:])
        return fields

    def merge(self, spec):
        """ Extend field spec using a different one. The result should be
        the union of both.

        .. notes:: If the field is in both specs and it's values are different
        there is a conflict. The conflict can be resolved by merging the sub
        specs.
        """
        if isinstance(spec, string_types):
            spec = Fieldspec(spec)

        if spec.all:
            self.all = True

        for name, members in iteritems(spec.fields):
            try:
                mymembers = self.fields[name]
                # There already is a field like that, we need to sort
                # out the conflict.
                if mymembers != members:
                    self.fields[name] = self._resolve_conflict(
                        mymembers, members
                    )
            except KeyError:
                # this field spec doesn't have the key yet
                self.fields[name] = members

        exclude = self.exclude
        self.exclude = OrderedDict()
        for name, members in iteritems(exclude):
            try:
                members = spec.fields[name]
                self.fields[name] = members
            except KeyError:
                self.exclude[name] = members

        return self

    def _resolve_conflict(self, mymembers, members):
        """ Resolve conflicting members by mergin them. """
        if isinstance(mymembers, Fieldspec):
            if isinstance(members, Fieldspec):
                return Fieldspec(mymembers).merge(members)
            else:  # members == True:
                return mymembers
        else:  # mymembers == True:
            return members

    def restrict(self, spec):
        """ Restrict the current field spec by another one. The result should be
        the intersection of both.
        """
        was_all = self.all
        my_fields = frozenset(self.fields.keys())
        other_fields = frozenset(spec.fields.keys())

        if spec.all:
            common = my_fields
        elif self.all:
            self.all = False
            common = other_fields
        else:
            common = my_fields & other_fields

        self.exclude.update(spec.exclude)

        newfields = []
        for name in common:
            try:
                mymembers = self.fields[name]
            except KeyError:
                if was_all:
                    newfields.append((name, spec.fields[name]))
                continue

            try:
                members = spec.fields[name]
                if mymembers != members:
                    newfields.append((name, self._resolve_restrict_conflict(
                        mymembers, members
                    )))
                    continue
            except KeyError:
                pass

            if name not in self.exclude:
                newfields.append((name, mymembers))

        self.fields = OrderedDict(newfields)
        return self

    def _resolve_restrict_conflict(self, mymembers, members):
        if isinstance(mymembers, Fieldspec):
            if isinstance(members, Fieldspec):
                return Fieldspec(mymembers).restrict(members)
            if members is True:
                return True
        raise NotImplementedError("Not implemented")

    @classmethod
    def from_query(self, qs):
        """ Create a field spec from a HTTP request query string. """
        qs  = dict(parse_qsl(qs)) if isinstance(qs, string_types) else qs
        return Fieldspec(qs.get('_fields', '*'))
