#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `certifiable.complex.certify_set` method."""

import unittest

from mock import Mock, call

from certifiable import CertifierTypeError, CertifierValueError
from certifiable.complex import certify_set
from certifiable.errors import CertifierParamError
from tests.utils import aSet, mSet, aIterable


class ComplexSetTestCase(unittest.TestCase):
    """Tests for `certifiable.complex.certify_set` method."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_set(self):
        for i in [
            set(),
            aSet(),
            mSet(),
        ]:
            certify_set(
                i,
                include_collections=True,
            )

    def test_set_no_collections(self):
        for i in [
            aSet(),
            mSet(),
        ]:
            self.assertRaises(
                CertifierTypeError,
                certify_set,
                i,
                include_collections=False,
            )

    def test_not_set(self):
        for include_collections in [True, False]:
            for i in [list(), tuple(), aIterable]:
                self.assertRaises(
                    CertifierTypeError,
                    certify_set,
                    i,
                    include_collections=include_collections,
                    required=True,
                )

    def test_min_length_fail(self):
        for i in [
            {1, 2, 3, 4},
            set(),
        ]:
            self.assertRaises(
                CertifierValueError,
                certify_set,
                i,
                min_len=5,
                required=True,
            )

    def test_min_length_ok(self):
        for i in [
            {1, 2, 3, 4},
            set(),
        ]:
            certify_set(
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
                certify_set,
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
                certify_set,
                i,
                max_len=-1,
                required=True,
            )

    def test_max_length_fail(self):
        for i in [
            {1, 2, 3, 4},
            {1},
        ]:
            self.assertRaises(
                CertifierValueError,
                certify_set,
                i,
                max_len=0,
                required=True,
            )

    def test_max_length_ok(self):
        for i in [
            {1, 2, 3, 4},
            set(),
        ]:
            certify_set(
                i,
                max_len=4,
                required=True,
            )

    def test_certifier_applied_to_each_element(self):
        e_result = {10, 8}
        required = True
        certifier = Mock()

        certify_set(
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
            any_order=True,
        )


if __name__ == '__main__':
    unittest.main()
