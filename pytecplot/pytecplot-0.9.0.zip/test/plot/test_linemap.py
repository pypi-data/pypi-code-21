import os
import unittest

import tecplot as tp
from tecplot.exception import *
from tecplot.constant import *
from tecplot.plot.axis import PolarAngleLineAxis, RadialLineAxis
from tecplot.tecutil import IndexRange

from ..sample_data import sample_data


class TestLinemap(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename,self.dataset = sample_data('xylines_poly')
        frame = tp.active_frame()
        frame.plot_type = PlotType.XYLine
        plot = frame.plot()
        zone = self.dataset.zone(0)
        x = self.dataset.variable('X')
        plot.add_linemap('p', zone, x, self.dataset.variable('P'))
        self.lmap = frame.plot().linemap(0)

    def tearDown(self):
        os.remove(self.filename)

    def test_eq(self):
        self.assertTrue(self.lmap == self.lmap.plot.linemap(0))
        self.assertTrue(self.lmap != self.lmap.plot.linemap(1))
        self.assertFalse(self.lmap != self.lmap.plot.linemap(0))
        self.assertFalse(self.lmap == self.lmap.plot.linemap(1))

    def test_show(self):
        for val in [True,False,True]:
            self.lmap.show = val
            self.assertEqual(self.lmap.show, val)

    def test_show_in_legend(self):
        for val in [LegendShow.Always,LegendShow.Never,LegendShow.Auto]:
            self.lmap.show_in_legend = val
            self.assertEqual(self.lmap.show_in_legend, val)
        with self.assertRaises(ValueError):
            self.lmap.show_in_legend = 0.5

    def test_name(self):
        self.lmap.name = 'test'
        self.assertEqual(self.lmap.name, 'test')

    def test_toplevel_style_objs(self):
        self.assertIsInstance(self.lmap.bars, tp.plot.LinemapBars)
        self.assertIsInstance(self.lmap.curve, tp.plot.LinemapCurve)
        self.assertIsInstance(self.lmap.error_bars, tp.plot.LinemapErrorBars)
        self.assertIsInstance(self.lmap.indices, tp.plot.LinemapIndices)
        self.assertIsInstance(self.lmap.line, tp.plot.LinemapLine)
        self.assertIsInstance(self.lmap.symbols, tp.plot.LinemapSymbols)

    def test_index(self):
        self.assertEqual(self.lmap.index, 0)

    def test_sort(self):
        with self.assertRaises(TecplotLogicError):
            self.lmap.sort_mode = LineMapSort.BySpecificVar
        self.lmap.sort_variable = self.dataset.variable(0)
        for val in [LineMapSort.ByIndependentVar, LineMapSort.ByDependentVar,
                    LineMapSort.BySpecificVar]:
            self.lmap.sort_mode = val
            self.assertEqual(self.lmap.sort_mode, val)
        with self.assertRaises(ValueError):
            self.lmap.sort_mode = 0.5

        var0 = self.dataset.variable(0)
        var2 = self.dataset.variable(2)
        var3 = self.dataset.variable(3)
        for val in [var0, var2, var3]:
            self.lmap.sort_variable = val
            self.assertEqual(self.lmap.sort_variable, val)
        self.lmap.sort_variable_index = 2
        self.assertEqual(self.lmap.sort_variable_index, 2)
        self.assertEqual(self.lmap.sort_variable, var2)
        with self.assertRaises(AttributeError):
            self.lmap.sort_variable = 0.5

    def test_zone(self):
        self.lmap.zone = self.dataset.zone(0)
        self.assertEqual(self.lmap.zone_index, 0)
        self.assertEqual(self.lmap.zone, self.dataset.zone(0))
        self.lmap.zone_index = 0
        self.assertEqual(self.lmap.zone_index, 0)
        self.assertEqual(self.lmap.zone, self.dataset.zone(0))

    def test_aux_data(self):
        self.lmap.aux_data['test'] = 'some info'
        self.assertEqual(self.lmap.aux_data['test'], 'some info')


class TestLinemapBars(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename,self.dataset = sample_data('xylines_poly')
        frame = tp.active_frame()
        frame.plot_type = PlotType.XYLine
        plot = frame.plot()
        zone = self.dataset.zone(0)
        x = self.dataset.variable('X')
        plot.add_linemap('p', zone, x, self.dataset.variable('P'))
        self.bars = frame.plot().linemap(0).bars

    def tearDown(self):
        os.remove(self.filename)

    def test_eq(self):
        self.assertTrue(self.bars == self.bars.linemap.plot.linemap(0).bars)
        self.assertTrue(self.bars != self.bars.linemap.plot.linemap(1).bars)
        self.assertFalse(self.bars != self.bars.linemap.plot.linemap(0).bars)
        self.assertFalse(self.bars == self.bars.linemap.plot.linemap(1).bars)

    def test_line_color(self):
        for val in [Color.Black,Color.Red,Color.Green]:
            self.bars.line_color = val
            self.assertEqual(self.bars.line_color, val)
        with self.assertRaises(ValueError):
            self.bars.line_color = 0.5

    def test_fill_mode(self):
        for c in [FillMode.UseSpecificColor, FillMode.UseBackgroundColor,
                  FillMode.UseLineColor]:
            self.bars.fill_mode = c
            self.assertEqual(self.bars.fill_mode, c)
        with self.assertRaises(ValueError):
            self.bars.fill_mode = 0.5

    def test_fill_color(self):
        for c in [Color.Red, Color.Black, Color.Blue, Color.Blue]:
            self.bars.fill_color = c
            self.assertEqual(self.bars.fill_color, c)
        with self.assertRaises(ValueError):
            self.bars.fill_color = 0.5

    def test_line_thickness(self):
        for val in [0.5,1,2]:
            self.bars.line_thickness = val
            self.assertEqual(self.bars.line_thickness, val)
        with self.assertRaises(ValueError):
            self.bars.line_thickness = 'badvalue'
        with self.assertRaises(TecplotSystemError):
            self.bars.line_thickness = 0
        with self.assertRaises(TecplotSystemError):
            self.bars.line_thickness = -1

    def test_show(self):
        for val in [True,False,True]:
            self.bars.show = val
            self.assertEqual(self.bars.show, val)

    def test_size(self):
        for val in [0,0.5,1,2]:
            self.bars.size = val
            self.assertEqual(self.bars.size, val)
        with self.assertRaises(ValueError):
            self.bars.size = 'badvalue'
        with self.assertRaises(TecplotSystemError):
            self.bars.size = -1


class TestLinemapCurve(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename,self.dataset = sample_data('xylines_poly')
        frame = tp.active_frame()
        frame.plot_type = PlotType.XYLine
        plot = frame.plot()
        zone = self.dataset.zone(0)
        x = self.dataset.variable('X')
        plot.add_linemap('p', zone, x, self.dataset.variable('P'))
        self.curve = frame.plot().linemap(0).curve

    def tearDown(self):
        os.remove(self.filename)

    def test_curve_type(self):
        for val in [CurveType.LineSeg,CurveType.PolynomialFit,
                    CurveType.EToRFit]:
            self.curve.curve_type = val
            self.assertEqual(self.curve.curve_type, val)
        with self.assertRaises(ValueError):
            self.curve.curve_type = 0.5

    def test_use_fit_range(self):
        for val in [True, False, True]:
            self.curve.use_fit_range = val
            self.assertEqual(self.curve.use_fit_range, val)

    def test_fit_range(self):
        for val in [(-10,0),(0,10),(0,-10)]:
            self.curve.fit_range = val
            self.assertEqual(self.curve.fit_range, val)
            if __debug__:
                with self.assertRaises(TecplotLogicError):
                    self.curve.fit_range = 3
            else:
                with self.assertRaises(TypeError):
                    self.curve.fit_range = 3

    def test_num_points(self):
        for val in [2,10,1000]:
            self.curve.num_points = val
            self.assertEqual(self.curve.num_points, val)
        with self.assertRaises(TecplotSystemError):
            self.curve.num_points = -1
        with self.assertRaises(TecplotSystemError):
            self.curve.num_points = 0
        with self.assertRaises(TecplotSystemError):
            self.curve.num_points = 1
        with self.assertRaises(TypeError):
            self.curve.num_points = None
        with self.assertRaises(ValueError):
            self.curve.num_points = 'badtype'

    def test_polynomial_order(self):
        for val in [1,2,10]:
            self.curve.polynomial_order = val
            self.assertEqual(self.curve.polynomial_order, val)
        with self.assertRaises(TecplotSystemError):
            self.curve.polynomial_order = -1
        with self.assertRaises(TecplotSystemError):
            self.curve.polynomial_order = 0
        with self.assertRaises(TecplotSystemError):
            self.curve.polynomial_order = 11
        with self.assertRaises(TypeError):
            self.curve.polynomial_order = None
        with self.assertRaises(ValueError):
            self.curve.polynomial_order = 'badtype'

    def test_clamp_spline(self):
        for val in [True, False, True]:
            self.curve.clamp_spline = val
            self.assertEqual(self.curve.clamp_spline, val)

    def test_spline_derivative_at_ends(self):
        for val in [(-10,0),(0,10),(0,-10)]:
            self.curve.spline_derivative_at_ends = val
            self.assertEqual(self.curve.spline_derivative_at_ends, val)
            if __debug__:
                with self.assertRaises(TecplotLogicError):
                    self.curve.spline_derivative_at_ends = 3
            else:
                with self.assertRaises(TypeError):
                    self.curve.spline_derivative_at_ends = 3

    def test_weight_variable(self):
        for val in [True, False, True]:
            self.curve.use_weight_variable = val
            self.assertEqual(self.curve.use_weight_variable, val)
        xvar = self.dataset.variable('X')
        yvar = self.dataset.variable('Y')
        self.curve.weight_variable = yvar
        self.assertEqual(self.curve.weight_variable, yvar)
        self.curve.weight_variable = xvar
        self.assertEqual(self.curve.weight_variable, xvar)
        with self.assertRaises(AttributeError):
            self.curve.weight_variable = None

    def test_weight_variable_index(self):
        var0 = self.dataset.variable(0)
        var1 = self.dataset.variable(1)
        self.curve.weight_variable_index = 1
        self.assertEqual(self.curve.weight_variable_index, 1)
        self.assertEqual(self.curve.weight_variable, var1)
        self.curve.weight_variable_index = 0
        self.assertEqual(self.curve.weight_variable_index, 0)
        self.assertEqual(self.curve.weight_variable, var0)
        with self.assertRaises(TypeError):
            self.curve.weight_variable_index = None


class TestLinemapErrorBars(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename,self.dataset = sample_data('xylines_poly')
        frame = tp.active_frame()
        frame.plot_type = PlotType.XYLine
        plot = frame.plot()
        zone = self.dataset.zone(0)
        x = self.dataset.variable('X')
        plot.add_linemap('p', zone, x, self.dataset.variable('P'))
        self.error_bars = frame.plot().linemap(0).error_bars
        self.error_bars.variable = self.dataset.variable('X')

    def tearDown(self):
        os.remove(self.filename)

    def test_bar_type(self):
        for val in [ErrorBar.Up,ErrorBar.Down,ErrorBar.Left]:
            self.error_bars.bar_type = val
            self.assertEqual(self.error_bars.bar_type, val)
        with self.assertRaises(ValueError):
            self.error_bars.bar_type = 0.5

    def test_color(self):
        for val in [Color.Black,Color.Red,Color.Green]:
            self.error_bars.color = val
            self.assertEqual(self.error_bars.color, val)
        with self.assertRaises(ValueError):
            self.error_bars.color = 0.5

    def test_line_thickness(self):
        for val in [0.5,1,2]:
            self.error_bars.line_thickness = val
            self.assertEqual(self.error_bars.line_thickness, val)
        with self.assertRaises(ValueError):
            self.error_bars.line_thickness = 'badvalue'
        with self.assertRaises(TecplotSystemError):
            self.error_bars.line_thickness = 0
        with self.assertRaises(TecplotSystemError):
            self.error_bars.line_thickness = -1

    def test_show(self):
        for val in [True,False,True]:
            self.error_bars.show = val
            self.assertEqual(self.error_bars.show, val)

    def test_endcap_size(self):
        for val in [0,0.5,1]:
            self.error_bars.endcap_size = val
            self.assertEqual(self.error_bars.endcap_size, val)
        with self.assertRaises(ValueError):
            self.error_bars.endcap_size = 'badtype'
        with self.assertRaises(TecplotSystemError):
            self.error_bars.endcap_size = -1

    def test_step_mode(self):
        for val in [StepMode.ByIndex,StepMode.ByFrameUnits,StepMode.ByIndex]:
            self.error_bars.step_mode = val
            self.assertEqual(self.error_bars.step_mode, val)
        with self.assertRaises(ValueError):
            self.error_bars.step_mode = 0.5

    def test_step(self):
        for val in [0,0.5,1,2]:
            self.error_bars.step = val
            self.assertEqual(self.error_bars.step, val)
        with self.assertRaises((TypeError,ValueError)):
            self.error_bars.step = 'badtype'
        with self.assertRaises((TecplotLogicError, TypeError)):
            self.error_bars.step = None
        if __debug__:
            with self.assertRaises(TecplotLogicError):
                self.error_bars.step = -1
        else:
            self.error_bars.step = -1

    def test_variable(self):
        qvar = self.dataset.variable('Q')
        rvar = self.dataset.variable('R')
        self.error_bars.variable = qvar
        self.assertEqual(self.error_bars.variable, qvar)
        self.error_bars.variable = rvar
        self.assertEqual(self.error_bars.variable, rvar)

    def test_variable_index(self):
        var0 = self.dataset.variable(0)
        var1 = self.dataset.variable(1)
        self.error_bars.variable_index = 1
        self.assertEqual(self.error_bars.variable_index, 1)
        self.assertEqual(self.error_bars.variable, var1)
        self.error_bars.variable_index = 0
        self.assertEqual(self.error_bars.variable_index, 0)
        self.assertEqual(self.error_bars.variable, var0)


class TestLinemapIndices(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename,dataset = sample_data('3x3x3_p')
        frame = tp.active_frame()
        frame.plot_type = PlotType.XYLine
        plot = frame.plot()
        zone = dataset.zone(0)
        x = dataset.variable('X')
        plot.add_linemap('p', zone, x, dataset.variable('P'))
        self.indices = frame.plot().linemap(0).indices

    def tearDown(self):
        os.remove(self.filename)

    def test_varying_index(self):
        for var in [IJKLines.K,IJKLines.J,IJKLines.I]:
            self.indices.varying_index = var
            self.assertEqual(self.indices.varying_index, var)
        with self.assertRaises(ValueError):
            self.indices.varying_index = 0.5

    def test_ranges(self):
        self.indices.i_range = None,None,None
        self.assertEqual(self.indices.i_range, IndexRange(0,-1,1))
        self.indices.i_range = 0,-1,1
        self.assertEqual(self.indices.i_range, IndexRange(0,-1,1))
        self.indices.i_range = -10,-1,1
        self.assertEqual(self.indices.i_range, IndexRange(-10,-1,1))
        self.indices.i_range = None,10,1
        self.assertEqual(self.indices.i_range, IndexRange(0,10,1))
        self.indices.i_range = 0,None,1
        self.assertEqual(self.indices.i_range, IndexRange(0,-1,1))
        self.indices.i_range = 0,10,None
        self.assertEqual(self.indices.i_range, IndexRange(0,10,1))
        self.indices.i_range = 0,10
        self.assertEqual(self.indices.i_range, IndexRange(0,10,1))
        self.indices.i_range = 0,
        self.assertEqual(self.indices.i_range, IndexRange(0,-1,1))

        self.indices.j_range = None,None,None
        self.assertEqual(self.indices.j_range, IndexRange(0,-1,1))
        self.indices.j_range = 0,-1,1
        self.assertEqual(self.indices.j_range, IndexRange(0,-1,1))
        self.indices.j_range = -10,-1,1
        self.assertEqual(self.indices.j_range, IndexRange(-10,-1,1))
        self.indices.j_range = None,10,1
        self.assertEqual(self.indices.j_range, IndexRange(0,10,1))
        self.indices.j_range = 0,None,1
        self.assertEqual(self.indices.j_range, IndexRange(0,-1,1))
        self.indices.j_range = 0,10,None
        self.assertEqual(self.indices.j_range, IndexRange(0,10,1))
        self.indices.j_range = 0,10
        self.assertEqual(self.indices.j_range, IndexRange(0,10,1))
        self.indices.j_range = 0,
        self.assertEqual(self.indices.j_range, IndexRange(0,-1,1))

        self.indices.k_range = None,None,None
        self.assertEqual(self.indices.k_range, IndexRange(0,-1,1))
        self.indices.k_range = 0,-1,1
        self.assertEqual(self.indices.k_range, IndexRange(0,-1,1))
        self.indices.k_range = -10,-1,1
        self.assertEqual(self.indices.k_range, IndexRange(-10,-1,1))
        self.indices.k_range = None,10,1
        self.assertEqual(self.indices.k_range, IndexRange(0,10,1))
        self.indices.k_range = 0,None,1
        self.assertEqual(self.indices.k_range, IndexRange(0,-1,1))
        self.indices.k_range = 0,10,None
        self.assertEqual(self.indices.k_range, IndexRange(0,10,1))
        self.indices.k_range = 0,10
        self.assertEqual(self.indices.k_range, IndexRange(0,10,1))
        self.indices.k_range = 0,
        self.assertEqual(self.indices.k_range, IndexRange(0,-1,1))


class TestLinemapLine(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename,dataset = sample_data('xylines_poly')
        frame = tp.active_frame()
        frame.plot_type = PlotType.XYLine
        plot = frame.plot()
        zone = dataset.zone(0)
        x = dataset.variable('X')
        plot.add_linemap('p', zone, x, dataset.variable('P'))
        self.line = frame.plot().linemap(0).line

    def tearDown(self):
        os.remove(self.filename)

    def test_show(self):
        for val in [True,False,True]:
            self.line.show = val
            self.assertEqual(self.line.show, val)

    def test_color(self):
        for val in [Color.Black,Color.Red,Color.Green]:
            self.line.color = val
            self.assertEqual(self.line.color, val)
        with self.assertRaises(ValueError):
            self.line.color = 0.5

    def test_line_pattern(self):
        for val in [LinePattern.Solid,LinePattern.Dashed,LinePattern.DashDot]:
            self.line.line_pattern = val
            self.assertEqual(self.line.line_pattern, val)
        with self.assertRaises(ValueError):
            self.line.line_pattern = 0.5

    def test_line_thickness(self):
        for val in [0.5,1,2]:
            self.line.line_thickness = val
            self.assertEqual(self.line.line_thickness, val)
        with self.assertRaises(ValueError):
            self.line.line_thickness = 'badvalue'
        with self.assertRaises(TecplotSystemError):
            self.line.line_thickness = 0
        with self.assertRaises(TecplotSystemError):
            self.line.line_thickness = -1

    def test_pattern_length(self):
        for val in [0.5,1,2]:
            self.line.pattern_length = val
            self.assertEqual(self.line.pattern_length, val)
        with self.assertRaises(ValueError):
            self.line.pattern_length = 'badvalue'
        with self.assertRaises(TecplotSystemError):
            self.line.pattern_length = 0
        with self.assertRaises(TecplotSystemError):
            self.line.pattern_length = -1


class TestLinemapSymbols(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename,dataset = sample_data('xylines_poly')
        frame = tp.active_frame()
        frame.plot_type = PlotType.XYLine
        plot = frame.plot()
        zone = dataset.zone(0)
        x = dataset.variable('X')
        plot.add_linemap('p', zone, x, dataset.variable('P'))
        self.sym = frame.plot().linemap(0).symbols

    def tearDown(self):
        os.remove(self.filename)

    def test_show(self):
        for val in [True,False]:
            self.sym.show = val
            self.assertEqual(self.sym.show, val)

    def test_symbol_type(self):
        for val in [SymbolType.Geometry, SymbolType.Text]:
            self.sym.symbol_type = val
            self.assertEqual(self.sym.symbol_type, val)
        with self.assertRaises(ValueError):
            self.sym.symbol_type = 0.5

    def test_symbol(self):
        self.sym.symbol_type = SymbolType.Text
        self.assertIsInstance(self.sym.symbol(), tp.plot.TextSymbol)
        self.sym.symbol_type = SymbolType.Geometry
        self.assertIsInstance(self.sym.symbol(), tp.plot.GeometrySymbol)

    def test_step_mode(self):
        for val in [StepMode.ByIndex,StepMode.ByFrameUnits,StepMode.ByIndex]:
            self.sym.step_mode = val
            self.assertEqual(self.sym.step_mode, val)
        with self.assertRaises(ValueError):
            self.sym.step_mode = 0.5

    def test_step(self):
        for val in [1,2]:
            self.sym.step = val
            self.assertEqual(self.sym.step, val)
        self.sym.step = 0
        self.assertEqual(self.sym.step, 1)
        with self.assertRaises((TypeError,ValueError)):
            self.sym.step = 'badtype'
        with self.assertRaises((TecplotLogicError, TypeError)):
            self.sym.step = None
        if __debug__:
            with self.assertRaises(TecplotLogicError):
                self.sym.step = -1
        else:
            self.sym.step = -1

    def test_fill_mode(self):
        for c in [FillMode.UseSpecificColor, FillMode.UseLineColor,
                  FillMode.UseBackgroundColor]:
            self.sym.fill_mode = c
            self.assertEqual(self.sym.fill_mode, c)
        with self.assertRaises(ValueError):
            self.sym.color = 0.5

    def test_fill_color(self):
        for c in [Color.Red, Color.Black, Color.Blue]:
            self.sym.fill_color = c
            self.assertEqual(self.sym.fill_color, c)
        with self.assertRaises(ValueError):
            self.sym.color = 0.5

    def test_color(self):
        for c in [Color.Red,Color.Black]:
            self.sym.color = c
            self.assertEqual(self.sym.color, c)
        with self.assertRaises(ValueError):
            self.sym.color = 0.5

    def test_size(self):
        for val in [0,0.5,1,2]:
            self.sym.size = val
            self.assertEqual(self.sym.size, val)
        with self.assertRaises(ValueError):
            self.sym.size = 'badvalue'
        with self.assertRaises(TecplotSystemError):
            self.sym.size = -1

    def test_line_thickness(self):
        for val in [0.5,1,2]:
            self.sym.line_thickness = val
            self.assertEqual(self.sym.line_thickness, val)
        with self.assertRaises(ValueError):
            self.sym.line_thickness = 'badvalue'
        with self.assertRaises(TecplotSystemError):
            self.sym.line_thickness = 0
        with self.assertRaises(TecplotSystemError):
            self.sym.line_thickness = -1


class TestXYLinemap(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename,self.dataset = sample_data('xylines_poly')
        frame = tp.active_frame()
        frame.plot_type = PlotType.XYLine
        self.plot = frame.plot()
        zone = self.dataset.zone(0)
        x = self.dataset.variable('X')
        self.plot.add_linemap('p', zone, x, self.dataset.variable('P'))
        self.lmap = self.plot.linemap(0)

    def tearDown(self):
        os.remove(self.filename)

    def test_function_dependency(self):
        for var in [FunctionDependency.YIndependent,
                    FunctionDependency.XIndependent,
                    FunctionDependency.YIndependent]:
            self.lmap.function_dependency = var
            self.assertEqual(self.lmap.function_dependency, var)
        with self.assertRaises(ValueError):
            self.lmap.function_dependency = 0.5

    def test_axes(self):
        for i in [0,1,4]:
            self.lmap.x_axis_index = i
            self.lmap.y_axis_index = i
            self.assertEqual(self.lmap.x_axis_index, i)
            self.assertEqual(self.lmap.y_axis_index, i)
        for i in [0,1,2]:
            a = self.plot.axes.x_axis(i)
            self.lmap.x_axis = a
            self.assertEqual(self.lmap.x_axis, a)
            self.assertEqual(self.lmap.x_axis_index, a.index)
            a = self.plot.axes.y_axis(i)
            self.lmap.y_axis = a
            self.assertEqual(self.lmap.y_axis, a)
            self.assertEqual(self.lmap.y_axis_index, a.index)

    def test_variables(self):
        for i in [0,1,2]:
            self.lmap.x_variable_index = i
            self.lmap.y_variable_index = i
            self.assertEqual(self.lmap.x_variable_index, i)
            self.assertEqual(self.lmap.y_variable_index, i)
        for i in [0,1,2]:
            v = self.dataset.variable(i)
            self.lmap.x_variable = v
            self.assertEqual(self.lmap.x_variable, v)
            self.assertEqual(self.lmap.x_variable_index, v.index)
            self.lmap.y_variable = v
            self.assertEqual(self.lmap.y_variable, v)
            self.assertEqual(self.lmap.y_variable_index, v.index)


class TestPolarLinemap(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename,self.dataset = sample_data('xylines_poly')
        frame = tp.active_frame()
        frame.plot_type = PlotType.PolarLine
        self.plot = frame.plot()
        zone = self.dataset.zone(0)
        x = self.dataset.variable('X')
        self.plot.add_linemap('p', zone, x, self.dataset.variable('P'))
        self.lmap = self.plot.linemap(0)

    def tearDown(self):
        os.remove(self.filename)

    def test_function_dependency(self):
        for var in [FunctionDependency.ThetaIndependent,
                    FunctionDependency.RIndependent,
                    FunctionDependency.ThetaIndependent]:
            self.lmap.function_dependency = var
            self.assertEqual(self.lmap.function_dependency, var)
        with self.assertRaises(ValueError):
            self.lmap.function_dependency = 0.5

    def test_axes(self):
        self.assertIsInstance(self.lmap.r_axis, RadialLineAxis)
        self.assertIsInstance(self.lmap.theta_axis, PolarAngleLineAxis)

    def test_variables(self):
        for i in [0,1,2]:
            self.lmap.r_variable_index = i
            self.lmap.theta_variable_index = i
            self.assertEqual(self.lmap.r_variable_index, i)
            self.assertEqual(self.lmap.theta_variable_index, i)
        for i in [0,1,2]:
            v = self.dataset.variable(i)
            self.lmap.r_variable = v
            self.assertEqual(self.lmap.r_variable, v)
            self.assertEqual(self.lmap.r_variable_index, v.index)
            self.lmap.theta_variable = v
            self.assertEqual(self.lmap.theta_variable, v)
            self.assertEqual(self.lmap.theta_variable_index, v.index)


if __name__ == '__main__':
    from .. import main
    main()
