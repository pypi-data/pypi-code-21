#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright Martin Manns
# Distributed under the terms of the GNU General Public License

# --------------------------------------------------------------------
# pyspread is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyspread is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyspread.  If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------


"""
test_selection
==============

Unit tests for selection.py

"""

import os
import sys

import wx
app = wx.App()

TESTPATH = os.sep.join(os.path.realpath(__file__).split(os.sep)[:-1]) + os.sep
sys.path.insert(0, TESTPATH)
sys.path.insert(0, TESTPATH + (os.sep + os.pardir) * 3)
sys.path.insert(0, TESTPATH + (os.sep + os.pardir) * 2)

from src.lib.testlib import params, pytest_generate_tests

from src.lib.selection import Selection

from src.gui._main_window import MainWindow


class TestSelection(object):
    """Unit tests for Selection"""

    def setup_method(self, method):
        self.main_window = MainWindow(None, -1)
        self.grid = self.main_window.grid

    param_test_nonzero = [
        {'sel': Selection([], [], [], [], [(32), (34)])},
        {'sel': Selection([], [], [], [], [(32, 53), (34, 56)])},
        {'sel': Selection([], [], [], [3], [])},
        {'sel': Selection([], [], [2], [], [])},
        {'sel': Selection([(1, 43)], [(2, 354)], [], [], [])},
    ]

    @params(param_test_nonzero)
    def test_nonzero(self, sel):
        """Unit test for __nonzero__"""

        assert sel

    def test_repr(self):
        """Unit test for __repr__"""

        selection = Selection([], [], [], [], [(32, 53), (34, 56)])
        assert str(selection) == \
            "Selection([], [], [], [], [(32, 53), (34, 56)])"

    param_test_eq = [
        {'sel1': Selection([], [], [], [], [(32, 53), (34, 56)]),
         'sel2': Selection([], [], [], [], [(32, 53), (34, 56)]),
         'res': True},
        {'sel1': Selection([], [], [], [], [(32, 53)]),
         'sel2': Selection([], [], [], [], [(32, 53), (34, 56)]),
         'res': False},
        {'sel1': Selection([], [], [], [], [(34, 56), (32, 53)]),
         'sel2': Selection([], [], [], [], [(32, 53), (34, 56)]),
         'res': False},
        {'sel1': Selection([], [], [3, 5], [1, 4], [(32, 53)]),
         'sel2': Selection([], [], [5, 3], [1, 4], [(32, 53)]),
         'res': False},
        {'sel1': Selection([], [], [3, 5], [1, 4], [(32, 2343)]),
         'sel2': Selection([], [], [5, 3], [1, 4], [(32, 53)]),
         'res': False},
        {'sel1': Selection([(2, 3), (9, 10)], [(5, 9), (100, 34)], [], [], []),
         'sel2': Selection([(2, 3), (9, 10)], [(5, 9), (100, 34)], [], [], []),
         'res': True},
        {'sel1': Selection([(9, 10), (2, 3)], [(100, 34), (5, 9)], [], [], []),
         'sel2': Selection([(2, 3), (9, 10)], [(5, 9), (100, 34)], [], [], []),
         'res': False},
    ]

    @params(param_test_eq)
    def test_eq(self, sel1, sel2, res):
        """Unit test for __eq__"""

        assert (sel1 == sel2) == res
        assert (sel2 == sel1) == res

    param_test_contains = [
        # Cell selections
        {'sel': Selection([], [], [], [], [(32, 53), (34, 56)]),
         'key': (32, 53), 'res': True},
        {'sel': Selection([], [], [], [], [(32, 53), (34, 56)]),
         'key': (23, 34534534), 'res': False},
        # Block selections
        {'sel': Selection([(4, 5)], [(100, 200)], [], [], []),
         'key': (4, 5), 'res': True},
        {'sel': Selection([(4, 5)], [(100, 200)], [], [], []),
         'key': (99, 199), 'res': True},
        {'sel': Selection([(4, 5)], [(100, 200)], [], [], []),
         'key': (100, 200), 'res': True},
        {'sel': Selection([(4, 5)], [(100, 200)], [], [], []),
         'key': (0, 0), 'res': False},
        {'sel': Selection([(4, 5)], [(100, 200)], [], [], []),
         'key': (0, 1), 'res': False},
        {'sel': Selection([(4, 5)], [(100, 200)], [], [], []),
         'key': (1, 0), 'res': False},
        {'sel': Selection([(4, 5)], [(100, 200)], [], [], []),
         'key': (4, 4), 'res': False},
        {'sel': Selection([(4, 5)], [(100, 200)], [], [], []),
         'key': (3, 5), 'res': False},
        {'sel': Selection([(4, 5)], [(100, 200)], [], [], []),
         'key': (100, 201), 'res': False},
        {'sel': Selection([(4, 5)], [(100, 200)], [], [], []),
         'key': (10**10, 10**10), 'res': False},
        # Row selection
        {'sel': Selection([], [], [3], [], []),
         'key': (0, 0), 'res': False},
        {'sel': Selection([], [], [3], [], []),
         'key': (3, 0), 'res': True},
        {'sel': Selection([], [], [3, 5], [], []),
         'key': (3, 0), 'res': True},
        {'sel': Selection([], [], [3, 5], [], []),
         'key': (5, 0), 'res': True},
        {'sel': Selection([], [], [3, 5], [], []),
         'key': (4, 0), 'res': False},
        # Column selection
        {'sel': Selection([], [], [], [2, 234, 434], []),
         'key': (234, 234), 'res': True},
        {'sel': Selection([], [], [], [2, 234, 434], []),
         'key': (234, 0), 'res': False},
        # Combinations
        {'sel': Selection([(0, 0)], [(90, 23)], [0], [0, 34], [((0, 0))]),
         'key': (0, 0), 'res': True},
    ]

    @params(param_test_contains)
    def test_contains(self, sel, key, res):
        """Unit test for __contains__

        Used in: ele in selection

        """

        assert (key in sel) == res

    param_test_add = [
        {'sel': Selection([], [], [], [], [(0, 0), (34, 56)]),
         'add': (4, 5),
         'res': Selection([], [], [], [], [(4, 5), (38, 61)])},
        {'sel': Selection([], [], [], [], [(0, 0), (34, 56)]),
         'add': (0, 0),
         'res': Selection([], [], [], [], [(0, 0), (34, 56)])},
        {'sel': Selection([], [], [], [], [(0, 0), (34, 56)]),
         'add': (-3, -24),
         'res': Selection([], [], [], [], [(-3, -24), (31, 32)])},
        {'sel': Selection([(2, 5)], [(4, 6)], [1], [0], [(0, 0), (34, 56)]),
         'add': (1, 0),
         'res': Selection([(3, 5)], [(5, 6)], [2], [0], [(1, 0), (35, 56)])},
    ]

    @params(param_test_add)
    def test_add(self, sel, add, res):
        """Unit test for __add__"""

        val = sel + add
        assert val == res

    param_test_and = [
        {'s1': Selection([], [], [], [], []),
         's2': Selection([], [], [], [], []),
         'res': Selection([], [], [], [], [])},
        {'s1': Selection([], [], [], [], [(0, 0)]),
         's2': Selection([], [], [], [], []),
         'res': Selection([], [], [], [], [])},
        {'s1': Selection([], [], [], [], [(0, 0)]),
         's2': Selection([], [], [], [], [(0, 0)]),
         'res': Selection([], [], [], [], [(0, 0)])},
        {'s1': Selection([], [], [], [], [(0, 0)]),
         's2': Selection([(0, 0)], [(5, 5)], [], [], []),
         'res': Selection([], [], [], [], [(0, 0)])},
        {'s1': Selection([(0, 0)], [(1000, 200)], [], [], []),
         's2': Selection([(0, 0)], [(1000, 200)], [], [], []),
         'res': Selection([(0, 0)], [(1000, 200)], [], [], [])},
        {'s1': Selection([(0, 0)], [(1000, 200)], [], [], []),
         's2': Selection([(1, 2)], [(10, 20)], [], [], []),
         'res': [(1, 2), (10, 20)]},
        {'s1': Selection([(0, 0)], [(1000, 200)], [], [], []),
         's2': Selection([], [], [(2)], [], []),
         'res': [(2, 3), (2, 0), (2, 200)]},
        {'s1': Selection([(0, 0)], [(1000, 200)], [], [], []),
         's2': Selection([], [], [], [(5)], []),
         'res': [(0, 5), (1000, 5)]},
    ]

    @params(param_test_and)
    def test_and(self, s1, s2, res):
        """Unit test for __and__"""

        s1_and_s2 = s1 & s2
        if type(res) is type([]):
            for cell in res:
                assert cell in s1_and_s2
        else:
            assert s1_and_s2 == res

    param_test_insert = [
        {'sel': Selection([], [], [2], [], []),
         'point': 1, 'number': 10, 'axis': 0,
         'res': Selection([], [], [12], [], [])},
        {'sel': Selection([], [], [], [], [(234, 23)]),
         'point': 20, 'number': 4, 'axis': 1,
         'res': Selection([], [], [], [], [(234, 27)])},
        {'sel': Selection([], [], [21], [33, 44], [(234, 23)]),
         'point': 40, 'number': 4, 'axis': 1,
         'res': Selection([], [], [21], [33, 48], [(234, 23)])},
    ]

    @params(param_test_insert)
    def test_insert(self, sel, point, number, axis, res):
        """Unit test for insert"""

        sel.insert(point, number, axis)
        assert sel == res

    param_test_get_bbox = [
        {'sel': Selection([], [], [], [], [(32, 53), (34, 56)]),
         'res': ((32, 53), (34, 56))},
        {'sel': Selection([(4, 5)], [(100, 200)], [], [], []),
         'res': ((4, 5), (100, 200))},
    ]

    @params(param_test_get_bbox)
    def test_get_bbox(self, sel, res):
        """Unit test for get_bbox"""

        assert sel.get_bbox() == res

    param_get_access_string = [
        {'sel': Selection([], [], [], [], [(32, 53), (34, 56)]),
         'shape': (1000, 100, 3), 'table': 0,
         'res': "[S[key] for key in [(32, 53, 0)] + [(34, 56, 0)] "
                "if S[key] is not None]"},
        {'sel': Selection([], [], [4, 5], [53], []),
         'shape': (1000, 100, 3), 'table': 2,
         'res': "[S[key] for key in [(4, c, 2) for c in xrange(100)] + "
                "[(5, c, 2) for c in xrange(100)] + [(r, 53, 2) for r in "
                "xrange(1000)] if S[key] is not None]"},
        {'sel': Selection([(0, 0), (2, 2)], [(1, 1), (7, 5)], [], [], []),
         'shape': (1000, 100, 3), 'table': 0,
         'res': "[S[key] for key in [(r, c, 0) for r in xrange(0, 2) for c in "
                "xrange(0, 2)] + [(r, c, 0) for r in xrange(2, 8) for c in "
                "xrange(2, 6)] if S[key] is not None]"},
    ]

    @params(param_get_access_string)
    def test_get_access_string(self, sel, shape, table, res):
        """Unit test for get_access_string"""

        assert sel.get_access_string(shape, table) == res

    param_test_shifted = [
        {'sel': Selection([], [], [], [], [(32, 53), (34, 56)]),
         'rows': 0, 'cols': 0,
         'res': Selection([], [], [], [], [(32, 53), (34, 56)])},
        {'sel': Selection([], [], [], [], [(32, 53), (34, 56)]),
         'rows': 1, 'cols': 1,
         'res': Selection([], [], [], [], [(33, 54), (35, 57)])},
        {'sel': Selection([], [], [], [], [(32, 53), (34, 56)]),
         'rows': -1, 'cols': 0,
         'res': Selection([], [], [], [], [(31, 53), (33, 56)])},
        {'sel': Selection([], [], [], [], [(32, 53), (34, 56)]),
         'rows': -1, 'cols': -1,
         'res': Selection([], [], [], [], [(31, 52), (33, 55)])},
        {'sel': Selection([], [], [], [], [(32, 53), (34, 56)]),
         'rows': -1, 'cols': 1,
         'res': Selection([], [], [], [], [(31, 54), (33, 57)])},
        {'sel': Selection([], [], [], [], [(32, 53), (34, 56)]),
         'rows': -100, 'cols': 100,
         'res': Selection([], [], [], [], [(-68, 153), (-66, 156)])},
        {'sel': Selection([(0, 0), (1, 1)], [(10, 10), (50, 50)], [], [], []),
         'rows': 1, 'cols': 0,
         'res': Selection([(1, 0), (2, 1)], [(11, 10), (51, 50)], [], [], [])},
        {'sel': Selection([], [], [1, 4, 6], [3, 4], []),
         'rows': 2, 'cols': 1,
         'res': Selection([], [], [3, 6, 8], [4, 5], [])},
    ]

    @params(param_test_shifted)
    def test_shifted(self, sel, rows, cols, res):
        """Unit test for shifted"""

        assert sel.shifted(rows, cols) == res

    param_test_grid_select = [
        {'sel': Selection([], [], [], [], [(1, 0), (2, 0)]),
         'key': (1, 0), 'res': True},
        {'sel': Selection([], [], [], [], [(1, 0), (2, 0)]),
         'key': (0, 0), 'res': False},
        {'sel': Selection([], [], [1, 2], [], []),
         'key': (0, 0), 'res': False},
        {'sel': Selection([], [], [1, 2], [], []),
         'key': (1, 0), 'res': True},
        {'sel': Selection([], [], [], [3], []),
         'key': (0, 3), 'res': True},
        {'sel': Selection([], [], [], [3], []),
         'key': (0, 0), 'res': False},
        {'sel': Selection([(0, 0)], [(2, 2)], [], [], []),
         'key': (1, 1), 'res': True},
    ]

    @params(param_test_grid_select)
    def test_grid_select(self, sel, key, res):
        """Unit test for grid_select"""

        sel.grid_select(self.grid)
        assert self.grid.IsInSelection(*key) == res

