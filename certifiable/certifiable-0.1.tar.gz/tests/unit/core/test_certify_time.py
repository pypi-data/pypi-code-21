#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `certifiable.core.certify_time` method."""

import datetime
import unittest
from decimal import Decimal

from certifiable import CertifierTypeError
from certifiable.core import certify_time


class CoreCertifyTimeTestCase(unittest.TestCase):
    """Tests for `certifiable.core.certify_time` method."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_time(self):
        for i in [
            datetime.time(),
        ]:
            certify_time(
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
            datetime.date.today(),
            TestEnum1.X,
        ]:
            self.assertRaises(
                CertifierTypeError,
                certify_time,
                i,
                required=True,
            )


if __name__ == '__main__':
    unittest.main()
