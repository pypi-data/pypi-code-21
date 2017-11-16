import os
import unittest

import tecplot as tp
from tecplot.exception import *
from tecplot.constant import *

from ..sample_data import sample_data

class TestTextBox(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename, self.dataset = sample_data('2x2x3_overlap')
        frame = tp.active_frame()
        plot = frame.plot(PlotType.Cartesian3D)
        plot.vector.u_variable_index = 0
        plot.vector.v_variable_index = 1
        plot.vector.w_variable_index = 2
        self.box = plot.contour(0).legend.box

    def tearDown(self):
        os.remove(self.filename)

    def test_box_type(self):
        for val in TextBox:
            self.box.box_type = val
            self.assertEqual(self.box.box_type, val)
        with self.assertRaises(ValueError):
            self.box.box_type = "badtype"

    def test_color(self):
        for val in [Color.Red, Color.Blue]:
            self.box.color = val
            self.assertEqual(self.box.color, val)
        with self.assertRaises(ValueError):
            self.box.color = "badtype"

    def test_fill_color(self):
        for val in [Color.Magenta, Color.Cyan]:
            self.box.fill_color = val
            self.assertEqual(self.box.fill_color, val)
        with self.assertRaises(ValueError):
            self.box.fill_color = "badtype"

    def test_line_thickness(self):
        for val in [0.5,1,2]:
            self.box.line_thickness = val
            self.assertEqual(self.box.line_thickness, val)
        with self.assertRaises(ValueError):
            self.box.line_thickness = "badtype"
        with self.assertRaises(TecplotSystemError):
            self.box.line_thickness = -1
        with self.assertRaises(TecplotSystemError):
            self.box.line_thickness = 0

    def test_margin(self):
        for val in [0,0.5,1,2]:
            self.box.margin = val
            self.assertEqual(self.box.margin, val)
        with self.assertRaises(ValueError):
            self.box.margin = "badtype"
        with self.assertRaises(TecplotSystemError):
            self.box.margin = -1
