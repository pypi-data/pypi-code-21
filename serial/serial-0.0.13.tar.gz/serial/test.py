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
from itertools import chain

from serial import meta, model

try:
    import typing
except ImportError as e:
    typing = None


def _object_discrepancies(a, b):
    # type: (Object, Object) -> dict
    discrepancies = {}
    a_properties = set(meta.get(a).properties.keys())
    b_properties = set(meta.get(b).properties.keys())
    for p in a_properties | b_properties:
        try:
            av = getattr(a, p)
        except AttributeError:
            av = None
        try:
            bv = getattr(b, p)
        except AttributeError:
            bv = None
        if av != bv:
            discrepancies[p] = (av, bv)
    return discrepancies


def json_object(
    o  # type: Union[model.Object, typing.Sequence]
):
    if isinstance(o, model.Object):
        model.validate(o)
        t = type(o)
        string = str(o)
        assert string != ''
        reloaded = t(string)
        try:
            assert o == reloaded
        except AssertionError as e:
            message = [
                'Discrepancies were found between the instance of `%s` provided and ' % qualified_name(type(o)) +
                'a serialized/deserialized clone:'
            ]
            for k, a_b in _object_discrepancies(o, reloaded).items():
                a, b = a_b
                sa = model.serialize(a)
                sb = model.serialize(b)
                message.append(
                    '\n    %s().%s:\n\n        %s\n        %s\n        %s' % (
                        tn,
                        k,
                        sa,
                        '==' if sa == sb else '!=',
                        sb
                    )
                )
                ra = ''.join(l.strip() for l in repr(a).split('\n'))
                rb = ''.join(l.strip() for l in repr(b).split('\n'))
                message.append(
                    '\n        %s\n        %s\n        %s' % (
                        ra,
                        '==' if ra == rb else '!=',
                        rb
                    )
                )
            e.args = tuple(
                chain(
                    (e.args[0] + '\n' + '\n'.join(message) if e.args else '\n'.join(message),),
                    e.args[1:] if e.args else tuple()
                )
            )
            raise e
        reloaded_string = str(reloaded)
        assert string == reloaded_string
        reloaded_json = json.loads(
            string,
            object_hook=collections.OrderedDict,
            object_pairs_hook=collections.OrderedDict
        )
        keys = set()
        for n, p in meta.get(o).properties.items():
            keys.add(p.name or n)
            json_object(getattr(o, n))
        for k in reloaded_json.keys():
            if k not in keys:
                raise KeyError(
                    '"%s" not found in serialized/re-deserialized data: %s' % (
                        k,
                        string
                    )
                )
    elif (
        # ``isinstance(o, collections.Iterable)`` produces a recursion error in Python 2x, so we test for the
        # existence of an '__iter__' method directly
        hasattr(o, '__iter__') and not
        isinstance(o, (str, native_str, bytes))
    ):
        if isinstance(o, (dict, collections.OrderedDict, model.Dictionary)):
            for k, v in o.items():
                json_object(v)
        else:
            for oo in o:
                json_object(oo)