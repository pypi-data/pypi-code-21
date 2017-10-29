#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `certifiable.complex.certify_dict` method."""

import unittest
from decimal import Decimal

from certifiable import CertifierTypeError
from certifiable.complex import certify_dict
from tests.utils import aIterable, aMapping, aSet, mMapping, mSet


class ComplexDictTestCase(unittest.TestCase):
    """Tests for `certifiable.complex.certify_dict` method."""

    def dictUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_dict(self):
        for i in [
            dict(),
            mMapping(),
            aMapping(),
        ]:
            certify_dict(
                i,
                include_collections=True,
            )

    def test_dict_no_collections(self):
        for i in [
            aMapping(),
            mMapping(),
        ]:
            self.assertRaises(
                CertifierTypeError,
                certify_dict,
                i,
                include_collections=False,
            )

    def test_not_dict(self):
        for include_collections in [True, False]:
            for i in [
                list(),
                tuple(),
                aIterable,
                aSet(),
                mSet(),
                '',
                1.2,
                3,
                Decimal(4)
            ]:
                self.assertRaises(
                    CertifierTypeError,
                    certify_dict,
                    i,
                    include_collections=include_collections,
                    required=True,
                )


if __name__ == '__main__':
    unittest.main()
