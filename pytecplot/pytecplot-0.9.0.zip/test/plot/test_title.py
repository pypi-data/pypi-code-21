import os
import unittest

import tecplot as tp
from tecplot.exception import *
from tecplot.constant import *
from tecplot import text


from ..sample_data import sample_data


class _TestAxisTitle(object):
    def test_text(self):
        for val in ['aa', '0', 0, 3.14, None]:
            self.title.text = val
            self.assertEqual(self.title.text, str(val))

    def test_show(self):
        for val in [True,False,True]:
            self.title.show = val
            self.assertEqual(self.title.show, val)

    def test_position(self):
        for val in [0,0.5,1,100]:
            self.title.position = val
            self.assertEqual(self.title.position, val)
        with self.assertRaises(ValueError):
            self.title.position = 'badvalue'
        with self.assertRaises(TecplotSystemError):
            self.title.position = -1
        with self.assertRaises(TecplotSystemError):
            self.title.position = 150

    def test_color(self):
        for val in [Color.Blue, Color.Red, Color.Black]:
            self.title.color = val
            self.assertEqual(self.title.color, val)
        with self.assertRaises(ValueError):
            self.title.color = 'badvalue'
        with self.assertRaises(ValueError):
            self.title.color = 0.5

    def test_offset(self):
        for val in [-100,-1,0,0.5,1,100]:
            self.title.offset = val
            self.assertEqual(self.title.offset, val)
        with self.assertRaises(ValueError):
            self.title.offset = 'badvalue'
        with self.assertRaises(TecplotSystemError):
            self.title.offset = 150

    def test_font(self):
        self.assertIsInstance(self.title.font, text.Font)


class _TestAxis3DTitle(_TestAxisTitle):
    def test_show_on_opposite_edge(self):
        for val in [True,False,True]:
            self.title.show_on_opposite_edge = val
            self.assertEqual(self.title.show_on_opposite_edge, val)


class _TestDataAxisTitle(_TestAxisTitle):
    def test_title_mode(self):
        for val in [AxisTitleMode.UseText, AxisTitleMode.UseVarName]:
            self.title.title_mode = val
            self.assertEqual(self.title.title_mode, val)
        with self.assertRaises(ValueError):
            self.title.title_mode = 'badvalue'
        with self.assertRaises(ValueError):
            self.title.title_mode = 0.5
        if __debug__:
            with self.assertRaises(TecplotLogicError):
                self.title.title_mode = AxisTitleMode.NoTitle

    def test_text(self):
        for val in ['aa', '0', 0, 3.14]:
            self.title.text = val
            self.assertEqual(self.title.text, str(val))


class TestAxis2DTitle(unittest.TestCase, _TestAxisTitle):
    def setUp(self):
        tp.new_layout()
        plot = tp.active_frame().plot(PlotType.Sketch)
        plot.activate()
        self.title = plot.axes.x_axis.title

    def test_show_on_border_min(self):
        for val in [True,False,True]:
            self.title.show_on_border_min = val
            self.assertEqual(self.title.show_on_border_min, val)

    def test_show_on_border_max(self):
        for val in [True,False,True]:
            self.title.show_on_border_max = val
            self.assertEqual(self.title.show_on_border_max, val)


class TestDataAxis2DTitle(_TestDataAxisTitle, TestAxis2DTitle):
    def setUp(self):
        tp.new_layout()
        self.filename,ds = sample_data('xylines_poly')
        fr = tp.active_frame()
        fr.activate()
        plot = fr.plot(PlotType.XYLine)
        plot.activate()
        self.title = plot.axes.x_axis(0).title

    def tearDown(self):
        os.remove(self.filename)


class TestDataAxis3DTitle(unittest.TestCase, _TestDataAxisTitle, _TestAxis3DTitle):
    def setUp(self):
        tp.new_layout()
        self.filename,ds = sample_data('3x3x3_p')
        fr = tp.active_frame()
        fr.activate()
        plot = fr.plot(PlotType.Cartesian3D)
        plot.activate()
        self.title = plot.axes.x_axis.title

    def tearDown(self):
        os.remove(self.filename)


class TestRadialAxisTitle(TestDataAxis2DTitle):
    def setUp(self):
        tp.new_layout()
        self.filename,ds = sample_data('xylines_poly')
        fr = tp.active_frame()
        fr.activate()
        plot = fr.plot(PlotType.PolarLine)
        plot.activate()
        self.title = plot.axes.r_axis.title

    def tearDown(self):
        os.remove(self.filename)

    def test_show_on_all_radial_axes(self):
        for val in [True,False,True]:
            self.title.show_on_all_radial_axes = val
            self.assertEqual(self.title.show_on_all_radial_axes, val)


if __name__ == '__main__':
    from .. import main
    main()
