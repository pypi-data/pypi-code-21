#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `certifiable.core.certify_bool` method."""
import unittest

from certifiable import CertifierTypeError, CertifierValueError
from certifiable.core import certify_bool


class CoreCertifyBoolTestCase(unittest.TestCase):
    """Tests for `certifiable.core.certify_bool` method."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_bool(self):
        for i in [
            True,
            False,
        ]:
            certify_bool(i)

    def test_not_bool(self):
        for i in [1, 0, 2L, 3.9, '1.2', 'three', complex(1, 2)]:
            self.assertRaises(
                CertifierTypeError,
                certify_bool,
                i,
                required=True,
            )


if __name__ == '__main__':
    unittest.main()
