#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `certifiable.core.certify_enum` method."""

import unittest
from decimal import Decimal

from certifiable import CertifierTypeError
from certifiable.core import certify_enum


class CoreCertifyEnumTestCase(unittest.TestCase):
    """Tests for `certifiable.core.certify_enum` method."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_wrong_enum(self):
        from tests import TestEnum, TestEnum1

        i = TestEnum.X
        self.assertRaises(
            CertifierTypeError,
            certify_enum,
            i,
            kind=TestEnum1,
            required=True,
        )

    def test_correct_enum(self):
        from tests import TestEnum

        i = TestEnum.X
        certify_enum(
            i,
            kind=TestEnum,
            required=True,
        )

    def test_not_enum(self):
        from tests import TestEnum

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
                certify_enum,
                i,
                kind=TestEnum,
                required=True,
            )


if __name__ == '__main__':
    unittest.main()
