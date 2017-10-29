#!/usr/bin/env python
# -*- coding: latin-1 -*-
#
# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `certifiable.complex.certify_tuple` method."""

import unittest

from mock import Mock

from certifiable import CertifierValueError, make_certifier
from certifiable.complex import certify_dict_schema, certify_iterable_schema
from certifiable.errors import CertifierParamError
from tests import Doh


class ComplexIterableSchemaTestCase(unittest.TestCase):
    """Tests for `certifiable.complex.certify_iterable_schema` method."""

    def setUp(self):
        """Tuple up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_schema_none_provided(self):
        required = True
        certify_iterable_schema(
            value=[],
            schema=[],
            required=required,
        )

    def test_schema_lengths_different_not_enough_values(self):
        value = []
        required = True

        schema = tuple([
            None,
            None,
            None
        ])

        try:
            certify_iterable_schema(
                value=value,
                schema=schema,
                required=required,
            )
        except CertifierValueError as e:
            self.assertEqual(e.message, 'encountered -3 extra items')
            self.assertEqual(e.required, required)
            self.assertEqual(e.value, value)
        else:
            assert False

    def test_schema_lengths_different_too_many_values(self):
        value = [
            1,
            2,
            3,
            4,
            5,
            6,
        ]
        required = True

        schema = tuple([
            None,
            None,
        ])

        try:
            certify_iterable_schema(
                value=value,
                schema=schema,
                required=required,
            )
        except CertifierValueError as e:
            self.assertEqual(e.message, 'encountered 4 extra items')
            self.assertEqual(e.required, required)
            self.assertEqual(e.value, value)
        else:
            assert False

    def test_certifier_error_reraised(self):
        value = [
            'abc',
            'xyz',
        ]
        required = True

        @make_certifier()
        def x(value, **kwargs):
            raise Doh('bang: {value}'.format(
                value=value,
            ))

        schema = tuple([
            lambda value: None,
            x,
        ])

        try:
            certify_iterable_schema(
                value=value,
                schema=schema,
                required=required,
            )
        except CertifierValueError as e:
            self.assertEqual(e.message, 'invalid value \'xyz\' for item 1')
            self.assertEqual(e.required, required)
            self.assertEqual(e.value, value)
        else:
            assert False


class ComplexDictSchemaTestCase(unittest.TestCase):
    """Tests for `certifiable.complex.certify_dict_schema` method."""

    def setUp(self):
        """Tuple up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_no_schema_or_certifiers(self):
        value = {'a': 1, 'b': 2}
        schema = {}
        allow_extra = True
        certify_dict_schema(
            value=value,
            schema=schema,
            key_certifier=None,
            value_certifier=None,
            required=True,
            allow_extra=allow_extra,
        )

    def test_invalid_schema(self):
        value = {'a': 1, 'b': 2}
        schema = 123
        allow_extra = True
        self.assertRaises(
            CertifierParamError,
            certify_dict_schema,
            value=value,
            schema=schema,
            key_certifier=None,
            value_certifier=None,
            required=True,
            allow_extra=allow_extra,
        )

    def test_key_certifier(self):
        value = {'a': 1, 'b': 2}
        schema = None
        m = Mock()

        @make_certifier()
        def key_certifier(value):
            m(value)
            raise Doh()

        allow_extra = True
        self.assertRaises(
            Doh,
            certify_dict_schema,
            value=value,
            schema=schema,
            key_certifier=key_certifier,
            value_certifier=None,
            required=True,
            allow_extra=allow_extra,
        )

        self.assertEqual(m.call_count, 1)

    def test_value_certifier(self):
        value = {'a': 1, 'b': 2}
        schema = None
        m = Mock()

        @make_certifier()
        def key_certifier(value):
            m(value)
            raise Doh()

        allow_extra = True
        self.assertRaises(
            Doh,
            certify_dict_schema,
            value=value,
            schema=schema,
            key_certifier=None,
            value_certifier=key_certifier,
            required=True,
            allow_extra=allow_extra,
        )

        self.assertEqual(m.call_count, 1)

    def test_extra_key_not_allowed(self):
        @make_certifier()
        def key_certifier(value):
            m(value)

        required = True
        value = {'a': 1, 'b': 2}
        schema = {
            'a': key_certifier,
        }
        m = Mock()

        allow_extra = False

        try:
            certify_dict_schema(
                value=value,
                schema=schema,
                key_certifier=None,
                value_certifier=None,
                required=required,
                allow_extra=allow_extra,
            )
        except CertifierValueError as e:
            self.assertEqual(e.message, 'encountered unexpected keys: set([\'b\'])')
            self.assertEqual(e.required, required)
            self.assertIn(e.value, [set(['b']), set(['b'])])
        else:
            assert False

        self.assertEqual(m.call_count, 1)

    def test_key_not_in_schema(self):
        @make_certifier()
        def key_certifier(value):
            m(value)

        required = True
        value = {'b': 2}
        schema = {
            'a': key_certifier,
        }
        m = Mock()

        allow_extra = False

        try:
            certify_dict_schema(
                value=value,
                schema=schema,
                key_certifier=None,
                value_certifier=None,
                required=required,
                allow_extra=allow_extra,
            )
        except CertifierValueError as e:
            self.assertEqual(e.message, 'key \'a\' missing from dictionary')
            self.assertEqual(e.required, required)
        else:
            assert False

        m.assert_not_called()

    def test_schema_ok(self):
        @make_certifier()
        def value_certifier_2(value):
            m2(value)
            assert value == 2

        @make_certifier()
        def value_certifier_3(value):
            m3(value)
            assert value == 3

        @make_certifier()
        def value_certifier_4(value):
            m4(value)
            assert value == 4

        required = True
        value = {
            'a': 2,
            'b': 3,
            'c': 4,
        }
        schema = {
            'a': value_certifier_2,
            'b': value_certifier_3,
            'c': value_certifier_4,
        }
        m2 = Mock()
        m3 = Mock()
        m4 = Mock()

        certify_dict_schema(
            value=value,
            schema=schema,
            key_certifier=None,
            value_certifier=None,
            required=required,
        )

    def test_schema_fail(self):
        @make_certifier()
        def value_certifier(value):
            m(value)
            assert value == 2
            raise Doh()

        required = True
        value = {
            'a': 2,
        }
        schema = {
            'a': value_certifier,
        }
        m = Mock()

        self.assertRaises(
            Doh,
            certify_dict_schema,
            value=value,
            schema=schema,
            key_certifier=None,
            value_certifier=None,
            required=required,
        )
        self.assertEqual(m.call_count, 1)


if __name__ == '__main__':
    unittest.main()
