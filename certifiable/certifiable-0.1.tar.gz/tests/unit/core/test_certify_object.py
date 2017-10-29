#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `certifiable.core.certify_object` method."""

import unittest
from decimal import Decimal

from certifiable import CertifierValueError
from certifiable.core import certify_object


class CoreCertifyObjectTestCase(unittest.TestCase):
    """Tests for `certifiable.core.certify_object` method."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_correct_enum(self):
        from tests import TestEnum

        i = TestEnum.X
        certify_object(
            i,
            kind=TestEnum,
            required=True,
        )

    def test_not_object(self):
        from tests import TestEnum, TestEnum1

        for i in [
            0,
            True,
            False,
            3.4,
            5L,
            complex(6, 7),
            Decimal(8),
            TestEnum1.X,
        ]:
            self.assertRaises(
                CertifierValueError,
                certify_object,
                i,
                kind=TestEnum,
                required=True,
            )


if __name__ == '__main__':
    unittest.main()
