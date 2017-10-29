#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `certifiable.core.certify_date` method."""

import datetime
import unittest
from decimal import Decimal

from certifiable import CertifierTypeError
from certifiable.core import certify_date


class CoreCertifyDateTestCase(unittest.TestCase):
    """Tests for `certifiable.core.certify_date` method."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_timestamp(self):
        for i in [
            datetime.date(2017, 11, 30),
        ]:
            certify_date(
                i,
                required=True,
            )

    def test_not_timestamp(self):
        from tests import TestEnum1

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
                CertifierTypeError,
                certify_date,
                i,
                required=True,
            )


if __name__ == '__main__':
    unittest.main()
