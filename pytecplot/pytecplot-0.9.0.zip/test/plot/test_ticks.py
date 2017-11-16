import os
import unittest

from tempfile import NamedTemporaryFile

from test import patch_tecutil

import tecplot as tp
from tecplot.exception import *
from tecplot.constant import *
from tecplot.plot import *
from tecplot.text import *

from ..sample_data import sample_data


class TestTicks(object):
    def test_show(self):
        for val in [True,False,True]:
            self.ticks.show = val
            self.assertEqual(self.ticks.show, val)

    def test_direction(self):
        for val in [TickDirection.In, TickDirection.Out,
                    TickDirection.Centered]:
            self.ticks.direction = val
            self.assertEqual(self.ticks.direction, val)
        with self.assertRaises(ValueError):
            self.ticks.direction = 0.5

    def test_length(self):
        for val in [0,0.5,1,100]:
            self.ticks.length = val
            self.assertEqual(self.ticks.length, val)
        with self.assertRaises(ValueError):
            self.ticks.length = 'badvalue'
        with self.assertRaises(TecplotSystemError):
            self.ticks.length = -1
        with self.assertRaises(TecplotSystemError):
            self.ticks.length = 150

    def test_line_thickness(self):
        for val in [0.5,1,100]:
            self.ticks.line_thickness = val
            self.assertEqual(self.ticks.line_thickness, val)
        with self.assertRaises(ValueError):
            self.ticks.line_thickness = 'badvalue'
        with self.assertRaises(TecplotSystemError):
            self.ticks.line_thickness = -1
        with self.assertRaises(TecplotSystemError):
            self.ticks.line_thickness = 0

    def test_minor_num_ticks(self):
        for val in [0,1,2,100]:
            self.ticks.minor_num_ticks = val
            self.assertEqual(self.ticks.minor_num_ticks, val)
        with self.assertRaises(ValueError):
            self.ticks.minor_num_ticks = 'badvalue'
        with self.assertRaises(TecplotSystemError):
            self.ticks.minor_num_ticks = -1

    def test_minor_minor_length(self):
        for val in [0,0.5,1,100]:
            self.ticks.minor_length = val
            self.assertEqual(self.ticks.minor_length, val)
        with self.assertRaises(ValueError):
            self.ticks.minor_length = 'badvalue'
        with self.assertRaises(TecplotSystemError):
            self.ticks.minor_length = -1
        with self.assertRaises(TecplotSystemError):
            self.ticks.minor_length = 150

    def test_minor_line_thickness(self):
        for val in [0.5,1,100]:
            self.ticks.minor_line_thickness = val
            self.assertEqual(self.ticks.minor_line_thickness, val)
        with self.assertRaises(ValueError):
            self.ticks.minor_line_thickness = 'badvalue'
        with self.assertRaises(TecplotSystemError):
            self.ticks.minor_line_thickness = -1
        with self.assertRaises(TecplotSystemError):
            self.ticks.minor_line_thickness = 0

    def test_auto_spacing(self):
        for val in [True, False, True]:
            self.ticks.auto_spacing = val
            self.assertAlmostEqual(self.ticks.auto_spacing, val)

    def test_spacing(self):
        self.ticks.auto_spacing = False
        self.ticks.axis.min = 0
        self.ticks.axis.max = 4
        for val in [0.5, 1, 2]:
            self.ticks.spacing = val
            self.assertAlmostEqual(self.ticks.spacing, val)
        with self.assertRaises(ValueError):
            self.ticks.spacing = 'badvalue'
        with self.assertRaises(TecplotSystemError):
            self.ticks.spacing = -1
        with self.assertRaises(TecplotSystemError):
            self.ticks.spacing = 0
        with self.assertRaises(TecplotSystemError):
            self.ticks.spacing = 100

    def test_spacing_anchor(self):
        for val in [-100,-1,-0.5,0,0.5,1,100]:
            self.ticks.spacing_anchor = val
            self.assertAlmostEqual(self.ticks.spacing_anchor, val)
        with self.assertRaises(ValueError):
            self.ticks.spacing_anchor = 'badvalue'


class TestTicks2D(unittest.TestCase, TestTicks):
    def setUp(self):
        tp.new_layout()
        self.filename,ds = sample_data('xylines_poly')
        fr = tp.active_frame()
        fr.activate()
        plot = fr.plot(PlotType.XYLine)
        plot.activate()
        self.ticks = plot.axes.x_axis(0).ticks

    def tearDown(self):
        os.remove(self.filename)

    def test_type(self):
        self.assertIsInstance(self.ticks, Ticks2D)

    def test_show_on_border_min(self):
        for val in [True,False,True]:
            self.ticks.show_on_border_min = val
            self.assertEqual(self.ticks.show_on_border_min, val)

    def test_show_on_border_max(self):
        for val in [True,False,True]:
            self.ticks.show_on_border_max = val
            self.assertEqual(self.ticks.show_on_border_max, val)


class TestRadialTicks(TestTicks2D):
    def setUp(self):
        tp.new_layout()
        self.filename,ds = sample_data('xylines_poly')
        fr = tp.active_frame()
        fr.activate()
        plot = fr.plot(PlotType.PolarLine)
        plot.activate()
        self.ticks = plot.axes.r_axis.ticks

    def tearDown(self):
        os.remove(self.filename)

    def test_show_on_all_radial_axes(self):
        for val in [True,False,True]:
            self.ticks.show_on_all_radial_axes = val
            self.assertEqual(self.ticks.show_on_all_radial_axes, val)


class TestTicks3D(unittest.TestCase, TestTicks):
    def setUp(self):
        tp.new_layout()
        self.filename,ds = sample_data('3x3x3_p')
        fr = tp.active_frame()
        fr.activate()
        plot = fr.plot(PlotType.Cartesian3D)
        plot.activate()
        self.ticks = plot.axes.x_axis.ticks

    def tearDown(self):
        os.remove(self.filename)

    def test_type(self):
        self.assertIsInstance(self.ticks, Ticks3D)

    def test_show_on_opposite_edge(self):
        for val in [True,False,True]:
            self.ticks.show_on_opposite_edge = val
            self.assertEqual(self.ticks.show_on_opposite_edge, val)


class TestTickLabels(object):
    def test_show(self):
        for val in [True,False,True]:
            self.labels.show = val
            self.assertEqual(self.labels.show, val)

    def test_alignment(self):
        for val in [LabelAlignment.ByAngle, LabelAlignment.AlongAxis,
                    LabelAlignment.PerpendicularToAxis]:
            self.labels.alignment = val
            self.assertAlmostEqual(self.labels.alignment, val)
        with self.assertRaises(ValueError):
            self.labels.alignment = 'badvalue'

    def test_angle(self):
        for val in [-100,-1,-0.5,0,0.5,1,100]:
            self.labels.angle = val
            self.assertAlmostEqual(self.labels.angle, val)
        with self.assertRaises(ValueError):
            self.labels.angle = 'badvalue'

    def test_color(self):
        for val in [Color.Blue, Color.Red, Color.Black]:
            self.labels.color = val
            self.assertEqual(self.labels.color, val)
        with self.assertRaises(ValueError):
            self.labels.color = 'badvalue'
        with self.assertRaises(ValueError):
            self.labels.color = 0.5

    def test_offset(self):
        for val in [-100,-1,-0.5,0,0.5,1,100]:
            self.labels.offset = val
            self.assertAlmostEqual(self.labels.offset, val)
        with self.assertRaises(ValueError):
            self.labels.offset = 'badvalue'

    def test_step(self):
        for val in [1,2,10]:
            self.labels.step = val
            self.assertAlmostEqual(self.labels.step, val)
        with self.assertRaises(ValueError):
            self.labels.step = 'badvalue'
        with self.assertRaises(TecplotSystemError):
            self.labels.step = -1
        with self.assertRaises(TecplotSystemError):
            self.labels.step = 0

    def test_format(self):
        self.assertIsInstance(self.labels.format, LabelFormat)

    def test_font(self):
        self.assertIsInstance(self.labels.font, Font)


class TestTickLabels2D(unittest.TestCase, TestTickLabels):
    def setUp(self):
        tp.new_layout()
        self.filename,ds = sample_data('xylines_poly')
        fr = tp.active_frame()
        fr.activate()
        plot = fr.plot(PlotType.XYLine)
        plot.activate()
        self.labels = plot.axes.x_axis(0).tick_labels

    def tearDown(self):
        os.remove(self.filename)

    def test_type(self):
        self.assertIsInstance(self.labels, TickLabels2D)

    def test_show_on_border_min(self):
        for val in [True,False,True]:
            self.labels.show_on_border_min = val
            self.assertEqual(self.labels.show_on_border_min, val)

    def test_show_on_border_max(self):
        for val in [True,False,True]:
            self.labels.show_on_border_max = val
            self.assertEqual(self.labels.show_on_border_max, val)

    def test_show_at_axis_intersection(self):
        for val in [True,False,True]:
            self.labels.show_at_axis_intersection = val
            self.assertEqual(self.labels.show_at_axis_intersection, val)

    def test_transparent_background(self):
        for val in [True,False,True]:
            self.labels.transparent_background = val
            self.assertEqual(self.labels.transparent_background, val)


class TestRadialTickLabels(TestTickLabels2D):
    def setUp(self):
        tp.new_layout()
        self.filename,ds = sample_data('xylines_poly')
        fr = tp.active_frame()
        fr.activate()
        plot = fr.plot(PlotType.PolarLine)
        plot.activate()
        self.labels = plot.axes.r_axis.tick_labels

    def tearDown(self):
        os.remove(self.filename)

    def test_show_on_all_radial_axes(self):
        for val in [True,False,True]:
            self.labels.show_on_all_radial_axes = val
            self.assertEqual(self.labels.show_on_all_radial_axes, val)


class TestTickLabels3D(unittest.TestCase, TestTickLabels):
    def setUp(self):
        tp.new_layout()
        self.filename,ds = sample_data('3x3x3_p')
        fr = tp.active_frame()
        fr.activate()
        plot = fr.plot(PlotType.Cartesian3D)
        plot.activate()
        self.labels = plot.axes.x_axis.tick_labels

    def tearDown(self):
        os.remove(self.filename)

    def test_type(self):
        self.assertIsInstance(self.labels, TickLabels3D)

    def test_show_on_opposite_edge(self):
        for val in [True,False,True]:
            self.labels.show_on_opposite_edge = val
            self.assertEqual(self.labels.show_on_opposite_edge, val)


if __name__ == '__main__':
    from .. import main
    main()
