#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `certifiable.core.certify_printable` method."""
import string
import unittest

import six

from certifiable import CertifierValueError
from certifiable.core import _certify_printable, certify_printable


class CoreCertifyPrintableTestCase(unittest.TestCase):
    """Tests for `certifiable.core.certify_printable` method."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_visible(self):
        for val in ['', string.printable, six.u('i'), six.u(string.printable)]:
            certify_printable(
                val,
                nonprintable=False,
                required=True,
            )

    def test_non_visible(self):
        for val in ['\x00', six.u('\x00')]:
            self.assertRaises(
                CertifierValueError,
                certify_printable,
                val,
                nonprintable=False,
                required=True,
            )

            certify_printable(
                val,
                nonprintable=True,
                required=True,
            )

    def test_certify_printable_no_non_required_value(self):
        self.assertIsNone(_certify_printable(
            None,
            required=False,
        ))
        self.assertIsNone(certify_printable(
            None,
            required=False,
        ))


if __name__ == '__main__':
    unittest.main()
