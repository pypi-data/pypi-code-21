#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `certifiable.utils` package."""

import unittest

from certifiable import CertifierError, CertifierTypeError, CertifierValueError


class UtilsTestCase(unittest.TestCase):
    """Tests for `certifiable.utils` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_CertifierError(self):
        msg = '123'
        value = 456
        required = False
        try:
            raise CertifierError(msg, value, required)
        except CertifierError as e:
            self.assertEqual(e.value, value)
            self.assertEqual(e.required, required)
            self.assertEqual(str(e), msg)
        else:
            assert False

    def test_CertifierValueError(self):
        self.assertTrue(issubclass(CertifierValueError, CertifierError))
        self.assertTrue(issubclass(CertifierValueError, ValueError))

    def test_CertifierTypeError(self):
        self.assertTrue(issubclass(CertifierTypeError, CertifierError))
        self.assertTrue(issubclass(CertifierTypeError, TypeError))


if __name__ == '__main__':
    unittest.main()
