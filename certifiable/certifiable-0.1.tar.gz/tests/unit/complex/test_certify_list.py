#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `certifiable.complex.certify_list` method."""

import unittest

from mock import Mock, call

from certifiable import CertifierTypeError, CertifierValueError
from certifiable.complex import certify_list
from certifiable.errors import CertifierParamError
from tests.utils import aSequence, aSet, mSequence, mSet, aIterable


class ComplexListTestCase(unittest.TestCase):
    """Tests for `certifiable.complex.certify_list` method."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_list(self):
        for i in [
            [],
            list([1, 2, 3]),
            aSequence([1, 2, 3]),
            mSequence([4, 5, 6])
        ]:
            certify_list(
                i,
                include_collections=True,
            )

    def test_list_no_collections(self):
        for i in [
            aSequence(),
            mSequence()
        ]:
            self.assertRaises(
                CertifierTypeError,
                certify_list,
                i,
                include_collections=False,
            )

    def test_not_list(self):
        include_collections = True
        for i in [
            set(),
            aIterable,
            aSet(),
            mSet(),
        ]:
            print(i)
            self.assertRaises(
                CertifierTypeError,
                certify_list,
                i,
                include_collections=include_collections,
                required=True,
            )

        include_collections = False
        for i in [
            set(),
            tuple(),
            aIterable,
            aSet(),
            mSet(),
            mSequence()
        ]:
            print(i)
            self.assertRaises(
                CertifierTypeError,
                certify_list,
                i,
                include_collections=include_collections,
                required=True,
            )

    def test_min_length_fail(self):
        for i in [
            [1, 2, 3, 4],
            list(),
        ]:
            self.assertRaises(
                CertifierValueError,
                certify_list,
                i,
                min_len=5,
                required=True,
            )

    def test_min_length_ok(self):
        for i in [
            [1, 2, 3, 4],
            list(),
        ]:
            certify_list(
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
                certify_list,
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
                certify_list,
                i,
                max_len=-1,
                required=True,
            )

    def test_max_length_fail(self):
        for i in [
            [1, 2, 3, 4],
            list([1]),
        ]:
            self.assertRaises(
                CertifierValueError,
                certify_list,
                i,
                max_len=0,
                required=True,
            )

    def test_max_length_ok(self):
        for i in [
            [1, 2, 3, 4],
            list(),
        ]:
            certify_list(
                i,
                max_len=4,
                required=True,
            )

    def test_certifier_applied_to_each_element(self):
        e_result = [10, 8]
        required = True
        certifier = Mock()

        certify_list(
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
