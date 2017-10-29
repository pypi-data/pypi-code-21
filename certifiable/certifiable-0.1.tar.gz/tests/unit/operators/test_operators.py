#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `certifiable.operators` package."""

import unittest

from certifiable import ALL, AND, ANY, CertifierValueError, NAND, XOR, certify_all, certify_any, \
    certify_none, certify_only_one
from tests import Doh, TestError, nok, ok


class OperatorsTestCase(unittest.TestCase):
    """Tests for `certifiable.operators` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_ANY_any(self):
        for oper in [
            ANY,
            certify_any,
        ]:
            oper()
            oper(
                lambda: ok(),
            )
            oper(
                lambda: ok(),
                lambda: ok(),
            )
            oper(
                lambda: nok(err=CertifierValueError),
            )
            oper(
                lambda: nok(err=CertifierValueError),
                lambda: nok(err=CertifierValueError),
            )
            oper(
                lambda: ok(),
                lambda: nok(err=CertifierValueError),
            )

    def test_ANY_any_all_fail(self):
        for oper in [
            ANY,
            certify_any,
        ]:
            self.assertRaises(
                TestError,
                oper,
                lambda: nok(err=TestError),
            )
            try:
                oper(
                    lambda: nok(x=1, err=TestError),
                    lambda: nok(x=2, err=TestError),
                )
            except TestError as e:
                self.assertEqual(e.value, 1)

    def test_ALL_AND_all(self):
        for oper in [
            AND,
            ALL,
            certify_all,
        ]:
            oper()
            oper(
                lambda: ok(),
            )
            oper(
                lambda: ok(),
                lambda: ok(),
            )

    def test_ALL_AND_all_fail(self):
        for oper in [
            AND,
            ALL,
            certify_all,
        ]:
            self.assertRaises(
                Doh,
                oper,
                lambda: nok()
            )
            self.assertRaises(
                Doh,
                oper,
                lambda: nok(),
                lambda: ok(),
            )
            try:
                oper(
                    lambda: nok(1),
                    lambda: nok(2),
                )
            except Doh as e:
                self.assertEqual(e.x, 1)
            else:
                assert False

    def test_NAND_none(self):
        for oper in [
            NAND,
            certify_none,
        ]:
            oper()
            oper(
                lambda: nok(),
            )
            oper(
                lambda: nok(),
                lambda: nok(),
            )

    def test_NAND_none_all_fail(self):
        self.assertEqual(NAND, certify_none)

        for oper in [
            NAND,
            certify_none,
        ]:
            self.assertRaises(
                CertifierValueError,
                oper,
                lambda: nok(),
                lambda: ok(),
            )
            self.assertRaises(
                CertifierValueError,
                oper,
                lambda: ok(),
                lambda: ok(),
            )

    def test_XOR_none(self):
        for oper in [
            XOR,
            certify_only_one,
        ]:
            oper(
                lambda: ok(),
                lambda: nok(),
            )
            oper(
                lambda: nok(),
                lambda: ok(),
            )

    def test_XOR_none_all_fail(self):
        for oper in [
            XOR,
            certify_only_one,
        ]:
            self.assertRaises(
                CertifierValueError,
                oper,
                lambda: ok(),
                lambda: ok(),
            )
            self.assertRaises(
                CertifierValueError,
                oper,
                lambda: nok(),
                lambda: nok(),
            )


if __name__ == '__main__':
    unittest.main()
