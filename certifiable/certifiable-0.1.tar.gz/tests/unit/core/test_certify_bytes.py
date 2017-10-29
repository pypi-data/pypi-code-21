#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `certifiable.core.certify_bytes` method."""

import unittest
from decimal import Decimal

import six

from certifiable import CertifierTypeError, CertifierValueError
from certifiable.core import certify_bytes


class CoreCertifyBytesTestCase(unittest.TestCase):
    """Tests for `certifiable.core.certify_bytes` method."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_not_bytes(self):
        for i in [
            0,
            True,
            False,
            3.4,
            5L,
            complex(6, 7),
            Decimal(8)
        ]:
            self.assertRaises(
                CertifierTypeError,
                certify_bytes,
                i,
                required=True,
            )

    def test_min_length(self):
        val = six.b('qwerty')
        for min_length in range(0, 7):
            certify_bytes(
                val,
                min_length=min_length,
                required=True,

            )
        for min_length in range(7, 10):
            self.assertRaises(
                CertifierValueError,
                certify_bytes,
                val,
                min_length=min_length,
                required=True,
            )

    def test_max_length(self):
        val = six.b('qwerty')
        for max_length in range(0, 6):
            self.assertRaises(
                CertifierValueError,
                certify_bytes,
                val,
                max_length=max_length,
                required=True,
            )
        for max_length in range(6, 10):
            certify_bytes(
                val,
                max_length=max_length,
                required=True,

            )


if __name__ == '__main__':
    unittest.main()
