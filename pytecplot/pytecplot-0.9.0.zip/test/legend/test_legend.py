import os
import unittest

import tecplot as tp
from tecplot.constant import *
from tecplot.exception import *
from tecplot.legend import LineLegend, ContourLegend

from ..property_test import PropertyTest
from ..sample_data import sample_data


class TestLegend(PropertyTest):

    def setUp(self):
        tp.new_layout()
        self.filename, self.dataset = sample_data('2x2x3_overlap')
        frame = tp.active_frame()
        frame.plot_type = PlotType.XYLine
        # type: LineLegend
        self.line_legend = frame.plot(PlotType.XYLine).legend

        plot = frame.plot(PlotType.Cartesian3D)
        plot.vector.u_variable_index = 0
        plot.vector.v_variable_index = 1
        plot.vector.w_variable_index = 2
        self.contour_legend = plot.contour(0).legend  # type: ContourLegend
        self.all_legends = ((self.line_legend, LineLegend),
                            (self.contour_legend, ContourLegend))

    def tearDown(self):
        os.remove(self.filename)

    def test_line_legend_round_trip(self):
        for api, value in (
                ('show_text', bool),
        ):
            self.internal_test_property_round_trip(
                api, value, LineLegend,
                self.line_legend)

        self.internal_test_text_box_round_trip(self.line_legend.box)
        self.internal_test_text_font_round_trip(self.line_legend.font)

    def test_round_trip(self):
        for legend, legend_type in self.all_legends:
            for api, value in (
                    ('anchor_alignment', AnchorAlignment),
                    ('row_spacing', float),
                    ('show', bool),
                    ('text_color', Color),
                    ('position', (1.0, 2.0)),
            ):
                self.internal_test_property_round_trip(
                    api, value, legend_type, legend)

        # Line Legend
        for api, value in (
                ('show_text', bool),
        ):
            self.internal_test_property_round_trip(
                api, value, LineLegend,
                self.line_legend)

        # Contour Legend
        for api, value in (
                ('auto_resize', bool),
                ('include_cutoff_levels', bool),
                ('vertical', bool),
                ('label_increment', float),
                ('label_location', ContLegendLabelLocation),
                ('overlay_bar_grid', bool),
                ('show_header', bool),
        ):
            self.internal_test_property_round_trip(
                api, value, ContourLegend,
                self.contour_legend)

    def test_invalid_position(self):
        if __debug__:
            for legend, _ in self.all_legends:
                with self.assertRaises(TypeError):
                    legend.position = '###'
                with self.assertRaises(TypeError):
                    legend.position = [1, 2, 3]
                with self.assertRaises(TypeError):
                    legend.position = 0
                with self.assertRaises(ValueError):
                    legend.position = 'a'


class TestLineLegendFont(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename, self.dataset = sample_data('2x2x3_overlap')
        frame = tp.active_frame()
        frame.plot_type = PlotType.XYLine
        self.legend = frame.plot(PlotType.XYLine).legend

    def tearDown(self):
        os.remove(self.filename)

    def test_bold(self):
        for val in [True, False, True]:
            self.legend.font.bold = val
            self.assertEqual(self.legend.font.bold, val)

    def test_italic(self):
        for val in [True, False, True]:
            self.legend.font.italic = val
            self.assertEqual(self.legend.font.italic, val)

    def test_size(self):
        for val in [1, 100]:
            self.legend.font.size = val
            self.assertEqual(self.legend.font.size, val)
        with self.assertRaises(ValueError):
            self.legend.font.size = 'badtype'
        with self.assertRaises(TecplotSystemError):
            self.legend.font.size = 0

    def test_size_units(self):
        for val in [Units.Point, Units.Frame, Units.Point]:
            self.legend.font.size_units = val
            self.assertEqual(self.legend.font.size_units, val)
        with self.assertRaises((TecplotValueError, TecplotSystemError)):
            self.legend.font.size_units = Units.Grid

    def test_typeface(self):
        for val in ['Arial']:
            self.legend.font.typeface = val
            self.assertEqual(self.legend.font.typeface, val)


class TestContourLegend(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename, self.dataset = sample_data('2x2x3_overlap')
        frame = tp.active_frame()

        plot = frame.plot(PlotType.Cartesian3D)
        plot.vector.u_variable_index = 0
        plot.vector.v_variable_index = 1
        plot.vector.w_variable_index = 2
        self.legend = plot.contour(0).legend

    def tearDown(self):
        os.remove(self.filename)

    def test_box(self):
        self.assertIsInstance(self.legend.box, tp.text.TextBox)

    def test_label_step(self):
        for val in [1,2,3.14,10]:
            self.legend.label_step = val
            self.assertEqual(self.legend.label_step, int(val))
            self.assertEqual(self.legend.contour.labels.step, int(val))
        with self.assertRaises(ValueError):
            self.legend.label_step = 'badtype'
        with self.assertRaises(TypeError):
            self.legend.label_step = None
        with self.assertRaises(TecplotSystemError):
            self.legend.label_step = -1
        with self.assertRaises(TecplotSystemError):
            self.legend.label_step = 0

    def test_label_format(self):
        fmt = self.legend.label_format
        fmt_alt = self.legend.contour.labels.format
        for val in [1,2,10]:
            fmt.precision = val
            self.assertAlmostEqual(fmt.precision, val)
            self.assertAlmostEqual(fmt.precision, fmt_alt.precision)
        with self.assertRaises(ValueError):
            fmt.precision = 'badvalue'
        with self.assertRaises(TecplotSystemError):
            fmt.precision = -1
        with self.assertRaises(TecplotSystemError):
            fmt.precision = 0


class TestContourLegendFont(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename, self.dataset = sample_data('2x2x3_overlap')
        frame = tp.active_frame()

        plot = frame.plot(PlotType.Cartesian3D)
        plot.vector.u_variable_index = 0
        plot.vector.v_variable_index = 1
        plot.vector.w_variable_index = 2
        self.legend = plot.contour(0).legend

    def tearDown(self):
        os.remove(self.filename)

    def test_bold(self):
        for val in [True, False, True]:
            self.legend.header_font.bold = val
            self.assertEqual(self.legend.header_font.bold, val)

            self.legend.number_font.bold = val
            self.assertEqual(self.legend.number_font.bold, val)

    def test_italic(self):
        for val in [True, False, True]:
            self.legend.header_font.italic = val
            self.assertEqual(self.legend.header_font.italic, val)
            self.legend.number_font.italic = val
            self.assertEqual(self.legend.number_font.italic, val)

    def test_size(self):
        for val in [1, 100]:
            self.legend.header_font.size = val
            self.assertEqual(self.legend.header_font.size, val)
            self.legend.number_font.size = val
            self.assertEqual(self.legend.number_font.size, val)
        with self.assertRaises(ValueError):
            self.legend.number_font.size = 'badtype'
        with self.assertRaises(TecplotSystemError):
            self.legend.number_font.size = 0

    def test_size_units(self):
        for val in [Units.Point, Units.Frame, Units.Point]:
            self.legend.header_font.size_units = val
            self.assertEqual(self.legend.header_font.size_units, val)
        with self.assertRaises((TecplotValueError, TecplotSystemError)):
            self.legend.header_font.size_units = Units.Grid

        for val in [Units.Point, Units.Frame, Units.Point]:
            self.legend.number_font.size_units = val
            self.assertEqual(self.legend.number_font.size_units, val)
        with self.assertRaises((TecplotValueError, TecplotSystemError)):
            self.legend.number_font.size_units = Units.Grid

    def test_typeface(self):
        for val in ['Arial']:
            self.legend.header_font.typeface = val
            self.assertEqual(self.legend.header_font.typeface, val)
            self.legend.number_font.typeface = val
            self.assertEqual(self.legend.number_font.typeface, val)


if __name__ == '__main__':
    from .. import main
    main()
