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


class TestLocalOneToOneFaceNeighbors(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        nodes = (
            (0, 0, 0  ), # node 0
            (1, 0, 0.5), # node 1
            (0, 1, 0.5), # ...
            (1, 0, 0.5),
            (0, 1, 0.5),
            (1, 1, 1  ))

        conn = (
            (0, 1, 2), # element 0 consisting of faces (node connections) 0-1, 1-2, 2-0
            (3, 5, 4),
            #(1, 3, 2), # elements 2 and 3 are created to indicate elements 0 and 1 are
            #(2, 3, 4), # face neighbors
            )

        # Create the dataset and zones
        ds = tp.active_frame().create_dataset('Data', ['x','y','z'])
        z = ds.add_fe_zone(ZoneType.FETriangle,
                            name='FE Triangle Float (4,2) Nodal',
                            num_points=len(nodes), num_elements=len(conn))

        # Fill in node locations
        z.values('x')[:] = [n[0] for n in nodes]
        z.values('y')[:] = [n[1] for n in nodes]
        z.values('z')[:] = [n[2] for n in nodes]

        # Set the nodemap
        z.nodemap[:] = conn

        self.z = z

    def test_no_neighbors(self):
        with self.z.face_neighbors.assignment():
            pass
        fn = self.z.face_neighbors
        for elem in range(2):
            for face in range(3):
                face_neighbors = fn.neighbors(elem, face)
                self.assertEqual(len(face_neighbors), 0)

    def test_eq(self):
        fn0 = self.z.face_neighbors
        neighbors = ((None, None, [1]), ([0], None, None))
        self.z.face_neighbors.set_neighbors(neighbors)
        fn1 = self.z.face_neighbors
        self.assertTrue(fn0 == self.z.face_neighbors)
        self.assertTrue(fn1 == self.z.face_neighbors)
        self.assertTrue(fn0 == fn1)
        self.assertFalse(fn0 != self.z.face_neighbors)
        self.assertFalse(fn1 != self.z.face_neighbors)
        self.assertFalse(fn0 != fn1)

    def test_mode(self):
        self.assertIsInstance(self.z.face_neighbors.mode, FaceNeighborMode)
        self.assertEqual(self.z.face_neighbors.mode,
                         FaceNeighborMode.LocalOneToOne)

    def test_set_neighbors(self):
        neighbors = (
            (None, 1, None),
            (None, None, 0))
        fn = self.z.face_neighbors
        fn.set_neighbors(neighbors, obscures=True)
        for elem in range(2):
            for face in range(3):
                face_neighbors = fn.neighbors(elem, face)
                if (elem,face) in [(0,1), (1,2)]:
                    self.assertEqual(len(face_neighbors), 1)
                    self.assertEqual(face_neighbors[0],
                        tp.data.FaceNeighbors._Neighbor((elem+1)%2, None))
                else:
                    self.assertEqual(len(face_neighbors), 0)

        with self.assertRaises((TecplotLogicError, TecplotSystemError)):
            zones = ((0,0,0), (0,0,0))
            fn.set_neighbors(neighbors, zones)

        with self.assertRaises((TecplotLogicError, IndexError)):
            zones = ((0,[0,1],0), (0,0,0))
            fn.set_neighbors(neighbors, zones)

        with patch_tecutil('DataFaceNbrAssignByRef', return_value=False):
            with self.assertRaises(TecplotSystemError):
                fn.set_neighbors(neighbors)

        neighbors = (
            (None, 8, None),
            (None, None, 0))
        fn = self.z.face_neighbors
        if __debug__:
            with self.assertRaises(TecplotIndexError):
                fn.set_neighbors(neighbors)

    def test_local_neighbors(self):
        fn = self.z.face_neighbors
        neighbors = ((None, 1, None), (None, None, 0))
        with fn.assignment():
            fn.add_local_neighbors(neighbors)
        for elem in range(2):
            for face in range(3):
                face_neighbors = fn.neighbors(elem, face)
                if (elem,face) in [(0,1), (1,2)]:
                    self.assertEqual(len(face_neighbors), 1)
                    self.assertEqual(face_neighbors[0],
                        tp.data.FaceNeighbors._Neighbor((elem+1)%2, None))
                else:
                    self.assertEqual(len(face_neighbors), 0)

        if __debug__:
            with self.assertRaises(TecplotIndexError):
                with fn.assignment():
                    fn.add_local_neighbors(((-2,1,-1), (-1,-1,0)))

    def test_assignment_failure(self):
        fn = self.z.face_neighbors
        with patch_tecutil('DataFaceNbrBeginAssign', return_value=False):
            with self.assertRaises(TecplotSystemError):
                with fn.assignment():
                    pass

        with patch_tecutil('DataFaceNbrBeginAssign', return_value=True):
            with patch_tecutil('DataFaceNbrEndAssign') as end:
                with self.assertRaises(Exception):
                    with fn.assignment():
                        raise Exception
        self.assertEqual(end.call_count, 1)

    def test_is_obscured(self):
        neighbors = ((None, 1, None), (None, None, 0))
        obs = ((False, True, False), (False, False, False))
        fn = self.z.face_neighbors
        fn.set_neighbors(neighbors, obscures=obs)
        fr = self.z.dataset.frame
        fr.plot_type = PlotType.Cartesian3D
        self.assertFalse(fn.is_obscured(0, 0))
        self.assertTrue(fn.is_obscured(0, 1))
        self.assertTrue(fn.is_obscured(0, 1, fr.active_zones()))
        self.assertFalse(fn.is_obscured(1, 2))


class TestGlobalOneToOneFaceNeighbors(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        nodes0 = (
            (0, 0, 0  ),
            (1, 0, 0.5),
            (0, 1, 0.5))
        scalar_data0 = (0, 1, 2)
        conn0 = ((0, 1, 2),)

        # Triangle 1
        nodes1 = (
            (1, 0, 0.5),
            (0, 1, 0.5),
            (1, 1, 1  ))
        scalar_data1 = (1, 2, 3)
        conn1 = ((0, 1, 2),)

        # Create the dataset and zones
        ds = tp.active_frame().create_dataset('Data', ['x','y','z','s'])
        z0 = ds.add_fe_zone(ZoneType.FETriangle,
                            name='FE Triangle Float (3,1) Nodal 0',
                            num_points=len(nodes0), num_elements=len(conn0),
                            face_neighbor_mode=FaceNeighborMode.GlobalOneToOne)
        z1 = ds.add_fe_zone(ZoneType.FETriangle,
                            name='FE Triangle Float (3,1) Nodal 1',
                            num_points=len(nodes1), num_elements=len(conn1),
                            face_neighbor_mode=FaceNeighborMode.GlobalOneToOne)

        # Fill in and connect first triangle
        z0.values('x')[:] = [n[0] for n in nodes0]
        z0.values('y')[:] = [n[1] for n in nodes0]
        z0.values('z')[:] = [n[2] for n in nodes0]
        z0.nodemap[:] = conn0
        z0.values('s')[:] = scalar_data0

        # Fill in and connect second triangle
        z1.values('x')[:] = [n[0] for n in nodes1]
        z1.values('y')[:] = [n[1] for n in nodes1]
        z1.values('z')[:] = [n[2] for n in nodes1]
        z1.nodemap[:] = conn1
        z1.values('s')[:] = scalar_data1

        self.z0 = z0
        self.z1 = z1

    def test_no_neighbors(self):
        z0, z1 = self.z0, self.z1
        for z in [z0, z1]:
            with z.face_neighbors.assignment():
                pass
            fn = z.face_neighbors
            for face in range(3):
                face_neighbors = fn.neighbors(0, face)
                self.assertEqual(len(face_neighbors), 0)

    def test_eq(self):
        neighbors0 = ((None, 0, None),)
        neighbor_zones0 = ((None, 1, None),)
        neighbors1 = ((0, None, None),)
        neighbor_zones1 = ((0, None, None),)
        self.z0.face_neighbors.set_neighbors(neighbors0, neighbor_zones0, True)
        self.z1.face_neighbors.set_neighbors(neighbors1, neighbor_zones1, True)

        z0, z1 = self.z0, self.z1
        fn0, fn1 = z0.face_neighbors, z1.face_neighbors

        self.assertFalse(fn0 == fn1)
        self.assertTrue(fn0 != fn1)

    def test_mode(self):
        for z in [self.z0, self.z1]:
            self.assertIsInstance(z.face_neighbors.mode, FaceNeighborMode)
            self.assertEqual(z.face_neighbors.mode,
                             FaceNeighborMode.GlobalOneToOne)

    def test_set_neighbors(self):
        neighbors0 = ((None, 0, None),)
        neighbor_zones0 = ((None, 1, None),)
        neighbors1 = ((0, None, None),)
        neighbor_zones1 = ((0, None, None),)
        self.z0.face_neighbors.set_neighbors(neighbors0, neighbor_zones0, True)
        self.z1.face_neighbors.set_neighbors(neighbors1, neighbor_zones1, True)

        z0, z1 = self.z0, self.z1
        fn0, fn1 = z0.face_neighbors, z1.face_neighbors

        for zi,z in enumerate([z0, z1]):
            for face in range(3):
                face_neighbors = z.face_neighbors.neighbors(0, face)
                if (zi,face) in [(0,1), (1,0)]:
                    self.assertEqual(len(face_neighbors), 1)
                    nz = self.z0.dataset.zone((zi+1)%2)
                    self.assertEqual(face_neighbors[0],
                        tp.data.FaceNeighbors._Neighbor(0, nz))
                else:
                    self.assertEqual(len(face_neighbors), 0)

        with self.assertRaises((TecplotLogicError, TecplotSystemError)):
            fn0.set_neighbors(neighbors0)

        with self.assertRaises((TecplotLogicError, IndexError)):
            zones = ((0,[0,2],0), (0,0,0))
            fn0.set_neighbors(neighbors0, zones)

        with patch_tecutil('DataFaceNbrAssignByRef', return_value=False):
            with self.assertRaises(TecplotSystemError):
                fn0.set_neighbors(neighbors0)

        if __debug__:
            nbrs = ((None, 8, None),)
            nzones = ((None, 1, None),)
            with self.assertRaises(TecplotIndexError):
                self.z0.face_neighbors.set_neighbors(nbrs, nzones)

            nbrs = ((None, 0, None),)
            nzones = ((None, 4, None),)
            with self.assertRaises(TecplotIndexError):
                self.z0.face_neighbors.set_neighbors(nbrs, nzones)

    def test_is_obscured(self):
        neighbors0 = ((None, 0, None),)
        neighbor_zones0 = ((None, 1, None),)
        obs0 = ((False, True, False),)
        neighbors1 = ((0, None, None),)
        neighbor_zones1 = ((0, None, None),)
        obs1 = ((False, False, False),)
        self.z0.face_neighbors.set_neighbors(neighbors0, neighbor_zones0, obs0)
        self.z1.face_neighbors.set_neighbors(neighbors1, neighbor_zones1, obs1)

        z0, z1 = self.z0, self.z1
        fn0, fn1 = z0.face_neighbors, z1.face_neighbors

        fr = self.z0.dataset.frame
        fr.plot_type = PlotType.Cartesian3D
        self.assertFalse(fn0.is_obscured(0, 0))
        self.assertTrue(fn0.is_obscured(0, 1))
        self.assertTrue(fn0.is_obscured(0, 1, fr.active_zones()))
        self.assertFalse(fn1.is_obscured(0, 2))


class TestLocalOneToManyFaceNeighbors(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        nodes = (
            ( 0  ,  0  , 0  ),
            (-0.4, -0.4, 0.5),
            ( 0  ,  0  , 0.5),
            ( 0.4,  0.4, 0.5),
            (-0.2, -0.2, 1  ),
            ( 0.2,  0.2, 1  ))
        conn = (
            (0, 3, 1),
            (1, 2, 4),
            (2, 3, 5),
            (2, 5, 4))

        # Create the dataset and zones
        ds = tp.active_frame().create_dataset('Data', ['x','y','z'])
        z = ds.add_fe_zone(ZoneType.FETriangle,
                            name='FE Triangle Float (6,4) Nodal',
                            num_points=len(nodes), num_elements=len(conn),
                            face_neighbor_mode=FaceNeighborMode.LocalOneToMany)

        # Fill in node locations
        z.values('x')[:] = [n[0] for n in nodes]
        z.values('y')[:] = [n[1] for n in nodes]
        z.values('z')[:] = [n[2] for n in nodes]
        z.nodemap[:] = conn

        self.z = z
        z.dataset.frame.plot_type = PlotType.Cartesian3D

    def test_set_neighbors(self):
        fn = self.z.face_neighbors
        neighbors = (
            (-1, [1,2], -1),
            ( 0, -1   , -1),
            ( 0, -1   , -1),
            (-1, -1   , -1))
        obscures = (True, True, True, False)
        fn.set_neighbors(neighbors, obscures=obscures)

        def _neighbors(fn, face, elem):
            return [n.element for n in fn.neighbors(face, elem)]

        self.assertEqual(_neighbors(fn,0,0), [])
        self.assertEqual(_neighbors(fn,0,1), [1,2])
        self.assertEqual(_neighbors(fn,0,2), [])
        self.assertEqual(_neighbors(fn,1,0), [0])
        self.assertEqual(_neighbors(fn,1,1), [3])
        self.assertEqual(_neighbors(fn,1,2), [])
        self.assertEqual(_neighbors(fn,2,0), [0])
        self.assertEqual(_neighbors(fn,2,1), [])
        self.assertEqual(_neighbors(fn,2,2), [3])
        self.assertEqual(_neighbors(fn,3,0), [2])
        self.assertEqual(_neighbors(fn,3,1), [])
        self.assertEqual(_neighbors(fn,3,2), [1])

    def test_is_obscured(self):
        fn = self.z.face_neighbors
        neighbors = (
            (-1, [1,2], -1),
            (0, -1, -1),
            (0, -1, -1),
            (-1, -1, -1))
        fn.set_neighbors(neighbors, obscures=True)
        self.assertTrue(fn.is_obscured(2,0))
        neighbors = (
            (-1, [1,2], -1),
            (0, -1, -1),
            (0, -1, -1),
            (-1, -1, -1))
        fn.set_neighbors(neighbors, obscures=False)
        self.assertFalse(fn.is_obscured(2,0))


class TestGlobalOneToManyFaceNeighbors(unittest.TestCase):
    def setUp(self):
        tp.new_layout()

        nodes0 = (
            ( 0  ,  0  , 0  ),
            (-0.4, -0.4, 0.5),
            ( 0.4,  0.4, 0.5))
        conn0 = ((0, 2, 1),)

        nodes1 = (
            (-0.4, -0.4, 0.5),
            ( 0  ,  0  , 0.5),
            ( 0.4,  0.4, 0.5),
            (-0.2, -0.2, 1  ),
            ( 0.2,  0.2, 1  ))
        conn1 = (
            (0, 1, 3),
            (1, 2, 4),
            (1, 4, 3))

        # Create the dataset and zones
        ds = tp.active_frame().create_dataset('Data', ['x','y','z'])
        z0 = ds.add_fe_zone(ZoneType.FETriangle,
                            name='FE Triangle Float (3,1) Nodal',
                            num_points=len(nodes0), num_elements=len(conn0),
                            face_neighbor_mode=FaceNeighborMode.GlobalOneToMany)
        z1 = ds.add_fe_zone(ZoneType.FETriangle,
                            name='FE Triangle Float (5,3) Nodal',
                            num_points=len(nodes1), num_elements=len(conn1),
                            face_neighbor_mode=FaceNeighborMode.GlobalOneToMany)

        # Fill in and connect first triangle
        z0.values('x')[:] = [n[0] for n in nodes0]
        z0.values('y')[:] = [n[1] for n in nodes0]
        z0.values('z')[:] = [n[2] for n in nodes0]
        z0.nodemap[:] = conn0

        # Fill in and connect second triangle
        z1.values('x')[:] = [n[0] for n in nodes1]
        z1.values('y')[:] = [n[1] for n in nodes1]
        z1.values('z')[:] = [n[2] for n in nodes1]
        z1.nodemap[:] = conn1

        self.z0 = z0
        self.z1 = z1

    def test_set_neighbors(self):
        z0, z1 = self.z0, self.z1
        fn0, fn1 = z0.face_neighbors, z1.face_neighbors

        neighbors0 = ((None, [0,1], None),)
        neighbor_zones0 = ((None, [1,1], None),)
        obscures0 = (True,)
        fn0.set_neighbors(neighbors0, neighbor_zones0, obscures0)

        neighbors1 = (
            (0, None, None),
            (0, -1, None),
            (None, None, None))
        neighbor_zones1 = (
            (0, None, None),
            (0, None, None),
            (None, None, None))
        obscures1 = (True, True, False)
        fn1.set_neighbors(neighbors1, neighbor_zones1, obscures1)

        n0 = [fn0.neighbors(e,f) for e,f in it.product(range(1),range(3))]
        n1 = [fn1.neighbors(e,f) for e,f in it.product(range(3),range(3))]


        self.assertEqual([n.element for n in n0[0]], [])
        self.assertEqual([n.element for n in n0[1]], [0,1])
        self.assertEqual([n.element for n in n0[2]], [])
        self.assertEqual([n.element for n in n1[0]], [0])
        self.assertEqual([n.element for n in n1[1]], [2]) # set by Tecplot
        self.assertEqual([n.element for n in n1[2]], [])
        self.assertEqual([n.element for n in n1[3]], [0])
        self.assertEqual([n.element for n in n1[4]], [])


if __name__ == '__main__':
    from .. import main
    main()
