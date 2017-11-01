# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# stdlib imports
from unittest import TestCase

# local imports
from serafin import Context
from serafin.core import dump_val
from serafin.serializers import serialize_dict
from serafin.fieldspec import Fieldspec


class TestSerializeDict(TestCase):
    def test_only_primitives_inside_one_level_deep(self):
        data = {
            'field1':  123,
            'field2':  "string",
            'field3':  123.321,
            'field4':  {
                'field1': 3.14159,
                'field2': 'sub val'
            }
        }
        ctx = Context(dumpval=dump_val)
        result = serialize_dict(data, Fieldspec('*'), ctx)
        self.assertDictEqual(result, {
            'field1':  123,
            'field2':  "string",
            'field3':  123.321,
            'field4':  {}
        })

    def test_converts_string_to_Fieldspec(self):
        ctx = Context(dumpval=dump_val)
        output = serialize_dict({'test': 123}, Fieldspec('*'), ctx)
        self.assertDictEqual(output, {'test': 123})
