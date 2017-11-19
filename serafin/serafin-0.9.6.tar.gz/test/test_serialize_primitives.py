# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# stdlib imports
from unittest import TestCase
from datetime import datetime

# local imports
from serafin import Context
from serafin.core import dump_val
from serafin.serializers import serialize_primitive
from serafin.fieldspec import Fieldspec


class TestPrimitives(TestCase):
    def test_serialize_int(self):
        ctx = Context(dumpval=dump_val)
        out = serialize_primitive(5, Fieldspec('*'), ctx)
        self.assertEqual(out, 5)

    def test_serialize_None(self):
        ctx = Context(dumpval=dump_val)
        out = serialize_primitive(None, Fieldspec('*'), ctx)
        self.assertEqual(out, None)

    def test_serialize_str(self):
        ctx = Context(dumpval=dump_val)
        out = serialize_primitive('test str', Fieldspec('*'), ctx)
        self.assertEqual(out, 'test str')

    def test_serialize_datetime(self):
        dt = datetime(2015, 5, 1, 13, 21, 38)
        ctx = Context(dumpval=dump_val)
        out = serialize_primitive(dt, Fieldspec('*'), ctx)
        self.assertEqual(out, dt.isoformat())
