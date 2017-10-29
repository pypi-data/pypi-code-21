#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `certifiable.core.certify_timestamp` method."""

import datetime
import unittest
from decimal import Decimal

from certifiable import CertifierTypeError
from certifiable.core import certify_timestamp


class CoreCertifyTimestampTestCase(unittest.TestCase):
    """Tests for `certifiable.core.certify_timestamp` method."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_timestamp(self):
        for i in [
            datetime.datetime.utcnow(),
        ]:
            certify_timestamp(
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
            datetime.date(2017, 11, 1),
            TestEnum1.X,
        ]:
            self.assertRaises(
                CertifierTypeError,
                certify_timestamp,
                i,
                required=True,
            )


if __name__ == '__main__':
    unittest.main()
