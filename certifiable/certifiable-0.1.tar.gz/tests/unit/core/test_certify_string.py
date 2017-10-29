#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `certifiable.core.certify_string` method."""
import string
import unittest

import six

from certifiable import CertifierTypeError, CertifierValueError
from certifiable.core import certify_string


class CoreStringStringTestCase(unittest.TestCase):
    """Tests for `certifiable.core.certify_string` method."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_not_text(self):
        self.assertRaises(
            CertifierTypeError,
            certify_string,
            123,
            required=True,
        )

    def test_min_length(self):
        val = six.u('qwerty')
        for min_length in range(0, 7):
            certify_string(
                val,
                min_length=min_length,
                required=True,

            )
        for min_length in range(7, 10):
            self.assertRaises(
                CertifierValueError,
                certify_string,
                val,
                min_length=min_length,
                required=True,
            )

    def test_max_length(self):
        val = six.u('qwerty')
        for max_length in range(0, 6):
            self.assertRaises(
                CertifierValueError,
                certify_string,
                val,
                max_length=max_length,
                required=True,
            )
        for max_length in range(6, 10):
            certify_string(
                val,
                max_length=max_length,
                required=True,

            )

    def test_visible(self):
        for val in [six.u(''), six.u(string.printable)]:
            certify_string(
                val,
                nonprintable=False,
                required=True,
            )

    def test_non_visible(self):
        val = six.u('\x00')
        self.assertRaises(
            CertifierValueError,
            certify_string,
            val,
            nonprintable=False,
            required=True,
        )

        certify_string(
            val,
            nonprintable=True,
            required=True,
        )


if __name__ == '__main__':
    unittest.main()
