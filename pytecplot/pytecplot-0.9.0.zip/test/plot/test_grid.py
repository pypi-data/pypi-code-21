import numpy as np
import os
import random
import sys
import unittest

from os import path
from unittest.mock import patch, Mock

from test import patch_tecutil

import tecplot as tp
from tecplot.exception import *
from tecplot.constant import *
from tecplot.plot import *

from ..sample_data import sample_data


class TestGridArea(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename, ds = sample_data('xylines_poly')
        fr = tp.active_frame()
        fr.activate()
        plot = fr.plot(PlotType.PolarLine)
        plot.activate()
        self.grid = plot.axes.grid_area

    def tearDown(self):
        os.remove(self.filename)

    def test_filled(self):
        for val in [True, False, True]:
            self.grid.filled = val
            self.assertEqual(self.grid.filled, val)

    def test_fill_color(self):
        for val in [Color.Blue, Color.Red, Color.Black]:
            self.grid.fill_color = val
            self.assertEqual(self.grid.fill_color, val)
        with self.assertRaises(ValueError):
            self.grid.fill_color = 0.5

    def test_show_border(self):
        for val in [True, False, True]:
            self.grid.show_border = val
            self.assertEqual(self.grid.show_border, val)


class TestCartesian2DGridArea(TestGridArea):
    def setUp(self):
        tp.new_layout()
        self.filename, ds = sample_data('3x3x3_p')
        fr = tp.active_frame()
        fr.activate()
        plot = fr.plot(PlotType.Cartesian2D)
        plot.activate()
        self.grid = plot.axes.grid_area

    def tearDown(self):
        os.remove(self.filename)

    def test_border_color(self):
        for val in [Color.Blue, Color.Red, Color.Black]:
            self.grid.border_color = val
            self.assertEqual(self.grid.border_color, val)
        with self.assertRaises(ValueError):
            self.grid.border_color = 0.5

    def test_border_thickness(self):
        for val in [0.5, 1, 100]:
            self.grid.border_thickness = val
            self.assertAlmostEqual(self.grid.border_thickness, val)
        with self.assertRaises(ValueError):
            self.grid.border_thickness = 'badvalue'
        with self.assertRaises(TecplotSystemError):
            self.grid.border_thickness = 0
        with self.assertRaises(TecplotSystemError):
            self.grid.border_thickness = -1
        with self.assertRaises(TecplotSystemError):
            self.grid.border_thickness = 150


class TestCartesian3DGridArea(TestGridArea):
    def setUp(self):
        tp.new_layout()
        self.filename, ds = sample_data('3x3x3_p')
        fr = tp.active_frame()
        fr.activate()
        plot = fr.plot(PlotType.Cartesian3D)
        plot.activate()
        self.grid = plot.axes.grid_area

    def tearDown(self):
        os.remove(self.filename)

    def test_use_lighting_effect(self):
        for val in [True, False, True]:
            self.grid.use_lighting_effect = val
            self.assertEqual(self.grid.use_lighting_effect, val)


class TestPreciseGrid(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename, ds = sample_data('3x3x3_p')
        fr = tp.active_frame()
        fr.activate()
        plot = fr.plot(PlotType.Cartesian2D)
        plot.activate()
        self.grid = plot.axes.precise_grid

    def tearDown(self):
        os.remove(self.filename)

    def test_show(self):
        for val in [True, False, True]:
            self.grid.show = val
            self.assertEqual(self.grid.show, val)

    def test_size(self):
        for val in [0.5, 1]:
            self.grid.size = val
            self.assertAlmostEqual(self.grid.size, val)
        with self.assertRaises(ValueError):
            self.grid.size = 'badvalue'
        with self.assertRaises(TecplotSystemError):
            self.grid.size = 0
        with self.assertRaises(TecplotSystemError):
            self.grid.size = -1
        with self.assertRaises(TecplotSystemError):
            self.grid.size = 100

    def test_color(self):
        for val in [Color.Blue, Color.Red, Color.Black]:
            self.grid.color = val
            self.assertEqual(self.grid.color, val)
        with self.assertRaises(ValueError):
            self.grid.color = 0.5


class _TestGridLinesStyle(object):
    def test_show(self):
        for val in [True, False, True]:
            self.grid.show = val
            self.assertEqual(self.grid.show, val)

    def test_color(self):
        for val in [Color.Blue, Color.Red, Color.Black]:
            self.grid.color = val
            self.assertEqual(self.grid.color, val)
        with self.assertRaises(ValueError):
            self.grid.color = 0.5

    def test_line_thickness(self):
        for val in [0.5, 1, 100]:
            self.grid.line_thickness = val
            self.assertAlmostEqual(self.grid.line_thickness, val)
        with self.assertRaises(ValueError):
            self.grid.line_thickness = 'badvalue'
        with self.assertRaises(TecplotSystemError):
            self.grid.line_thickness = 0
        with self.assertRaises(TecplotSystemError):
            self.grid.line_thickness = -1
        with self.assertRaises(TecplotSystemError):
            self.grid.line_thickness = 150

    def test_line_pattern(self):
        for val in [LinePattern.Solid, LinePattern.Dashed, LinePattern.DashDot]:
            self.grid.line_pattern = val
            self.assertEqual(self.grid.line_pattern, val)
        with self.assertRaises(ValueError):
            self.grid.line_pattern = 0.5

    def test_pattern_length(self):
        for val in [0.5, 1, 100]:
            self.grid.pattern_length = val
            self.assertAlmostEqual(self.grid.pattern_length, val)
        with self.assertRaises(ValueError):
            self.grid.pattern_length = 'badvalue'
        with self.assertRaises(TecplotSystemError):
            self.grid.pattern_length = 0
        with self.assertRaises(TecplotSystemError):
            self.grid.pattern_length = -1
        with self.assertRaises(TecplotSystemError):
            self.grid.pattern_length = 150



class TestGridLines(_TestGridLinesStyle, unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename, ds = sample_data('3x3x3_p')
        fr = tp.active_frame()
        fr.activate()
        plot = fr.plot(PlotType.Cartesian3D)
        plot.activate()
        self.grid = plot.axes.x_axis.grid_lines

    def tearDown(self):
        os.remove(self.filename)

    def test_draw_last(self):
        with self.assertRaises(AttributeError):
            self.grid.draw_last

class TestGridLines2D(TestGridLines):
    def setUp(self):
        tp.new_layout()
        self.filename, ds = sample_data('xylines_poly')
        fr = tp.active_frame()
        fr.activate()
        plot = fr.plot(PlotType.XYLine)
        plot.activate()
        self.grid = plot.axes.x_axis(0).grid_lines

    def tearDown(self):
        os.remove(self.filename)

    def test_draw_last(self):
        for val in [True, False, True]:
            self.grid.draw_last = val
            self.assertEqual(self.grid.draw_last, val)


class TestMinorGridLines(_TestGridLinesStyle, unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename, ds = sample_data('3x3x3_p')
        fr = tp.active_frame()
        fr.activate()
        plot = fr.plot(PlotType.Cartesian3D)
        plot.activate()
        self.grid = plot.axes.x_axis.minor_grid_lines

    def tearDown(self):
        os.remove(self.filename)

    def test_draw_last(self):
        with self.assertRaises(AttributeError):
            self.grid.draw_last

class TestMinorGridLines2D(TestMinorGridLines):
    def setUp(self):
        tp.new_layout()
        self.filename, ds = sample_data('xylines_poly')
        fr = tp.active_frame()
        fr.activate()
        plot = fr.plot(PlotType.XYLine)
        plot.activate()
        self.grid = plot.axes.x_axis(0).minor_grid_lines

    def test_draw_last(self):
        for val in [True, False, True]:
            self.grid.draw_last = val
            self.assertEqual(self.grid.draw_last, val)


class TestPolarAngleGridLines(TestGridLines):
    def setUp(self):
        tp.new_layout()
        self.filename, ds = sample_data('xylines_poly')
        fr = tp.active_frame()
        fr.activate()
        plot = fr.plot(PlotType.PolarLine)
        plot.activate()
        self.grid = plot.axes.theta_axis.grid_lines

    def tearDown(self):
        os.remove(self.filename)

    def test_radial_cutoff(self):
        for val in [0, 0.5, 1, 100]:
            self.grid.radial_cutoff = val
            self.assertAlmostEqual(self.grid.radial_cutoff, val)
        with self.assertRaises(ValueError):
            self.grid.radial_cutoff = 'badvalue'
        with self.assertRaises(TecplotSystemError):
            self.grid.radial_cutoff = 101
        with self.assertRaises(TecplotSystemError):
            self.grid.radial_cutoff = -1

    def test_draw_last(self):
        for val in [True, False, True]:
            self.grid.draw_last = val
            self.assertEqual(self.grid.draw_last, val)


class TestPolarAngleMinorGridLines(TestMinorGridLines, TestPolarAngleGridLines):
    def setUp(self):
        tp.new_layout()
        self.filename, ds = sample_data('xylines_poly')
        fr = tp.active_frame()
        fr.activate()
        plot = fr.plot(PlotType.PolarLine)
        plot.activate()
        self.grid = plot.axes.theta_axis.minor_grid_lines

    def tearDown(self):
        os.remove(self.filename)

    def test_draw_last(self):
        for val in [True, False, True]:
            self.grid.draw_last = val
            self.assertEqual(self.grid.draw_last, val)

class TestMarkerGridLine(_TestGridLinesStyle, unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename, ds = sample_data('3x3x3_p')
        fr = tp.active_frame()
        fr.activate()
        plot = fr.plot(PlotType.Cartesian3D)
        plot.activate()
        self.grid = plot.axes.x_axis.marker_grid_line

    def tearDown(self):
        os.remove(self.filename)

    def test_position_by(self):
        for val in [PositionMarkerBy.Constant, PositionMarkerBy.SolutionTime]:
            self.grid.position_by = val
            self.assertEqual(self.grid.position_by, val)
        with self.assertRaises(ValueError):
            self.grid.position = 'badvalue'

    def test_position(self):
        self.grid.position_by = PositionMarkerBy.Constant
        for val in [-1, 0, 0.5, 1.0]:
            self.grid.position = val
            self.assertEqual(self.grid.position, val)
        with self.assertRaises(ValueError):
            self.grid.position = 'badvalue'

    def test_draw_last(self):
        with self.assertRaises(AttributeError):
            self.grid.draw_last


class TestMarkerGridLine2D(TestMarkerGridLine, TestGridLines2D):
    def setUp(self):
        tp.new_layout()
        self.filename, ds = sample_data('xylines_poly')
        fr = tp.active_frame()
        fr.activate()
        plot = fr.plot(PlotType.XYLine)
        plot.activate()
        self.grid = plot.axes.x_axis(0).marker_grid_line

    def tearDown(self):
        os.remove(self.filename)

    def test_draw_last(self):
        for val in [True, False, True]:
            self.grid.draw_last = val
            self.assertEqual(self.grid.draw_last, val)

if __name__ == '__main__':
    from .. import main
    main()
