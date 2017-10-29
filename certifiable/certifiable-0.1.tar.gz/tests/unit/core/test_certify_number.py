#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `certifiable.core.certify_number` method."""
import sys
import unittest
from decimal import Decimal

from certifiable import CertifierTypeError, CertifierValueError
from certifiable.core import certify_number


class CoreCertifyNumberTestCase(unittest.TestCase):
    """Tests for `certifiable.core.certify_number` method."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_number(self):
        for i in [
            -sys.maxint, sys.maxint,
            0,
            0.0, 3.2, -3.2,
            100000L, -100000L,
            Decimal(3.2)
        ]:
            certify_number(i)

    def test_not_number(self):
        for i in ['1.2', 'three', complex(1, 2)]:
            self.assertRaises(
                CertifierTypeError,
                certify_number,
                i,
                required=True,
            )

    def test_min_value(self):
        val = 7
        for min_value in range(-8, 8):
            certify_number(
                val,
                min_value=min_value,
                required=True,

            )
        for min_value in range(8, 10):
            self.assertRaises(
                CertifierValueError,
                certify_number,
                val,
                min_value=min_value,
                required=True,
            )

    def test_max_value(self):
        val = 6
        for max_value in range(-6, 6):
            self.assertRaises(
                CertifierValueError,
                certify_number,
                val,
                max_value=max_value,
                required=True,
            )
        for max_value in range(6, 10):
            certify_number(
                val,
                max_value=max_value,
                required=True,

            )


if __name__ == '__main__':
    unittest.main()
