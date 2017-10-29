#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `certifiable.core.certify_enum_value_value` method."""

import unittest
from decimal import Decimal

from certifiable import CertifierValueError
from certifiable.core import certify_enum_value


class CoreCertifyEnumValueTestCase(unittest.TestCase):
    """Tests for `certifiable.core.certify_enum_value_value` method."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_wrong_enum(self):
        from tests import TestEnum, TestEnum1

        for i in [
            TestEnum.A,
            TestEnum.B.value,
        ]:
            self.assertRaises(
                CertifierValueError,
                certify_enum_value,
                i,
                kind=TestEnum1,
                required=True,
            )

    def test_correct_enum(self):
        from tests import TestEnum

        for i in [
            TestEnum.X,
            TestEnum.X.value,
        ]:
            certify_enum_value(
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
                CertifierValueError,
                certify_enum_value,
                i,
                kind=TestEnum,
                required=True,
            )


if __name__ == '__main__':
    unittest.main()
