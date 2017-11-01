# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# stdlib imports
import unittest
from functools import partial

# local imports
from serafin import Context, serialize


class CustomClass(Context):
    pass


class TestSerialize(unittest.TestCase):
    def _test_dict(self):
        return {
            'field1': 10,
            'field2': {
                'sub1': 1,
                'sub2': 2,
            },
            'field3': 20,
        }

    def test_serialize__all(self):
        model = self._test_dict()
        self.assertDictEqual(serialize(model, '*'), {
            'field1': 10,
            'field2': {},
            'field3': 20
        })

    def test_serialize__selected(self):
        model = self._test_dict()

        self.assertDictEqual(serialize(model, 'field1,field3'), {
            'field1': 10,
            'field3': 20
        })

    def test_serialize__expand_selected(self):
        model = self._test_dict()
        self.assertDictEqual(serialize(model, 'field1,field2(sub1)'), {
            'field1': 10,
            'field2': {
                'sub1': 1
            }
        })

    def test_serialize__expand_all(self):
        model = self._test_dict()
        self.assertDictEqual(serialize(model, 'field1,field2(*)'), {
            'field1': 10,
            'field2': {
                'sub1': 1,
                'sub2': 2
            }
        })

    def test_serialize__all_recursive(self):
        model = self._test_dict()

        self.assertDictEqual(serialize(model, '**'), {
            'field1': 10,
            'field2': {
                'sub1': 1,
                'sub2': 2
            },
            'field3': 20
        })

    def test_context_is_being_passed(self):
        # pylint: disable=unused-variable
        @serialize.type(CustomClass)
        def custom_serialize(obj, spec, ctx):
            ctx.called()
            self.assertIn('test_val', ctx)
            self.assertEqual(ctx.test_val, 123)

        tmp = Context(called=False)
        obj = CustomClass(test_val=321)
        called = partial(setattr, tmp, 'called', True)
        serialize(obj, '*', test_val=123, called=called)
        self.assertTrue(tmp.called)
