import os
import unittest

import tecplot as tp
from tecplot.exception import *
from tecplot.constant import *

from ..sample_data import sample_data


class TestScatter(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename,self.dataset = sample_data('10x10x10')
        frame = tp.active_frame()
        frame.plot_type = PlotType.Cartesian3D
        self.scatter = frame.plot().scatter

    def tearDown(self):
        os.remove(self.filename)

    def test_variable(self):
        for v in self.dataset.variables():
            self.scatter.variable = v
            self.assertEqual(self.scatter.variable, v)
            self.assertEqual(self.scatter.variable_index, v.index)

            self.scatter.variable_index = v.index
            self.assertEqual(self.scatter.variable, v)
            self.assertEqual(self.scatter.variable_index, v.index)


class TestTextSymbol(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename,dataset = sample_data('xylines_poly')
        frame = tp.active_frame()
        frame.plot_type = PlotType.XYLine
        plot = frame.plot()
        zone = dataset.zone(0)
        x = dataset.variable('X')
        plot.add_linemap('p', zone, x, dataset.variable('P'))
        sym = frame.plot().linemap(0).symbols
        sym.symbol_type = SymbolType.Text
        self.symbol = sym.symbol()

    def tearDown(self):
        os.remove(self.filename)

    def test_text(self):
        for c in ['a','1',1,0,True,False,'abc']:
            self.symbol.text = c
            self.assertEqual(self.symbol.text, str(c)[0])
        with self.assertRaises(IndexError):
            self.symbol.text = ''

    def test_typeface(self):
        for val in [True, False, True]:
            self.symbol.use_base_font = val
            self.assertEqual(self.symbol.use_base_font, val)

        for c in [tp.constant.Font.Greek, tp.constant.Font.Math,
                  tp.constant.Font.UserDefined]:
            self.symbol.font_override = c
            self.assertEqual(self.symbol.font_override, c)
        if __debug__:
            with self.assertRaises(TecplotLogicError):
                self.symbol.font_override = 0.5
            with self.assertRaises(TecplotLogicError):
                self.symbol.font_override = tp.constant.Font.Helvetica
        else:
            with self.assertRaises(ValueError):
                self.symbol.font_override = 0.5


class TestGeometrySymbol(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename,dataset = sample_data('xylines_poly')
        frame = tp.active_frame()
        frame.plot_type = PlotType.XYLine
        plot = frame.plot()
        zone = dataset.zone(0)
        x = dataset.variable('X')
        plot.add_linemap('p', zone, x, dataset.variable('P'))
        sym = frame.plot().linemap(0).symbols
        sym.symbol_type = SymbolType.Geometry
        self.symbol = sym.symbol()

    def tearDown(self):
        os.remove(self.filename)

    def test_shape(self):
        for c in [GeomShape.Circle, GeomShape.Square]:
            self.symbol.shape = c
            self.assertEqual(self.symbol.shape, c)
        with self.assertRaises(ValueError):
            self.symbol.shape = 0.5


class TestTextScatterSymbol(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename,dataset = sample_data('10x10x10')
        frame = tp.active_frame()
        frame.plot_type = PlotType.Cartesian3D
        self.plot = frame.plot()
        fmap = self.plot.fieldmap(0)
        fmap.scatter.symbol_type = SymbolType.Text
        self.symbol = fmap.scatter.symbol()

    def tearDown(self):
        os.remove(self.filename)

    def test_text(self):
        for c in ['a','1',1,0,True,False,'abc']:
            self.symbol.text = c
            self.assertEqual(self.symbol.text, str(c)[0])
        with self.assertRaises(IndexError):
            self.symbol.text = ''

    def test_typeface(self):
        for val in [True, False, True]:
            self.symbol.use_base_font = val
            self.assertEqual(self.symbol.use_base_font, val)

        for c in [tp.constant.Font.Greek, tp.constant.Font.Math,
                  tp.constant.Font.UserDefined]:
            self.symbol.font_override = c
            self.assertEqual(self.symbol.font_override, c)
        if __debug__:
            with self.assertRaises(TecplotLogicError):
                self.symbol.font_override = 0.5
            with self.assertRaises(TecplotLogicError):
                self.symbol.font_override = tp.constant.Font.Helvetica
        else:
            with self.assertRaises(ValueError):
                self.symbol.font_override = 0.5


class TestGeometryScatterSymbol(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.filename,dataset = sample_data('10x10x10')
        frame = tp.active_frame()
        frame.plot_type = PlotType.Cartesian3D
        self.plot = frame.plot()
        fmap = self.plot.fieldmap(0)
        fmap.scatter.symbol_type = SymbolType.Geometry
        self.symbol = fmap.scatter.symbol()

    def tearDown(self):
        os.remove(self.filename)

    def test_shape(self):
        for c in [GeomShape.Circle, GeomShape.Square]:
            self.symbol.shape = c
            self.assertEqual(self.symbol.shape, c)
        with self.assertRaises(ValueError):
            self.symbol.shape = 0.5


if __name__ == '__main__':
    from .. import main
    main()
