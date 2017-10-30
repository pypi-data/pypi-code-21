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
test_xls
========

Unit tests for xls.py

"""


import os
import sys

try:
    import xlrd
except ImportError:
    xlrd = None

try:
    import xlwt
except ImportError:
    xlwt = None

import pytest

import wx
app = wx.App()

TESTPATH = os.sep.join(os.path.realpath(__file__).split(os.sep)[:-1]) + os.sep
sys.path.insert(0, TESTPATH)
sys.path.insert(0, TESTPATH + (os.sep + os.pardir) * 3)
sys.path.insert(0, TESTPATH + (os.sep + os.pardir) * 2)

from src.interfaces.xls import Xls
from src.lib.selection import Selection
from src.lib.testlib import params, pytest_generate_tests
from src.model.model import CodeArray
from src.sysvars import get_dpi, get_default_font

@pytest.mark.skipif(xlrd is None, reason="requires xlrd")
class TestXls(object):
    """Unit tests for Xls"""

    def setup_method(self, method):
        """Creates Xls class with code_array and temporary test.xls file"""

        # All data structures are initially empty
        # The test file xls_file has entries in each category

        self.top_window = wx.Frame(None, -1)
        wx.GetApp().SetTopWindow(self.top_window)

        self.code_array = CodeArray((1000, 100, 3))
        self.xls_infile = xlrd.open_workbook(TESTPATH + "xls_test1.xls",
                                             formatting_info=True)
        self.xls_outfile_path = TESTPATH + "xls_test2.xls"
        self.xls_in = Xls(self.code_array, self.xls_infile)

    def write_xls_out(self, xls, workbook, method_name, *args, **kwargs):
        """Helper that writes an xls file"""

        method = getattr(xls, method_name)
        method(*args, **kwargs)
        workbook.save(self.xls_outfile_path)

    def read_xls_out(self):
        """Returns string of xls_out content and removes xls_out"""

        out_workbook = xlrd.open_workbook(self.xls_outfile_path,
                                          formatting_info=True)

        # Clean up the test dir
        os.remove(self.xls_outfile_path)

        return out_workbook

    param_idx2colour = [
        {'idx': 0, 'res': (0, 0, 0)},
        {'idx': 1, 'res': (255, 255, 255)},
        {'idx': 2, 'res': (255, 0, 0)},
        {'idx': 3, 'res': (0, 255, 0)},
    ]

    @params(param_idx2colour)
    def test_idx2colour(self, idx, res):
        """Test idx2colour method"""

        assert self.xls_in.idx2colour(idx).Get() == res

    param_color2idx = [
        {'red': 0, 'green': 0, 'blue': 0, 'res': 0},
        {'red': 255, 'green': 255, 'blue': 255, 'res': 1},
        {'red': 255, 'green': 255, 'blue': 254, 'res': 1},
        {'red': 51, 'green': 52, 'blue': 51, 'res': 63},
    ]

    @params(param_color2idx)
    def test_color2idx(self, red, green, blue, res):
        """Test color2idx method"""

        assert self.xls_in.color2idx(red, green, blue) == res

    param_shape2xls = [
        {'tabs': 1, 'res': 1},
        {'tabs': 2, 'res': 2},
        {'tabs': 100, 'res': 100},
        {'tabs': 100000, 'res': 256},
    ]

    @params(param_shape2xls)
    @pytest.mark.skipif(xlwt is None, reason="requires xlwt")
    def test_shape2xls(self, tabs, res):
        """Test _shape2xls method"""

        self.code_array.dict_grid.shape = (99, 99, tabs)
        workbook = xlwt.Workbook()
        xls_out = Xls(self.code_array, workbook)
        self.write_xls_out(xls_out, workbook, "_shape2xls", [])
        workbook = self.read_xls_out()
        assert len(workbook.sheets()) == res

    def test_xls2shape(self):
        """Test _xls2shape method"""

        self.xls_in._xls2shape()
        assert self.code_array.dict_grid.shape == (19, 7, 3)

    param_code2xls = [
        {'code': [((0, 0, 0), "Test"), ], 'key': (0, 0, 0), 'val': "Test"},
        {'code': [((10, 1, 1), "Test"), ], 'key': (10, 1, 1), 'val': "Test"},
        {'code': [((1, 1, 0), "Test"), ], 'key': (0, 0, 0), 'val': ""},
    ]

    @params(param_code2xls)
    @pytest.mark.skipif(xlwt is None, reason="requires xlwt")
    def test_code2xls(self, key, val, code):
        """Test _code2xls method"""

        row, col, tab = key

        for __key, __val in code:
            self.code_array[__key] = __val
            self.code_array.shape = (1000, 100, 3)
        wb = xlwt.Workbook()
        xls_out = Xls(self.code_array, wb)
        worksheets = []
        xls_out._shape2xls(worksheets)
        self.write_xls_out(xls_out, wb, "_code2xls", worksheets)
        workbook = self.read_xls_out()

        worksheets = workbook.sheets()
        worksheet = worksheets[tab]
        assert worksheet.cell_value(row, col) == val

    param_xls2code = [
        {'key': (5, 2, 0), 'res': "34.234"},
        {'key': (6, 2, 0), 'res': "2.0"},
        {'key': (3, 4, 0), 'res': "Hi"},
    ]

    @params(param_xls2code)
    def test_xls2code(self, key, res):
        """Test _xls2code method"""

        worksheets = self.xls_in.workbook.sheet_names()

        for tab, worksheet_name in enumerate(worksheets):
            worksheet = self.xls_in.workbook.sheet_by_name(worksheet_name)
            self.xls_in._xls2code(worksheet, tab)

        assert self.xls_in.code_array(key) == res

    param_get_font = [
        {'pointsize': 100, 'fontweight': wx.NORMAL, "fontstyle": wx.ITALIC,
         'easyxf': 'font: bold off; font: italic on; font: height 2000'},
        {'pointsize': 10, 'fontweight': wx.BOLD, "fontstyle": wx.ITALIC,
         'easyxf': 'font: bold on; font: italic on; font: height 200'},
    ]

    @params(param_get_font)
    @pytest.mark.skipif(xlwt is None, reason="requires xlwt")
    def test_get_font(self, pointsize, fontweight, fontstyle, easyxf):
        """Test _get_font method"""

        pys_style = {
            'textfont': get_default_font().GetFaceName(),
            'pointsize': pointsize,
            'fontweight': fontweight,
            'fontstyle': fontstyle,
        }
        font = self.xls_in._get_font(pys_style)

        style = xlwt.easyxf(easyxf)

        assert font.bold == style.font.bold
        assert font.italic == style.font.italic
        assert font.height == style.font.height

    param_get_alignment = [
        {"justification": "left", "vertical_align": "top", "angle": 0,
         'easyxf': 'align: horz left; align: vert top; align: rota 0;'},
        {"justification": "right", "vertical_align": "bottom", "angle": 20,
         'easyxf': 'align: horz right; align: vert bottom; align: rota 20;'},
        {"justification": "right", "vertical_align": "bottom", "angle": -20,
         'easyxf': 'align: horz right; align: vert bottom; align: rota -20;'},
        {"justification": "center", "vertical_align": "middle", "angle": 30,
         'easyxf': 'align: horz center; align: vert center; align: rota 30;'},
    ]

    @params(param_get_alignment)
    @pytest.mark.skipif(xlwt is None, reason="requires xlwt")
    def test_get_alignment(self, justification, vertical_align, angle, easyxf):
        """Test _get_alignment method"""

        pys_style = {
            'justification': justification,
            'vertical_align': vertical_align,
            'angle': angle,
        }
        alignment = self.xls_in._get_alignment(pys_style)

        style = xlwt.easyxf(easyxf)

        assert alignment.horz == style.alignment.horz
        assert alignment.vert == style.alignment.vert
        assert alignment.rota == style.alignment.rota

    param_get_pattern = [
        {'bgcolor': wx.Colour(0, 0, 0).GetRGB(),
         'easyxf': 'pattern: fore_colour 0'},
        {'bgcolor': wx.Colour(255, 255, 0).GetRGB(),
         'easyxf': 'pattern: fore_colour 5'},
        {'bgcolor': wx.Colour(60, 10, 10).GetRGB(),
         'easyxf': 'pattern: fore_colour 59'},
    ]

    @params(param_get_pattern)
    @pytest.mark.skipif(xlwt is None, reason="requires xlwt")
    def test_get_pattern(self, bgcolor, easyxf):
        """Test _get_pattern method"""

        pys_style = {
            'bgcolor': bgcolor,
        }
        pattern = self.xls_in._get_pattern(pys_style)

        style = xlwt.easyxf(easyxf)

        assert pattern.pattern_fore_colour == style.pattern.pattern_fore_colour

    param_get_borders = [
        {'borderwidth_right': 0, 'borderwidth_bottom': 0,
         'bordercolor_right': wx.Colour(0, 0, 0).GetRGB(),
         'bordercolor_bottom': wx.Colour(0, 0, 0).GetRGB(),
         'easyxf': 'borders: right no_line; borders: bottom no_line; '
                   'borders: right_colour 0; borders: bottom_colour 0'},
        {'borderwidth_right': 1, 'borderwidth_bottom': 4,
         'bordercolor_right': wx.Colour(110, 0, 0).GetRGB(),
         'bordercolor_bottom': wx.Colour(0, 20, 210).GetRGB(),
         'easyxf': 'borders: right thin; borders: bottom medium; '
                   'borders: right_colour 16; borders: bottom_colour 4'},
    ]

    @params(param_get_borders)
    @pytest.mark.skipif(xlwt is None, reason="requires xlwt")
    def test_get_borders(self, borderwidth_right, borderwidth_bottom,
                         bordercolor_right, bordercolor_bottom, easyxf):
        """Test _get_borders method"""

        pys_style = {
            'borderwidth_right': borderwidth_right,
            'borderwidth_bottom': borderwidth_bottom,
            'bordercolor_right': bordercolor_right,
            'bordercolor_bottom': bordercolor_bottom,
        }
        borders = self.xls_in._get_borders(pys_style, pys_style, pys_style)

        style = xlwt.easyxf(easyxf)

        assert borders.right == style.borders.right
        assert borders.bottom == style.borders.bottom
        assert borders.right_colour == style.borders.right_colour
        assert borders.bottom_colour == style.borders.bottom_colour

    param_get_xfstyle = [
        {'key': (0, 0, 0), 'sec_key': 'pattern',
         'subsec_key': 'pattern_fore_colour',
         'style_key': 'bgcolor', 'val': wx.Colour(0, 0, 0).GetRGB(),
         'easyxf': 'pattern: fore_colour 0'},
        {'key': (10, 1, 0), 'sec_key': 'pattern',
         'subsec_key': 'pattern_fore_colour',
         'style_key': 'bgcolor', 'val': wx.Colour(0, 0, 0).GetRGB(),
         'easyxf': 'pattern: fore_colour 0'},
    ]

    @params(param_get_xfstyle)
    @pytest.mark.skipif(xlwt is None, reason="requires xlwt")
    def test_get_xfstyle(self, key, sec_key, subsec_key, style_key, val,
                         easyxf):
        """Test _get_xfstyle method"""

        row, col, tab = key

        pys_style = {style_key: val}

        dict_grid = self.code_array.dict_grid
        selection = Selection([], [], [], [], [(row, col)])
        dict_grid.cell_attributes.append((selection, tab, pys_style))

        xfstyle = self.xls_in._get_xfstyle([], key)

        style = xlwt.easyxf(easyxf)

        assert getattr(getattr(xfstyle, sec_key), subsec_key) == \
            getattr(getattr(style, sec_key), subsec_key)

    param_attributes2xls = [
        {'key': (14, 3, 0), 'attr': 'fontweight', 'val': 92},
        {'key': (14, 3, 0), 'attr': 'fontstyle', 'val': 90},
        {'key': (15, 3, 0), 'attr': 'fontstyle', 'val': 93},
        {'key': (16, 3, 0), 'attr': 'underline', 'val': True},
        {'key': (17, 3, 0), 'attr': 'textfont', 'val': "Serif"},
        {'key': (17, 3, 0), 'attr': 'pointsize', 'val': 20},
        {'key': (18, 3, 0), 'attr': 'borderwidth_bottom', 'val': 7},
        {'key': (18, 3, 0), 'attr': 'borderwidth_right', 'val': 7},
        {'key': (17, 3, 0), 'attr': 'borderwidth_bottom', 'val': 7},
        {'key': (18, 3, 0), 'attr': 'bgcolor', 'val': 52377},
    ]

    @params(param_attributes2xls)
    def test_xls2attributes(self, key, attr, val):
        """Test _xls2attributes method"""

        worksheet = self.xls_in.workbook.sheet_by_name("Sheet1")
        self.xls_in._xls2code(worksheet, 0)
        self.xls_in._xls2attributes(worksheet, 0)

        attrs = self.code_array.dict_grid.cell_attributes[key]

        assert attrs[attr] == val
#
#    param_cell_attribute_append = [
#        {'row': 0, 'tab': 0, 'height': 0.1, 'code': "0\t0\t0.1\n"},
#        {'row': 0, 'tab': 0, 'height': 0.0, 'code': "0\t0\t0.0\n"},
#        {'row': 10, 'tab': 0, 'height': 1.0, 'code': "10\t0\t1.0\n"},
#        {'row': 10, 'tab': 10, 'height': 1.0, 'code': "10\t10\t1.0\n"},
#        {'row': 10, 'tab': 10, 'height': 100.0, 'code': "10\t10\t100.0\n"},
#    ]
#

#

    def _hpixels_to_xlsheight(self, hpixels):
        """Returns xls height from hpixels"""

        hinches = float(hpixels) / get_dpi()[1]
        hpoints = hinches * 72.0
        xlsheight = hpoints * 20.0

        return xlsheight

    param_row_heights2xls = [
        {'row': 0, 'tab': 0, 'hpixels': 0.1},
        {'row': 0, 'tab': 0, 'hpixels': 0.0},
        {'row': 10, 'tab': 0, 'hpixels': 1.0},
        {'row': 10, 'tab': 10, 'hpixels': 1.0},
        {'row': 10, 'tab': 10, 'hpixels': 100.0},
    ]

    @params(param_row_heights2xls)
    @pytest.mark.skipif(xlwt is None, reason="requires xlwt")
    def test_row_heights2xls(self, row, tab, hpixels):
        """Test _row_heights2xls method"""

        self.code_array.shape = (1000, 100, 30)
        self.code_array.dict_grid.row_heights = {(row, tab): hpixels}

        wb = xlwt.Workbook()
        xls_out = Xls(self.code_array, wb)
        worksheets = []
        xls_out._shape2xls(worksheets)
        self.write_xls_out(xls_out, wb, "_row_heights2xls", worksheets)
        workbook = self.read_xls_out()

        worksheets = workbook.sheets()
        worksheet = worksheets[tab]

        xlsheight = self._hpixels_to_xlsheight(hpixels)

        assert worksheet.rowinfo_map[row].height == int(xlsheight)

    param_xls2row_heights = [
        {'row': 1, 'tab': 0, 'height': 44},
        {'row': 10, 'tab': 0, 'height': 45},
    ]

    @params(param_xls2row_heights)
    def test_xls2row_heights(self, row, tab, height):
        """Test _xls2row_heights method"""

        worksheet_names = self.xls_in.workbook.sheet_names()
        worksheet_name = worksheet_names[tab]
        worksheet = self.xls_in.workbook.sheet_by_name(worksheet_name)

        self.xls_in._xls2row_heights(worksheet, tab)
        res = self.code_array.dict_grid.row_heights[(row, tab)]
        assert int(res) == height

    param_pys_width2xls_width = [
        {'pys_width': 0},
        {'pys_width': 1},
        {'pys_width': 1.1},
        {'pys_width': 3},
        {'pys_width': 1141.1},
        {'pys_width': 0.0},
    ]

    @params(param_pys_width2xls_width)
    def test_pys_width2xls_width(self, pys_width):
        """Unit test for pys_width2xls_width and xls_width2pys_width

        Roundtrip test

        """

        wb = xlwt.Workbook()
        xls_out = Xls(self.code_array, wb)
        xls_width = xls_out.pys_width2xls_width(pys_width)
        roundtrip_width = xls_out.xls_width2pys_width(xls_width)

        assert round(pys_width) == round(roundtrip_width)

    param_col_widths2xls = [
        {'col': 0, 'tab': 0, 'width': 0.1},
        {'col': 0, 'tab': 0, 'width': 0.0},
        {'col': 10, 'tab': 0, 'width': 1.0},
        {'col': 10, 'tab': 10, 'width': 1.0},
        {'col': 10, 'tab': 10, 'width': 100.0},
    ]

    @params(param_col_widths2xls)
    @pytest.mark.skipif(xlwt is None, reason="requires xlwt")
    def test_col_widths2xls(self, col, tab, width):
        """Test _col_widths2xls method"""

        self.code_array.shape = (1000, 100, 30)
        self.code_array.dict_grid.col_widths = {(col, tab): width}

        wb = xlwt.Workbook()
        xls_out = Xls(self.code_array, wb)
        worksheets = []
        xls_out._shape2xls(worksheets)
        self.write_xls_out(xls_out, wb, "_col_widths2xls", worksheets)
        workbook = self.read_xls_out()

        points = xls_out.pys_width2xls_width(width)

        worksheets = workbook.sheets()
        worksheet = worksheets[tab]
        assert worksheet.colinfo_map[col].width == points

    param_xls2col_widths = [
        {'col': 4, 'tab': 0},
        {'col': 6, 'tab': 0},
    ]

    @params(param_xls2col_widths)
    def test_xls2col_widths(self, col, tab):
        """Test _xls2col_widths method"""

        worksheet_names = self.xls_in.workbook.sheet_names()
        worksheet_name = worksheet_names[tab]
        worksheet = self.xls_in.workbook.sheet_by_name(worksheet_name)

        self.xls_in._xls2col_widths(worksheet, tab)
        res = self.code_array.dict_grid.col_widths[(col, tab)]
        xls_width = worksheet.colinfo_map[col].width
        pys_width = self.xls_in.xls_width2pys_width(xls_width)
        assert round(res, 3) == round(pys_width, 3)

    @pytest.mark.skipif(xlwt is None, reason="requires xlwt")
    def test_from_code_array(self):
        """Test from_code_array method"""

        self.xls_in.to_code_array()

        wb = xlwt.Workbook()
        xls_out = Xls(self.code_array, wb)
        worksheets = []
        xls_out._shape2xls(worksheets)
        xls_out._code2xls(worksheets)
        xls_out._row_heights2xls(worksheets)

        self.write_xls_out(xls_out, wb, "_col_widths2xls", worksheets)

        new_code_array = CodeArray((1000, 100, 3))

        xls_outfile = xlrd.open_workbook(self.xls_outfile_path,
                                         formatting_info=True)
        xls_out = Xls(new_code_array, xls_outfile)

        xls_out.to_code_array()

        assert self.code_array.shape == new_code_array.shape
        assert self.code_array.macros == new_code_array.macros
        assert self.code_array.dict_grid == new_code_array.dict_grid
        # There may be additional standard heights in copy --> 1 way test
        for height in self.code_array.row_heights:
            assert height in new_code_array.row_heights
        assert self.code_array.col_widths == new_code_array.col_widths

        # Clean up the test dir
        os.remove(self.xls_outfile_path)

    def test_to_code_array(self):
        """Test to_code_array method"""

        self.xls_in.to_code_array()

        assert self.code_array((3, 4, 0)) == 'Hi'
        assert self.code_array((10, 6, 0)) == '465.0'
