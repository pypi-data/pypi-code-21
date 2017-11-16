import os
import unittest

import tecplot as tp
from tecplot.constant import *
from tecplot.exception import *

from .. import patch_tecutil
from ..sample_data import sample_data

class TestLabelFormat(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename,ds = sample_data('xylines_poly')
        fr = tp.active_frame()
        fr.activate()
        plot = fr.plot(PlotType.XYLine)
        plot.activate()
        self.fmt = plot.axes.x_axis(0).tick_labels.format

    def tearDown(self):
        os.remove(self.filename)

    def test_format_type(self):
        for val in [NumberFormat.Integer, NumberFormat.TimeDate,
                    NumberFormat.BestFloat]:
            self.fmt.format_type = val
            self.assertEqual(self.fmt.format_type, val)
        with self.assertRaises(ValueError):
            self.fmt.format_type = 0.5

    def test_custom_labels(self):
        self.assertEqual(self.fmt.num_custom_labels, 0)
        self.fmt.add_custom_labels('a', 'b')
        self.assertEqual(self.fmt.num_custom_labels, 1)
        self.assertEqual(self.fmt.custom_labels(0), ['a', 'b'])
        self.fmt.custom_labels_index = 0
        self.assertEqual(self.fmt.custom_labels_index, 0)

        with patch_tecutil('CustomLabelsGet', side_effect=TecplotSystemError):
            with self.assertRaises(TecplotSystemError):
                self.fmt.custom_labels(0)

        with self.assertRaises((TecplotLogicError, TecplotSystemError)):
            self.fmt.custom_labels(1)

        with patch_tecutil('CustomLabelsAppend', side_effect=TecplotSystemError):
            with self.assertRaises(TecplotSystemError):
                self.fmt.add_custom_labels('c', 'd')

    def test_precision(self):
        for val in [1,2,10]:
            self.fmt.precision = val
            self.assertAlmostEqual(self.fmt.precision, val)
        with self.assertRaises(ValueError):
            self.fmt.precision = 'badvalue'
        with self.assertRaises(TecplotSystemError):
            self.fmt.precision = -1
        with self.assertRaises(TecplotSystemError):
            self.fmt.precision = 0

    def test_remove_leading_zeros(self):
        for val in [True,False,True]:
            self.fmt.remove_leading_zeros = val
            self.assertEqual(self.fmt.remove_leading_zeros, val)

    def test_show_decimals_on_whole_numbers(self):
        for val in [True,False,True]:
            self.fmt.show_decimals_on_whole_numbers = val
            self.assertEqual(self.fmt.show_decimals_on_whole_numbers, val)

    def test_show_negative_sign(self):
        for val in [True,False,True]:
            self.fmt.show_negative_sign = val
            self.assertEqual(self.fmt.show_negative_sign, val)

    def test_negative_prefix(self):
        for val in ['aa', '0', 0, 3.14, None]:
            self.fmt.negative_prefix = val
            self.assertEqual(self.fmt.negative_prefix, str(val))

    def test_negative_suffix(self):
        for val in ['aa', '0', 0, 3.14, None]:
            self.fmt.negative_suffix = val
            self.assertEqual(self.fmt.negative_suffix, str(val))

    def test_positive_prefix(self):
        for val in ['aa', '0', 0, 3.14, None]:
            self.fmt.positive_prefix = val
            self.assertEqual(self.fmt.positive_prefix, str(val))

    def test_positive_suffix(self):
        for val in ['aa', '0', 0, 3.14, None]:
            self.fmt.positive_suffix = val
            self.assertEqual(self.fmt.positive_suffix, str(val))

    def test_zero_prefix(self):
        for val in ['aa', '0', 0, 3.14, None]:
            self.fmt.zero_prefix = val
            self.assertEqual(self.fmt.zero_prefix, str(val))

    def test_zero_suffix(self):
        for val in ['aa', '0', 0, 3.14, None]:
            self.fmt.zero_suffix = val
            self.assertEqual(self.fmt.zero_suffix, str(val))

    def test_datetime_format(self):
        for val in ['aa', '0', 0, 3.14, None]:
            self.fmt.datetime_format = val
            self.assertEqual(self.fmt.datetime_format, str(val))


if __name__ == '__main__':
    from .. import main
    main()
