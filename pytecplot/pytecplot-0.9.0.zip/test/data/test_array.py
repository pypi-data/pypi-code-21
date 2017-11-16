# coding: utf-8
from __future__ import unicode_literals

import ctypes
import numpy as np
import os
import platform
import sys
import unittest
import six

from collections import namedtuple
from contextlib import contextmanager
from ctypes import *
from os import path
from textwrap import dedent
from unittest.mock import patch, Mock

import tecplot as tp
from tecplot import session
from tecplot.constant import *
from tecplot.exception import *
from tecplot.tecutil import _tecutil_connector

from test import patch_tecutil, skip_on
from ..sample_data import sample_data_file


class TestArray(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        self.ds = tp.active_frame().create_dataset('D', ['x'])
        self.ds.add_ordered_zone('Z0', (3,))
        self.ds.add_ordered_zone('Z1', (3,3))
        self.ds.add_ordered_zone('Z2', (3,3,3))
        self.ds.add_ordered_zone('Z3', (1,1,3))
        self.ds.add_fe_zone(ZoneType.FEQuad, 'Z4', 8, 3)
        self.ds.add_poly_zone(ZoneType.FEPolyhedron, 'Z5', 8, 1, 12)
        self.ds.add_variable('n', FieldDataType.Double,
                             locations=ValueLocation.Nodal)
        self.ds.add_variable('c', FieldDataType.Int32,
                             locations=ValueLocation.CellCentered)

    def test_native_ref(self):
        rref = self.ds.zone(0).values(0)._native_reference(False)
        self.assertIsInstance(rref, six.integer_types)
        wref = self.ds.zone(0).values(0)._native_reference(True)
        self.assertIsInstance(wref, six.integer_types)
        self.assertEqual(rref, wref)
        self.assertEqual(self.ds.zone(0).values(0)._native_reference(), rref)

    def test_raw_pointer(self):
        if _tecutil_connector.connected:
            with self.assertRaises(TecplotLogicError):
                rptr = self.ds.zone(0).values(0)._raw_pointer(False)
        else:
            rptr = self.ds.zone(0).values(0)._raw_pointer(False)
            self.assertIsInstance(rptr, ctypes.POINTER(ctypes.c_float))
            wptr = self.ds.zone(0).values(0)._raw_pointer(True)
            self.assertIsInstance(wptr, ctypes.POINTER(ctypes.c_float))
            self.assertEqual(rptr[0], wptr[0])

            ptr = self.ds.zone(0).values(1)._raw_pointer()
            self.assertIsInstance(ptr, ctypes.POINTER(ctypes.c_double))

            ptr = self.ds.zone(0).values(2)._raw_pointer()
            self.assertIsInstance(ptr, ctypes.POINTER(ctypes.c_int32))

    def test_eq(self):
        x = self.ds.zone(0).values(0)
        n = self.ds.zone(0).values(1)
        self.assertTrue (x == self.ds.zone(0).values(0))
        self.assertFalse(x != self.ds.zone(0).values(0))
        self.assertFalse(n == x)
        self.assertTrue (n != x)

    def test_len(self):
        self.assertEqual(len(self.ds.zone(0).values(0)), 3)
        self.assertEqual(len(self.ds.zone(0).values(1)), 3)
        self.assertEqual(len(self.ds.zone(0).values(2)), 2)
        self.assertEqual(len(self.ds.zone(2).values(0)), 3*3*3)
        self.assertEqual(len(self.ds.zone(2).values(1)), 3*3*3)
        self.assertEqual(len(self.ds.zone(2).values(2)), 2*3*3)

    def test_shape(self):
        self.assertEqual(self.ds.zone(0).values(0).shape, (3,))
        self.assertEqual(self.ds.zone(0).values(1).shape, (3,))
        self.assertEqual(self.ds.zone(0).values(2).shape, (2,))
        self.assertEqual(self.ds.zone(2).values(0).shape, (3,3,3))
        self.assertEqual(self.ds.zone(2).values(1).shape, (3,3,3))
        self.assertEqual(self.ds.zone(2).values(2).shape, (2,2,2))
        self.assertEqual(self.ds.zone(3).values(0).shape, (3,))
        self.assertEqual(self.ds.zone(3).values(2).shape, (2,))

        self.assertEqual(self.ds.zone(4).values(0).shape, (8,))
        self.assertEqual(self.ds.zone(4).values(2).shape, (7,))
        self.assertEqual(self.ds.zone(5).values(0).shape, (8,))
        self.assertEqual(self.ds.zone(5).values(2).shape, (7,))

        small_zone = self.ds.add_ordered_zone('small zone', (1,))
        self.assertEqual(small_zone.values(0).shape, (1,))

    def test_c_type(self):
        self.assertEqual(self.ds.zone(0).values(0).c_type, ctypes.c_float)
        self.assertEqual(self.ds.zone(0).values(1).c_type, ctypes.c_double)
        self.assertEqual(self.ds.zone(0).values(2).c_type, ctypes.c_int32)
        self.assertEqual(self.ds.zone(1).values(0).c_type, ctypes.c_float)
        self.assertEqual(self.ds.zone(1).values(1).c_type, ctypes.c_double)
        self.assertEqual(self.ds.zone(1).values(2).c_type, ctypes.c_int32)
        self.assertEqual(self.ds.zone(2).values(0).c_type, ctypes.c_float)
        self.assertEqual(self.ds.zone(2).values(1).c_type, ctypes.c_double)
        self.assertEqual(self.ds.zone(2).values(2).c_type, ctypes.c_int32)

    def test_data_type(self):
        self.assertEqual(self.ds.zone(0).values(0).data_type, FieldDataType.Float)
        self.assertEqual(self.ds.zone(1).values(0).data_type, FieldDataType.Float)
        self.assertEqual(self.ds.zone(2).values(0).data_type, FieldDataType.Float)
        self.assertEqual(self.ds.zone(0).values(1).data_type, FieldDataType.Double)
        self.assertEqual(self.ds.zone(1).values(1).data_type, FieldDataType.Double)
        self.assertEqual(self.ds.zone(2).values(1).data_type, FieldDataType.Double)
        self.assertEqual(self.ds.zone(0).values(2).data_type, FieldDataType.Int32)
        self.assertEqual(self.ds.zone(1).values(2).data_type, FieldDataType.Int32)
        self.assertEqual(self.ds.zone(2).values(2).data_type, FieldDataType.Int32)

    def test_copy(self):
        x = self.ds.zone(0).values(0)
        x[0] = 3.1415
        xcopy = x.copy()
        self.assertNotEqual(x, xcopy)
        self.assertEqual(x[0], xcopy[0])

    def test_slice_range(self):
        x = self.ds.zone(0).values(0)
        self.assertEqual(list(x._slice_range(slice(len(x)))),
                         list(range(0,len(x),1)))
        self.assertEqual(list(x._slice_range(slice(1))),
                         list(range(0,1,1)))
        self.assertEqual(list(x._slice_range(slice(0,2))),
                         list(range(0,2,1)))
        self.assertEqual(list(x._slice_range(slice(None,None,2))),
                         list(range(0,len(x),2)))

        with self.assertRaises((TecplotIndexError, TecplotSystemError)):
            x[:4096] = np.zeros(len(x))

    def test_get_set_item(self):
        x = self.ds.zone(2).values(0)
        x[0] = 3.1415
        self.assertAlmostEqual(x[0], 3.1415)
        x[:2] = [5,6]
        self.assertAlmostEqual(x[0], 5)
        self.assertAlmostEqual(x[1], 6)
        x[:3:2] = [8,9]
        self.assertAlmostEqual(x[0], 8)
        self.assertAlmostEqual(x[2], 9)
        arr = x[:3:2]
        self.assertAlmostEqual(arr[0], 8)
        self.assertAlmostEqual(arr[1], 9)
        #x[-1] = 6.28
        #self.assertAlmostEqual(x[len(x)-1], 6.28)
        #self.assertAlmostEqual(x[-1], 6.28)

    def test_iter(self):
        x = self.ds.zone(2).values(0)
        data = list(range(len(x)))
        x[:] = data
        for i,d in zip(x,data):
            self.assertAlmostEqual(i,d)

    def test_limits(self):
        x = self.ds.zone(2).values(0)
        data = list(range(len(x)))
        x[:] = data
        self.assertAlmostEqual(x.min(), 0)
        self.assertAlmostEqual(x.max(), len(x)-1)
        self.assertAlmostEqual(x.minmax()[0], 0)
        self.assertAlmostEqual(x.minmax()[1], len(x)-1)

        x[3] = -3.14
        x[5] = 4096
        self.assertAlmostEqual(x.min(), -3.14, 6)
        self.assertAlmostEqual(x.max(), 4096, 6)

    def test_shared_zones(self):
        z = self.ds.zone(0)
        z2 = z.copy(True)
        self.assertEqual(z.values(0).shared_zones, [z,z2])
        self.assertEqual(z.values(0), z2.values(0))

    @skip_on(TecplotOutOfDateEngineError)
    def test_passiveness(self):
        tp.new_layout()
        ds = tp.active_page().add_frame().create_dataset('D', ['x','y'])
        z = ds.add_ordered_zone('Z1', (3,))
        zcopy1 = z.copy(True)
        ds.branch_variables(z,0, copy_data=False)
        self.assertEqual(z.values(0).shared_zones, [])
        self.assertEqual(z.values(0).passive, True)


if __name__ == '__main__':
    from .. import main
    main()
