# coding: utf-8
from __future__ import unicode_literals

import base64
import os
import platform
import sys
import unittest
import zlib

from contextlib import contextmanager
from ctypes import *
from tempfile import NamedTemporaryFile
from unittest.mock import patch, Mock

import tecplot as tp
from tecplot import session
from tecplot.constant import *
from tecplot.exception import *

from test import patch_tecutil
from ..sample_data import sample_data_file, loaded_sample_data

class TestVariable(unittest.TestCase):

    def setUp(self):
        self.filename = sample_data_file('10x10x10')

    def tearDown(self):
        os.remove(self.filename)

    def test_str(self):
        tp.new_layout()
        ds = tp.data.load_tecplot(self.filename)
        z = ds.variable(0)
        self.assertRegex(str(z), r'X')

    def test_repr(self):
        tp.new_layout()
        ds = tp.data.load_tecplot(self.filename)
        z = ds.variable(0)
        self.assertRegex(repr(z), r'Variable\(.*')

    def test_eq(self):
        tp.new_layout()
        ds = tp.active_frame().create_dataset('D', ['x','y'])
        v0,v1 = ds.variable('x'), ds.variable('y')
        self.assertTrue( ds.variable(0) == v0)
        self.assertFalse(ds.variable(0) != v0)
        self.assertFalse(ds.variable(0) == v1)
        self.assertTrue( ds.variable(0) != v1)

    def test_aux_data(self):
        tp.new_layout()
        ds = tp.active_frame().create_dataset('D', ['x','y'])
        v0,v1 = ds.variable('x'), ds.variable('y')
        self.assertIsInstance(v0.aux_data, session.AuxData)
        self.assertEqual(v0.aux_data.object_type, AuxDataObjectType.Variable)

    def test_index(self):
        tp.new_layout()
        ds = tp.active_frame().create_dataset('D', ['x','y'])
        v0,v1 = ds.variable('x'), ds.variable('y')
        self.assertEqual(v0.index, 0)
        self.assertEqual(v1.index, 1)

    def test_limits(self):
        tp.new_layout()
        with loaded_sample_data('3x3x3_p') as ds:
            v = ds.variable('P')
            self.assertAlmostEqual(v.min(), -1.0)
            self.assertAlmostEqual(v.max(), 2.0)
            self.assertAlmostEqual(v.minmax()[0], -1.0)
            self.assertAlmostEqual(v.minmax()[1], 2.0)

            v.values(0)[0] = -1000
            v.values(0)[1] = 1000
            self.assertAlmostEqual(v.min(), -1000, 6)
            self.assertAlmostEqual(v.max(), 1000, 6)

    def test_name(self):
        tp.new_layout()
        ds = tp.data.load_tecplot(self.filename)
        xvar = ds.variable('X')
        self.assertEqual(xvar.name, 'X')
        xvar.name = 'Xα'
        self.assertEqual(xvar.name, 'Xα')
        xvar = ds.variable('Xα')
        self.assertEqual(xvar.name, 'Xα')
        xvar.name = ''
        self.assertEqual(xvar.name, '')

        with self.assertRaises((TecplotLogicError, TecplotSystemError)):
            xvar.name = None

        xvar.dataset.uid += 1 # trick this variable to point to a non-existant dataset
        with self.assertRaises((TecplotLogicError, TecplotSystemError)):
            xvar.name
        with self.assertRaises((TecplotLogicError, TecplotSystemError)):
            xvar.name = 'Test'

        with patch_tecutil('VarGetNameByDataSetID', return_value=(False,'')):
            with self.assertRaises(TecplotSystemError):
                n = xvar.name

    def test_num_zones(self):
        tp.new_layout()
        ds = tp.active_frame().create_dataset('D', ['x','y'])
        v = ds.variable(0)
        z = ds.add_ordered_zone('Z1', (3,))
        self.assertEqual(v.num_zones, 1)
        z = ds.add_ordered_zone('Z1', (3,))
        self.assertEqual(v.num_zones, 2)

    def test_values(self):
        tp.new_layout()
        ds = tp.active_frame().create_dataset('D', ['x','y'])
        z = ds.add_ordered_zone('Z1', (3,))
        v = ds.variable(0)
        a = v.values('Z1')
        self.assertIsInstance(a, tp.data.Array)
        self.assertEqual(a.zone, z)
        self.assertEqual(a.variable, v)

        x = ds.variable('x')
        z = ds.zone(0)
        a = z.values('x')
        self.assertEqual(x.values(z), a)
        self.assertEqual(x.values(z), z.values(x))


if __name__ == '__main__':
    from .. import main
    main()
