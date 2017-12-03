from __future__ import division, absolute_import, print_function

import unittest
import pytest


class TestRegression(unittest.TestCase):
    def test_numeric_random(self, level=1):
        """Ticket #552"""
        from oldnumeric.random_array import randint
        randint(0, 50, [2, 3])

    @pytest.mark.xfail
    def test_mlab_import(self):
        """gh-3803"""
        try:
            from oldnumeric import mlab
            import oldnumeric.mlab as mlab
        except:
            raise AssertionError("mlab import failed")

