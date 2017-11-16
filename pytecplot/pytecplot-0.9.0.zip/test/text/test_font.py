import unittest

import tecplot as tp
from tecplot.exception import *
from tecplot.constant import *


class TestFont(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        plot = tp.active_frame().plot(PlotType.Sketch)
        self.font = plot.axes.x_axis.title.font

    def test_bold(self):
        for val in [True,False,True]:
            self.font.bold = val
            self.assertEqual(self.font.bold, val)

    def test_italic(self):
        for val in [True,False,True]:
            self.font.italic = val
            self.assertEqual(self.font.italic, val)

    def test_size(self):
        self.font.size_units = Units.Frame
        for val in [1,10,100,150]:
            self.font.size = val
            self.assertEqual(self.font.size, val)
        with self.assertRaises(ValueError):
            self.font.size = 'badvalue'
        with self.assertRaises(TecplotSystemError):
            self.font.size = -1
        with self.assertRaises(TecplotSystemError):
            self.font.size = 0

        self.font.size_units = Units.Point
        for val in [1,10,100,150]:
            self.font.size = val
            self.assertEqual(self.font.size, val)
        with self.assertRaises(ValueError):
            self.font.size = 'badvalue'
        with self.assertRaises(TecplotSystemError):
            self.font.size = -1
        with self.assertRaises(TecplotSystemError):
            self.font.size = 0

    def test_size_units(self):
        sz = self.font.size
        for val in [Units.Frame, Units.Point, Units.Frame]:
            self.font.size_units = val
            self.assertEqual(self.font.size_units, val)
            self.assertEqual(self.font.size, sz)
        with self.assertRaises(ValueError):
            self.font.size_units = 0.5
        self.assertEqual(self.font.size, sz)

    def test_typeface(self):
        for val in ['Times', 'Helvetica', 'Invalid Font Name']:
            self.font.typeface = val
            self.assertEqual(self.font.typeface, val)


if __name__ == '__main__':
    from .. import main
    main()
