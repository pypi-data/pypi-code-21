#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `certifiable.complex.certify_tuple` method."""

import unittest

from mock import Mock, call

from certifiable import CertifierTypeError, CertifierValueError
from certifiable.complex import certify_tuple
from certifiable.errors import CertifierParamError
from tests.utils import aSet, mSet, aIterable


class ComplexTupleTestCase(unittest.TestCase):
    """Tests for `certifiable.complex.certify_tuple` method."""

    def setUp(self):
        """Tuple up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_tuple(self):
        for i in [
            (),
            (1,),
            tuple(),
        ]:
            certify_tuple(
                i,
            )

    def test_not_tuple(self):
        for i in [list(), set(), aIterable, mSet(), aSet()]:
            self.assertRaises(
                CertifierTypeError,
                certify_tuple,
                i,
                required=True,
            )

    def test_min_length_fail(self):
        for i in [
            (1, 2, 3, 4),
            tuple(),
        ]:
            self.assertRaises(
                CertifierValueError,
                certify_tuple,
                i,
                min_len=5,
                required=True,
            )

    def test_min_length_ok(self):
        for i in [
            (1, 2, 3, 4),
            tuple(),
        ]:
            certify_tuple(
                i,
                min_len=0,
                required=True,
            )

    def test_min_length_bad(self):
        for i in [
            set(),
        ]:
            self.assertRaises(
                CertifierParamError,
                certify_tuple,
                i,
                min_len=-1,
                required=True,
            )

    def test_max_length_bad(self):
        for i in [
            set(),
        ]:
            self.assertRaises(
                CertifierParamError,
                certify_tuple,
                i,
                max_len=-1,
                required=True,
            )

    def test_max_length_fail(self):
        for i in [
            tuple([1, 2, 3, 4]),
            tuple([1]),
        ]:
            self.assertRaises(
                CertifierValueError,
                certify_tuple,
                i,
                max_len=0,
                required=True,
            )

    def test_max_length_ok(self):
        for i in [
            tuple([1, 2, 3, 4]),
            tuple([1]),
        ]:
            certify_tuple(
                i,
                max_len=4,
                required=True,
            )

    def test_certifier_applied_to_each_element(self):
        e_result = tuple([10, 8])
        required = True
        certifier = Mock()

        certify_tuple(
            e_result,
            certifier=certifier,
            required=required,
        )

        self.assertEqual(certifier.call_count, 2)
        certifier.assert_has_calls(
            [
                call(10),
                call(8),
            ],
            any_order=False,
        )

    def test_schema(self):
        # TODO: Implement this.
        pass


if __name__ == '__main__':
    unittest.main()
