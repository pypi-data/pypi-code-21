#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for common use cases."""

import unittest

from certifiable import AND, NAND, XOR
from tests import Alt, Doh, nok, ok


class CommonUseCaseTestCase(unittest.TestCase):
    """Tests for common use cases."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_AND_ok(self):
        AND(
            lambda: ok(),
            lambda: ok(),
        )

    def test_AND_not_ok(self):
        try:
            AND(
                lambda: ok(),
                lambda: nok(),
            )
        except Doh:
            assert True
        else:
            assert False
        try:
            AND(
                lambda: nok(),
                lambda: ok(),
            )
        except Doh:
            assert True
        else:
            assert False
        try:
            AND(
                lambda: ok(),
                lambda: nok(),
                exc=lambda x: Alt(x)
            )
        except Alt:
            assert True
        else:
            assert False
        try:
            AND(
                lambda: nok(),
                lambda: ok(),
                exc=lambda x: Alt(x)
            )
        except Alt:
            assert True
        else:
            assert False

    def test_NAND_ok(self):
        NAND(
            lambda: nok(),
            lambda: nok(),
        )

    def test_NAND_not_ok(self):

        try:
            NAND(
                lambda: ok(),
                lambda: nok(),
            )
        except ValueError:
            assert True
        else:
            assert False
        try:
            NAND(
                lambda: nok(),
                lambda: ok(),
            )
        except ValueError:
            assert True
        else:
            assert False
        try:
            NAND(
                lambda: ok(),
                lambda: nok(),
                exc=Alt()
            )
        except Alt:
            assert True
        else:
            assert False
        try:
            AND(
                lambda: nok(),
                lambda: ok(),
                exc=lambda x: Alt(x)
            )
        except Alt:
            assert True
        else:
            assert False

    def test_XOR_ok(self):
        XOR(
            lambda: nok(),
            lambda: ok(),
        )
        XOR(
            lambda: ok(),
            lambda: nok(),
        )

    def test_XOR_not_ok(self):
        try:
            XOR(
                lambda: ok(),
                lambda: ok(),
            )
        except ValueError:
            assert True
        else:
            assert False

        try:
            XOR(
                lambda: nok(),
                lambda: nok(),
            )
        except ValueError:
            assert True
        else:
            assert False
        try:
            XOR(
                lambda: ok(),
                lambda: ok(),
                exc=Doh(),
            )
        except Doh:
            assert True
        else:
            assert False

        try:
            XOR(
                lambda: nok(),
                lambda: nok(),
                exc=Doh(),
            )
        except Doh:
            assert True
        else:
            assert False


if __name__ == '__main__':
    unittest.main()
