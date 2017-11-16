import ctypes
import itertools as it
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
from tecplot.constant import *
from tecplot.exception import *
from tecplot import session

from test import patch_tecutil


class TestNodemap(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        nodes = ((0, 0, 0), (1, 0, 0.5), (0, 1, 0.5), (1, 1, 1))
        self.conn = ((0, 1, 2), (1, 3, 2))
        ds = tp.active_frame().create_dataset('Data', ['x','y','z'])
        z = ds.add_fe_zone(ZoneType.FETriangle,
                           name='FE Triangle Float (4,2) Nodal',
                           num_points=len(nodes), num_elements=len(self.conn))

        z.values('x')[:] = [n[0] for n in nodes]
        z.values('y')[:] = [n[1] for n in nodes]
        z.values('z')[:] = [n[2] for n in nodes]

        self.z = z

    def test_access(self):
        self.z.nodemap[:] = self.conn
        self.assertEqual(self.z.nodemap[0], [0, 1, 2])
        self.assertEqual(self.z.nodemap[1], [1, 3, 2])
        self.assertEqual(self.z.nodemap[:], [[0, 1, 2], [1, 3, 2]])
        self.assertEqual(self.z.nodemap[::2], [[0, 1, 2]])

    def test_raw_array(self):
        if tp.tecutil._tecutil_connector.connected:
            with self.assertRaises(TecplotLogicError):
                _ = self.z.nodemap._raw_array(False)
            with self.assertRaises(TecplotLogicError):
                _ = self.z.nodemap._raw_array(True)
        else:
            self.z.nodemap[:] = self.conn
            ro = self.z.nodemap._raw_array(False)
            self.assertEqual(list(ro), [0, 1, 2, 1, 3, 2])
            rw = self.z.nodemap._raw_array(True)
            self.assertEqual(list(rw), [0, 1, 2, 1, 3, 2])

    def test_alloc(self):
        self.z.nodemap.alloc()

        with patch_tecutil('DataNodeAlloc', return_value=False):
            with self.assertRaises(TecplotSystemError):
                self.z.nodemap.alloc()

    def test_eq(self):
        nm = self.z.nodemap
        z2 = self.z.dataset.add_fe_zone(ZoneType.FETriangle, 'Z', 4, 2)
        self.assertTrue(nm == self.z.nodemap)
        self.assertFalse(nm == z2.nodemap)
        self.assertFalse(nm != self.z.nodemap)
        self.assertTrue(nm != z2.nodemap)

    def test_len(self):
        self.assertEqual(len(self.z.nodemap), self.z.num_elements)

    def test_iter(self):
        self.z.nodemap[:] = self.conn
        self.assertEqual(len(self.z.nodemap), len(self.conn))
        for i, nmap in enumerate(self.z.nodemap):
            self.assertEqual(list(nmap), list(self.conn[i]))

    def test_shape(self):
        self.z.nodemap[:] = self.conn
        self.assertEqual(self.z.nodemap.shape,
                         (len(self.conn), len(self.conn[0])))

    def test_setitem(self):
        for i, nodes in enumerate(self.conn):
            self.z.nodemap[i] = nodes
        for i, nmap in enumerate(self.z.nodemap):
            self.assertEqual(list(nmap), list(self.conn[i]))

    def test_setitem_partial(self):
        self.z.nodemap.array[:] = [0] * self.z.nodemap.size
        self.z.nodemap[:1] = self.conn[:1]
        self.z.nodemap[1:] = self.conn[1:]
        for i, nmap in enumerate(self.z.nodemap):
            self.assertEqual(list(nmap), list(self.conn[i]))

    def test_num_elements(self):
        self.z.nodemap[:] = self.conn
        self.assertEqual(self.z.nodemap.num_elements(0), 1)
        self.assertEqual(self.z.nodemap.num_elements(1), 2)

    def test_element(self):
        nmap = self.z.nodemap
        nmap[:] = self.conn
        self.assertEqual(nmap.element(0, 0), 0)
        self.assertEqual(nmap.element(1, 0), 0)
        self.assertEqual(nmap.element(1, 1), 1)
        with self.assertRaises((TecplotLogicError, TecplotSystemError)):
            nmap.element(0, 1)
        with self.assertRaises((TecplotLogicError, TecplotSystemError)):
            nmap.element(4, 0)

    def test_array(self):
        nmap = self.z.nodemap
        nmap[:] = self.conn
        arr = nmap.array
        self.assertEqual(arr[0], self.conn[0][0])
        self.assertEqual(arr[3], self.conn[1][0])
        self.assertEqual(len(arr), nmap.size)

        if __debug__:
            with self.assertRaises(TecplotIndexError):
                arr[:1] = [-1]

        arr[0] = 3
        self.assertEqual(arr[0], 3)

        self.assertEqual(arr.shape, (len(arr),))

    def test_slicing(self):
        nmap = self.z.nodemap
        nmap[:] = self.conn
        arr = nmap.array
        nmap[::2] = [[2,1,0]]
        self.assertEqual(list(nmap[0]), [2, 1, 0])

        arr[:] = [0]*6
        self.assertEqual(list(arr), [0]*6)
        arr[::2] = [1]*3
        self.assertEqual(arr[::2], [1]*3)



if __name__ == '__main__':
    from .. import main
    main()
