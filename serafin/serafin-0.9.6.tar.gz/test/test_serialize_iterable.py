# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# stdlib imports
from unittest import TestCase

# local imports
from serafin import Context
from serafin.core import dump_val
from serafin.serializers import serialize_iterable
from serafin.fieldspec import Fieldspec


class TestSerializeIterable(TestCase):
    def test_only_primitives_inside_one_level_deep(self):
        data = [1, 'test', 3.14159]
        ctx = Context(dumpval=dump_val)
        out = serialize_iterable(data, Fieldspec('*'), ctx)
        self.assertListEqual(out, data)

    def test_converts_string_to_Fieldspec(self):
        data = [1, 'test', 3.14159]
        ctx = Context(dumpval=dump_val)
        out = serialize_iterable(data, Fieldspec('*'), ctx)
        self.assertListEqual(out, data)
