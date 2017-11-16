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
from tecplot.data.operate import execute_equation
from tecplot.plot import *
from tecplot.legend import ContourLegend, LineLegend
from tecplot.tecutil import IndexRange

from ..sample_data import sample_data, loaded_sample_data


class TestSketchAxes(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        fr = tp.active_frame()
        fr.activate()
        ds = fr.dataset
        xvar = ds.add_variable('X')
        z = ds.add_ordered_zone('Zone', (2,))
        xx = np.linspace(-1,1,2)
        z.values('X')[:] = xx
        plot = fr.plot(PlotType.Sketch)
        plot.activate()
        self.axes = plot.axes

    def test_eq(self):
        self.assertTrue(self.axes == tp.active_frame().plot().axes)
        self.assertFalse(self.axes != tp.active_frame().plot().axes)
        self.assertTrue(self.axes != tp.active_frame().plot())

    def test_auto_adjust_ranges(self):
        for val in [True,False,True]:
            self.axes.auto_adjust_ranges = val
            self.assertEqual(self.axes.auto_adjust_ranges, val)

    def test_axis_mode(self):
        for val in [AxisMode.Independent, AxisMode.XYDependent,
                    AxisMode.Independent]:
            self.axes.axis_mode = val
            self.assertEqual(self.axes.axis_mode, val)
        with self.assertRaises(ValueError):
            self.axes.axis_mode = 0.5
        with self.assertRaises(TecplotSystemError):
            self.axes.axis_mode = AxisMode.XYZDependent

    def test_preserve_scale(self):
        for val in [True,False,True]:
            self.axes.preserve_scale = val
            self.assertEqual(self.axes.preserve_scale, val)

    def test_xy_ratio(self):
        for val in [0.5,1,2,100]:
            self.axes.xy_ratio = val
            self.assertEqual(self.axes.xy_ratio, val)
        with self.assertRaises(ValueError):
            self.axes.xy_ratio = 'badvalue'
        with self.assertRaises(TecplotSystemError):
            self.axes.xy_ratio = 0
        with self.assertRaises(TecplotSystemError):
            self.axes.xy_ratio = -1

    def test_subclasses(self):
        self.assertIsInstance(self.axes, SketchAxes)
        self.assertIsInstance(self.axes.grid_area   , GridArea)
        self.assertIsInstance(self.axes.precise_grid, PreciseGrid)
        self.assertIsInstance(self.axes.viewport    , Cartesian2DViewport)
        self.assertIsInstance(self.axes.x_axis      , SketchAxis)
        self.assertIsInstance(self.axes.y_axis      , SketchAxis)

    def test_iter(self):
        for ax, n in zip(self.axes, ('X', 'Y')):
            self.assertIsInstance(ax, SketchAxis)
            self.assertEqual(ax._sv_name, n)
        self.assertEqual(iter(self.axes).next()._sv_name, 'X')


class TestCartesian2DFieldAxes(TestSketchAxes):
    def setUp(self):
        tp.new_layout()
        self.filename,ds = sample_data('3x3x3_p')
        fr = tp.active_frame()
        fr.activate()
        plot = fr.plot(PlotType.Cartesian2D)
        plot.activate()
        self.axes = plot.axes

    def tearDown(self):
        os.remove(self.filename)

    def test_axis_mode(self):
        for val in [AxisMode.Independent, AxisMode.XYDependent,
                    AxisMode.Independent]:
            self.axes.axis_mode = val
            self.assertEqual(self.axes.axis_mode, val)
        with self.assertRaises(ValueError):
            self.axes.axis_mode = 0.5
        with self.assertRaises(TecplotSystemError):
            self.axes.axis_mode = AxisMode.XYZDependent

    def test_subclasses(self):
        self.assertIsInstance(self.axes, Cartesian2DFieldAxes)
        self.assertIsInstance(self.axes.grid_area   , GridArea)
        self.assertIsInstance(self.axes.precise_grid, PreciseGrid)
        self.assertIsInstance(self.axes.viewport    , Cartesian2DViewport)
        self.assertIsInstance(self.axes.x_axis      , Cartesian2DFieldAxis)
        self.assertIsInstance(self.axes.y_axis      , Cartesian2DFieldAxis)

    def test_iter(self):
        for ax, n in zip(self.axes, ('X', 'Y')):
            self.assertIsInstance(ax, Cartesian2DFieldAxis)
            self.assertEqual(ax._sv_name, n)


class TestCartesian3DFieldAxes(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename,ds = sample_data('3x3x3_p')
        fr = tp.active_frame()
        fr.activate()
        plot = fr.plot(PlotType.Cartesian3D)
        plot.activate()
        self.axes = plot.axes

    def tearDown(self):
        os.remove(self.filename)

    def test_axis_mode(self):
        for val in [AxisMode.Independent, AxisMode.XYDependent,
                    AxisMode.XYZDependent, AxisMode.Independent]:
            self.axes.axis_mode = val
            self.assertEqual(self.axes.axis_mode, val)
        with self.assertRaises(ValueError):
            self.axes.axis_mode = 0.5

    def test_preserve_scale(self):
        for val in [True,False,True]:
            self.axes.preserve_scale = val
            self.assertEqual(self.axes.preserve_scale, val)

    def test_xy_ratio(self):
        for val in [-1,-0.5,0.5,1,2,100]:
            self.axes.xy_ratio = val
            self.assertEqual(self.axes.xy_ratio, val)
        with self.assertRaises(ValueError):
            self.axes.xy_ratio = 'badvalue'
        with self.assertRaises(TecplotSystemError):
            self.axes.xy_ratio = 0

    def test_xz_ratio(self):
        for val in [-1,-0.5,0.5,1,2,100]:
            self.axes.xz_ratio = val
            self.assertEqual(self.axes.xz_ratio, val)
        with self.assertRaises(ValueError):
            self.axes.xz_ratio = 'badvalue'
        with self.assertRaises(TecplotSystemError):
            self.axes.xz_ratio = 0

    def test_aspect_ratio_limit(self):
        for val in [1,2,100]:
            self.axes.aspect_ratio_limit = val
            self.assertEqual(self.axes.aspect_ratio_limit, val)
        with self.assertRaises(ValueError):
            self.axes.aspect_ratio_limit = 'badvalue'
        with self.assertRaises(TecplotSystemError):
            self.axes.aspect_ratio_limit = 0
        with self.assertRaises(TecplotSystemError):
            self.axes.aspect_ratio_limit = 0.5
        with self.assertRaises(TecplotSystemError):
            self.axes.aspect_ratio_limit = -1

    def test_aspect_ratio_reset(self):
        for val in [1,2,100]:
            self.axes.aspect_ratio_reset = val
            self.assertEqual(self.axes.aspect_ratio_reset, val)
        with self.assertRaises(ValueError):
            self.axes.aspect_ratio_reset = 'badvalue'
        with self.assertRaises(TecplotSystemError):
            self.axes.aspect_ratio_reset = 0
        with self.assertRaises(TecplotSystemError):
            self.axes.aspect_ratio_reset = 0.5
        with self.assertRaises(TecplotSystemError):
            self.axes.aspect_ratio_reset = -1

    def test_range_aspect_ratio_limit(self):
        for val in [1,2,100]:
            self.axes.range_aspect_ratio_limit = val
            self.assertEqual(self.axes.range_aspect_ratio_limit, val)
        with self.assertRaises(ValueError):
            self.axes.range_aspect_ratio_limit = 'badvalue'
        with self.assertRaises(TecplotSystemError):
            self.axes.range_aspect_ratio_limit = 0
        with self.assertRaises(TecplotSystemError):
            self.axes.range_aspect_ratio_limit = 0.5
        with self.assertRaises(TecplotSystemError):
            self.axes.range_aspect_ratio_limit = -1

    def test_range_aspect_ratio_reset(self):
        for val in [1,2,100]:
            self.axes.range_aspect_ratio_reset = val
            self.assertEqual(self.axes.range_aspect_ratio_reset, val)
        with self.assertRaises(ValueError):
            self.axes.range_aspect_ratio_reset = 'badvalue'
        with self.assertRaises(TecplotSystemError):
            self.axes.range_aspect_ratio_reset = 0
        with self.assertRaises(TecplotSystemError):
            self.axes.range_aspect_ratio_reset = 0.5
        with self.assertRaises(TecplotSystemError):
            self.axes.range_aspect_ratio_reset = -1

    def test_auto_edge_assignment(self):
        for val in [True,False,True]:
            self.axes.auto_edge_assignment = val
            self.assertEqual(self.axes.auto_edge_assignment, val)

    def test_reset_scale(self):
        self.axes.aspect_ratio_limit = 1
        self.axes.aspect_ratio_reset = 1
        self.axes.range_aspect_ratio_limit = 1
        self.axes.range_aspect_ratio_reset = 1
        self.axes.reset_scale()
        self.assertEqual(self.axes.x_axis.min, -0.05)
        self.assertEqual(self.axes.x_axis.max,  1.05)
        self.assertEqual(self.axes.y_axis.min, -0.05)
        self.assertEqual(self.axes.y_axis.max,  1.05)
        self.assertEqual(self.axes.z_axis.min, -0.05)
        self.assertEqual(self.axes.z_axis.max,  1.05)

        with patch_tecutil('Reset3DScaleFactors', return_value=False):
            with self.assertRaises(TecplotSystemError):
                self.axes.reset_scale()

    def test_reset_range(self):
        self.axes.x_axis.min = -10
        self.axes.x_axis.max =  10
        self.axes.y_axis.min = -10
        self.axes.y_axis.max =  10
        self.axes.z_axis.min = -10
        self.axes.z_axis.max =  10
        self.axes.aspect_ratio_limit = 1
        self.axes.aspect_ratio_reset = 1
        self.axes.range_aspect_ratio_limit = 1
        self.axes.range_aspect_ratio_reset = 1
        self.axes.reset_range()
        self.assertEqual(self.axes.x_axis.min, -0.05)
        self.assertEqual(self.axes.x_axis.max,  1.05)
        self.assertEqual(self.axes.y_axis.min, -0.05)
        self.assertEqual(self.axes.y_axis.max,  1.05)
        self.assertEqual(self.axes.z_axis.min, -0.05)
        self.assertEqual(self.axes.z_axis.max,  1.05)

        with patch_tecutil('Reset3DAxes', return_value=False):
            with self.assertRaises(TecplotSystemError):
                self.axes.reset_range()

    def test_reset_origin(self):
        self.axes.aspect_ratio_limit = 1
        self.axes.aspect_ratio_reset = 1
        self.axes.range_aspect_ratio_limit = 1
        self.axes.range_aspect_ratio_reset = 1
        self.axes.reset_range()

        self.axes.plot.show_contour = True
        self.axes.plot.fieldmap(0).surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces

        self.axes.reset_origin(OriginResetLocation.DataCenter)
        self.axes.reset_origin(OriginResetLocation.ViewCenter)

        with patch_tecutil('Reset3DOriginX', return_value=False):
            with self.assertRaises(TecplotSystemError):
                self.axes.reset_origin()

    def test_padding(self):
        for val in [0,0.5,1,2,100,200]:
            self.axes.padding = val
            self.assertEqual(self.axes.padding, val)
        with self.assertRaises(ValueError):
            self.axes.padding = 'badvalue'
        with self.assertRaises(TecplotSystemError):
            self.axes.padding = -1

    def test_subclasses(self):
        self.assertIsInstance(self.axes, Cartesian3DFieldAxes)
        self.assertIsInstance(self.axes.grid_area   , Cartesian3DGridArea)
        self.assertIsInstance(self.axes.viewport    , ReadOnlyViewport)
        self.assertIsInstance(self.axes.x_axis      , Cartesian3DFieldAxis)
        self.assertIsInstance(self.axes.y_axis      , Cartesian3DFieldAxis)

    def test_iter(self):
        for ax, n in zip(self.axes, ('X', 'Y', 'Z')):
            self.assertIsInstance(ax, Cartesian3DFieldAxis)
            self.assertEqual(ax._sv_name, n)

class TestPolarLineAxes(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        fr = tp.active_frame()
        fr.activate()
        ds = fr.dataset
        xvar = ds.add_variable('X')
        z = ds.add_ordered_zone('Zone', (2,))
        xx = np.linspace(-1,1,2)
        z.values('X')[:] = xx
        plot = fr.plot(PlotType.PolarLine)
        plot.activate()
        self.axes = plot.axes

    def test_preserve_scale(self):
        for val in [True,False,True]:
            self.axes.preserve_scale = val
            self.assertEqual(self.axes.preserve_scale, val)

    def test_subclasses(self):
        self.assertIsInstance(self.axes, PolarLineAxes)
        self.assertIsInstance(self.axes.grid_area   , GridArea)
        self.assertIsInstance(self.axes.precise_grid, PreciseGrid)
        self.assertIsInstance(self.axes.viewport    , PolarViewport)
        self.assertIsInstance(self.axes.r_axis      , RadialLineAxis)
        self.assertIsInstance(self.axes.theta_axis  , PolarAngleLineAxis)

    def test_iter(self):
        r,t = list(self.axes)
        self.assertIsInstance(r, RadialLineAxis)
        self.assertIsInstance(t, PolarAngleLineAxis)
        self.assertEqual(r._sv_name, 'R')
        self.assertEqual(t._sv_name, 'THETA')

class TestXYLineAxes(TestCartesian2DFieldAxes):
    def setUp(self):
        tp.new_layout()
        self.filename,ds = sample_data('3x3x3_p')
        fr = tp.active_frame()
        fr.activate()
        plot = fr.plot(PlotType.XYLine)
        plot.activate()
        self.axes = plot.axes

    def tearDown(self):
        os.remove(self.filename)

    def test_subclasses(self):
        self.assertIsInstance(self.axes, XYLineAxes)
        self.assertIsInstance(self.axes.grid_area   , GridArea)
        self.assertIsInstance(self.axes.precise_grid, PreciseGrid)
        self.assertIsInstance(self.axes.viewport    , Cartesian2DViewport)
        self.assertIsInstance(self.axes.x_axis(0)   , XYLineAxis)
        self.assertIsInstance(self.axes.y_axis(0)   , XYLineAxis)

    def test_iter(self):
        axes = list(self.axes)
        self.assertEqual(len(axes), 10)
        for ax, n in zip(axes, ['X','Y']*5):
            self.assertIsInstance(ax, XYLineAxis)
            self.assertEqual(ax._sv_name, n)


class TestOrientationAxes(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename,ds = sample_data('3x3x3_p')
        fr = tp.active_frame()
        fr.activate()
        plot = fr.plot(PlotType.Cartesian3D)
        plot.activate()
        self.axes = plot.axes.orientation_axis

    def tearDown(self):
        os.remove(self.filename)

    def test_show(self):
        for val in [True,False,True]:
            self.axes.show = val
            self.assertEqual(self.axes.show, val)

    def test_size(self):
        for val in [0,0.5,1,100]:
            self.axes.size = val
            self.assertEqual(self.axes.size, val)
        with self.assertRaises(ValueError):
            self.axes.size = 'badvalue'
        with self.assertRaises(TecplotSystemError):
            self.axes.size = -1

    def test_line_thickness(self):
        for val in [0.5,1,100]:
            self.axes.line_thickness = val
            self.assertEqual(self.axes.line_thickness, val)
        with self.assertRaises(ValueError):
            self.axes.line_thickness = 'badvalue'
        with self.assertRaises(TecplotSystemError):
            self.axes.line_thickness = -1
        with self.assertRaises(TecplotSystemError):
            self.axes.line_thickness = 0

    def test_color(self):
        for val in [Color.Blue, Color.Red, Color.Black]:
            self.axes.color = val
            self.assertEqual(self.axes.color, val)
        with self.assertRaises(ValueError):
            self.axes.color = 0.5

    def test_position(self):
        p = self.axes.position
        for val in [(0,0), (1,0), (0,1)]:
            self.axes.position = val
            pos = self.axes.position
            self.assertEqual(pos[0], val[0])
            self.assertEqual(pos[1], val[1])
            self.assertEqual(pos.x, val[0])
            self.assertEqual(pos.y, val[1])
        with self.assertRaises(TypeError):
            self.axes.position = 0.5

    def test_show_variable_name(self):
        for val in [True,False,True]:
            self.axes.show_variable_name = val
            self.assertEqual(self.axes.show_variable_name, val)


if __name__ == '__main__':
    from .. import main
    main()
