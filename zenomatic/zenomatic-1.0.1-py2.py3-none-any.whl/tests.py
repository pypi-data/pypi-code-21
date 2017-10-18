"""Unittests for package.

Unit Tests for application.
Minimum coverage expected: 80%

"""
from __future__ import print_function
import unittest
from zenomatic import quotes
from zenomatic.utils import console
from zenomatic.run import start


class TestQuotes(unittest.TestCase):
    """Base Unit Test Class."""

    def test_get_wrong_quote(self):
        """Test wrong parameter."""
        ret, msg = quotes.get_quote("wrong")
        self.assertFalse(ret)

    def test_get_out_of_range_number(self):
        """Test out of range parameter."""
        ret, meg = quotes.get_quote(quotes.MAX_QUOTE + 1)
        self.assertFalse(ret)

    def test_get_quote(self):
        """Test get quote."""
        ret, msg = quotes.get_random_quote()
        self.assertTrue(ret)
        self.assertTrue(isinstance(msg, str) or isinstance(msg, unicode))

    def test_console(self):
        """Test console."""
        console(["unit", "test"], format_type="quote")

    def test_start(self):
        """Test docopt."""
        start(test=True)


if __name__ == '__main__':
    unittest.main()
