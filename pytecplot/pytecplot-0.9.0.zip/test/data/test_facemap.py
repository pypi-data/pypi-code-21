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

from test import patch_tecutil, skip_on, skip_if_sdk_version_before


@skip_if_sdk_version_before(2017, 3)
class TestFacemapPolygons(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        nodes = ((0, 0, 0  ),
                 (1, 0, 0.5),
                 (0, 1, 0.5),
                 (1, 1, 1  ))

        ds = tp.active_frame().create_dataset('Data', ['x','y','z'])
        z = ds.add_poly_zone(ZoneType.FEPolygon,
                             name='FE Polygon Float (4,2,5) Nodal',
                             num_points=len(nodes),
                             num_elements=2,
                             num_faces=5)

        z.values('x')[:] = [n[0] for n in nodes]
        z.values('y')[:] = [n[1] for n in nodes]
        z.values('z')[:] = [n[2] for n in nodes]

        self.z = z
        self.assertTrue(bool(self.z.facemap))
        self.assertTrue(self.z.facemap._has_data_backing)
        self.assertIsNotNone(self.z.facemap.node_c_type)
        self.assertIsNotNone(self.z.facemap.element_c_type)
        self.assertEqual(self.z.facemap.num_faces(), 5)
        self.assertEqual(self.z.facemap.num_unique_nodes, len(nodes))
        with self.assertRaises(TecplotNotImplementedError):
            self.assertEqual(self.z.facemap.num_nodes(), 10)

    def test_connections(self):
        faces = ((0, 1), (1, 2), (2, 0), (1, 3), (3, 2))
        elements = ((0, 0, 0, 1, 1), (-1, 1, -1, -1, -1))
        fm = self.z.facemap
        fm.set_mapping(faces, elements)
        self.assertTrue(fm._has_data_backing)
        self.assertTrue(fm == self.z.facemap)
        self.assertEqual(fm, self.z.facemap)
        self.assertEqual(len(fm), fm.num_faces())
        self.assertEqual(fm.num_faces(), 5)
        self.assertEqual(fm.num_faces(0), 3)
        self.assertEqual(fm.num_faces(1), 3)
        with self.assertRaises(TecplotNotImplementedError):
            self.assertEqual(fm.num_nodes(), 10)
        self.assertEqual(fm.num_nodes(0), 2)
        self.assertEqual(fm.num_nodes(1), 2)
        self.assertEqual(fm.num_unique_nodes, 4)
        self.assertEqual(fm.num_nodes(0), 2)
        self.assertEqual(fm.num_nodes(1), 2)
        self.assertEqual(fm.num_nodes(0, 0), 2)
        self.assertEqual(fm.num_nodes(element=1), 6)
        self.assertEqual(fm.num_nodes(4), fm.num_nodes(1,1))
        self.assertEqual(fm.num_boundary_connections(0), 0)
        self.assertEqual(fm.num_boundary_connections(0,0), 0)
        with self.assertRaises(TecplotLogicError):
            fm.boundary_connection(0,0)
        self.assertEqual(fm.node(0,0), 0)
        self.assertEqual(fm.node(0,1), 1)
        self.assertEqual(fm.node(2,0), 2)
        self.assertEqual(fm.left_element(0), 0)
        self.assertEqual(fm.left_element(1), 0)
        self.assertEqual(fm.right_element(0), -1)
        self.assertEqual(fm.right_element(1), 1)

        faces = [list(x) for x in faces]
        faces[0][0] = 4
        with self.assertRaises(TecplotSystemError):
            with fm.assignment():
                with self.assertRaises(TecplotIndexError):
                    fm.set_nodes(faces)

        elements = [list(x) for x in elements]
        elements[0][0] = 2
        with self.assertRaises(TecplotSystemError):
            with fm.assignment():
                with self.assertRaises(TecplotIndexError):
                    fm.set_elements(elements)
        elements[0][0] = 0
        elements[0][1] = 2
        with self.assertRaises(TecplotSystemError):
            with fm.assignment():
                with self.assertRaises(TecplotIndexError):
                    fm.set_elements(elements)

    def test_eq(self):
        fm = self.z.facemap
        fm.alloc(10)
        new_zone = self.z.dataset.add_poly_zone(ZoneType.FEPolygon,'Z',3,1,3)
        self.assertTrue(fm != new_zone.facemap)
        new_zone.facemap.alloc(6)
        self.assertTrue(bool(new_zone.facemap))
        self.assertFalse(fm == new_zone.facemap)
        self.assertTrue(fm != new_zone.facemap)

    def test_empty_facemap(self):
        self.z.facemap.alloc(10)
        self.assertTrue(bool(self.z.facemap))

    @skip_on(TecplotOutOfDateEngineError)
    def test_set_elementmap(self):
        nodes = ((0, 0, 0  ), (1, 0, 0.5), (0, 1, 0.5), (1, 1, 1  ))
        elementmap = ((0, 1, 2), (1, 3, 2))
        ds = self.z.dataset
        z = ds.add_poly_zone(ZoneType.FEPolygon, name='Zone',
                             num_points=len(nodes),
                             num_elements=len(elementmap))
        z.values('x')[:] = [n[0] for n in nodes]
        z.values('y')[:] = [n[1] for n in nodes]
        z.values('z')[:] = [n[2] for n in nodes]

        if __debug__:
            sdkver = tp.data.facemap.sdk_version_info
            try:
                tp.data.facemap.sdk_version_info = (0, 0, 0)
                with self.assertRaises(TecplotOutOfDateEngineError):
                    fm = z.facemap
            finally:
                tp.data.facemap.sdk_version_info = sdkver

        fm = z.facemap
        self.assertFalse(bool(fm))
        fm.set_elementmap(elementmap)

        self.assertTrue(fm._has_data_backing)
        self.assertTrue(fm == z.facemap)
        self.assertEqual(fm, z.facemap)
        self.assertEqual(len(fm), fm.num_faces())
        self.assertEqual(fm.num_faces(), 5)
        self.assertEqual(fm.num_faces(0), 3)
        self.assertEqual(fm.num_faces(1), 3)
        with self.assertRaises(TecplotNotImplementedError):
            self.assertEqual(fm.num_nodes(), 10)
        self.assertEqual(fm.num_nodes(0), 2)
        self.assertEqual(fm.num_unique_nodes, 4)
        self.assertEqual(fm.num_nodes(0), 2)
        self.assertEqual(fm.num_nodes(1), 2)
        self.assertEqual(fm.num_boundary_connections(0), 0)
        with self.assertRaises(TecplotNotImplementedError):
            fm.num_boundary_connections()
        self.assertEqual(fm.num_boundary_connections(element=0), 0)
        with self.assertRaises(TecplotLogicError):
            fm.boundary_connection(0,0)

        self.assertEqual(fm.node(0,0), 0)
        self.assertEqual(fm.node(0,1), 1)
        self.assertEqual(fm.node(2,0), 1)

        self.assertEqual(fm.left_element(0), 0)
        self.assertEqual(fm.left_element(1), -1)
        self.assertEqual(fm.left_element(2), 0)

        self.assertEqual(fm.right_element(0), -1)
        self.assertEqual(fm.right_element(1), 0)
        self.assertEqual(fm.right_element(2), 1)

        self.assertEqual(fm.left_element(0,0), 0)
        self.assertEqual(fm.left_element(1,0), 0)
        self.assertEqual(fm.left_element(2,0), -1)

        self.assertEqual(fm.right_element(0,0), -1)
        self.assertEqual(fm.right_element(1,0), 1)
        self.assertEqual(fm.right_element(2,0), 0)

        elementmap = [list(x) for x in elementmap]
        elementmap[0][0] = 4
        with self.assertRaises((TecplotIndexError, TecplotLogicError,
                                TecplotSystemError)):
            fm.set_elementmap(elementmap)

    @skip_on(TecplotOutOfDateEngineError)
    def test_set_elementmap2(self):
        nodes = ((0, 0, 0  ), (1, 0, 0.5), (0, 1, 0.5), (1, 1, 1  ))
        elementmap = ((0, 1, 2), (1, 3, 2))
        ds = self.z.dataset
        z = ds.add_poly_zone(ZoneType.FEPolygon, name='Z',
                             num_points=len(nodes),
                             num_elements=len(elementmap),
                             num_faces=5)
        z.values('x')[:] = [n[0] for n in nodes]
        z.values('y')[:] = [n[1] for n in nodes]
        z.values('z')[:] = [n[2] for n in nodes]

        fm = z.facemap
        self.assertTrue(bool(fm))
        fm.set_elementmap(elementmap)

        self.assertTrue(fm._has_data_backing)
        self.assertTrue(fm == z.facemap)
        self.assertEqual(fm, z.facemap)
        self.assertEqual(len(fm), fm.num_faces())
        self.assertEqual(fm.num_faces(), 5)
        self.assertEqual(fm.num_faces(0), 3)
        self.assertEqual(fm.num_faces(1), 3)
        with self.assertRaises(TecplotNotImplementedError):
            self.assertEqual(fm.num_nodes(), 10)
        self.assertEqual(fm.num_nodes(0), 2)
        self.assertEqual(fm.num_unique_nodes, 4)
        self.assertEqual(fm.num_nodes(0), 2)
        self.assertEqual(fm.num_nodes(1), 2)
        self.assertEqual(fm.num_boundary_connections(0), 0)
        with self.assertRaises(TecplotNotImplementedError):
            fm.num_boundary_connections()
        self.assertEqual(fm.num_boundary_connections(element=0), 0)
        with self.assertRaises(TecplotLogicError):
            fm.boundary_connection(0,0)

        self.assertEqual(fm.node(0,0), 0)
        self.assertEqual(fm.node(0,1), 1)
        self.assertEqual(fm.node(2,0), 1)

        self.assertEqual(fm.left_element(0), 0)
        self.assertEqual(fm.left_element(1), -1)
        self.assertEqual(fm.left_element(2), 0)

        self.assertEqual(fm.right_element(0), -1)
        self.assertEqual(fm.right_element(1), 0)
        self.assertEqual(fm.right_element(2), 1)

        self.assertEqual(fm.left_element(0,0), 0)
        self.assertEqual(fm.left_element(1,0), 0)
        self.assertEqual(fm.left_element(2,0), -1)

        self.assertEqual(fm.right_element(0,0), -1)
        self.assertEqual(fm.right_element(1,0), 1)
        self.assertEqual(fm.right_element(2,0), 0)

        elementmap = [list(x) for x in elementmap]
        elementmap[0][0] = 4
        with self.assertRaises((TecplotIndexError, TecplotLogicError,
                                TecplotSystemError)):
            fm.set_elementmap(elementmap)

    def test_alloc_failures(self):
        if __debug__:
            sdkver = tp.data.facemap.sdk_version_info
            try:
                tp.data.facemap.sdk_version_info = (0, 0, 0)
                with self.assertRaises(TecplotOutOfDateEngineError):
                    self.z.facemap.alloc(10, 1, 1)
            finally:
                tp.data.facemap.sdk_version_info = sdkver

        with patch_tecutil('DataFaceMapAlloc', return_value=False):
            with self.assertRaises((TecplotSystemError, TecplotLogicError)):
                self.z.facemap.alloc(10)

    def test_assignment_failures(self):
        with patch_tecutil('DataFaceMapEndAssign', return_value=False):
            with self.assertRaises(TecplotSystemError):
                self.z.facemap.alloc(10)
                with self.z.facemap.assignment():
                    pass
        if __debug__:
            faces = ((0, 1), (1, 2), (2, 0), (1, 3), (3, 2))
            nfaces = sum(len(n) for n in faces)

            with self.assertRaises(TecplotSystemError):
                self.z.facemap.alloc(nfaces)
                with self.z.facemap.assignment():
                    self.z.facemap.set_nodes(faces)
                    with self.assertRaises(TecplotIndexError):
                        self.z.facemap.set_elements((0, 0, 0, 1, 10),
                                                    (-1, 1, -1, -1, -1))

            with self.assertRaises(TecplotSystemError):
                self.z.facemap.alloc(nfaces)
                with self.z.facemap.assignment():
                    self.z.facemap.set_nodes(faces)
                    with self.assertRaises(TecplotIndexError):
                        self.z.facemap.set_elements((0, 0, 0, 1, 1),
                                                    (-1, 1, 10, -1, -1))


class TestFacemapPolyhedrons(unittest.TestCase):
    @skip_on(TecplotOutOfDateEngineError)
    def setUp(self):
        tp.new_layout()
        # Tetrahedron in the first zone
        nodes0 = ((0, 0, 0), (1, 1, 0), (1, 0, 1), (0, 1, 1))
        faces0 = ((0, 1, 2), (0, 1, 3), (1, 3, 2), (0, 2, 3))
        elems0 = ((0, 0, 0, 0), (-1, -1, -1, -2))
        scalar_data0 = (0,)
        num_elements0 = max(it.chain(*elems0)) + 1
        boundary_elems0 = ((0,),)
        boundary_zones0 = ((1,),)

        nodes1 = ((0, 0, 0), (1, 0, 1), (0, 1, 1), (0, 0, 1))
        faces1 = ((0, 1, 2), (0, 1, 3), (1, 3, 2), (0, 2, 3))
        elems1 = ((0, 0, 0, 0), (-2, -1, -1, -1))
        scalar_data1 = (1,)
        num_elements1 = max(it.chain(*elems1)) + 1
        boundary_elems1 = ((0,),)
        boundary_zones1 = ((0,),)

        ds = tp.active_frame().create_dataset('Data', ['x','y','z'])

        z0 = ds.add_poly_zone(ZoneType.FEPolyhedron,
                              name='0',
                              num_points=len(nodes0),
                              num_elements=num_elements0,
                              num_faces=len(faces0))
        z1 = ds.add_poly_zone(ZoneType.FEPolyhedron,
                              name='1',
                              num_points=len(nodes1),
                              num_elements=num_elements1,
                              num_faces=len(faces1))

        z0.values('x')[:] = [n[0] for n in nodes0]
        z0.values('y')[:] = [n[1] for n in nodes0]
        z0.values('z')[:] = [n[2] for n in nodes0]
        z1.values('x')[:] = [n[0] for n in nodes1]
        z1.values('y')[:] = [n[1] for n in nodes1]
        z1.values('z')[:] = [n[2] for n in nodes1]

        z0.facemap.set_mapping(faces0, elems0, boundary_elems0, boundary_zones0)
        z1.facemap.set_mapping(faces1, elems1, boundary_elems1, boundary_zones1)

        self.fm0 = z0.facemap
        self.fm1 = z1.facemap

    def test_num_faces(self):
        self.assertEqual(self.fm0.num_faces(), 4)
        self.assertEqual(self.fm1.num_faces(), 4)

    def test_num_unique_nodes(self):
        self.assertEqual(self.fm0.num_unique_nodes, 4)
        self.assertEqual(self.fm1.num_unique_nodes, 4)

    def test_num_nodes(self):
        with self.assertRaises(TecplotNotImplementedError):
            self.assertEqual(self.fm0.num_nodes(), 12)
        self.assertEqual(self.fm0.num_nodes(0), 3)
        with self.assertRaises(TecplotNotImplementedError):
            self.assertEqual(self.fm1.num_nodes(), 12)
        self.assertEqual(self.fm1.num_nodes(0), 3)

    def test_node(self):
        self.assertEqual(self.fm0.node(0,0), 0)
        self.assertEqual(self.fm0.node(1,0), 0)
        self.assertEqual(self.fm0.node(3,2), 3)
        self.assertEqual(self.fm0.node(0,0,0), 0)
        self.assertEqual(self.fm0.node(1,0,0), 0)
        self.assertEqual(self.fm0.node(3,2,0), 3)

    def test_face(self):
        self.assertEqual(self.fm0.face(0,0), 0)
        self.assertEqual(self.fm0.face(0,1), 1)

    def test_num_boundary_connections(self):
        self.assertEqual(self.fm0.num_boundary_connections(0), 0)
        self.assertEqual(self.fm0.num_boundary_connections(1), 0)
        self.assertEqual(self.fm0.num_boundary_connections(2), 0)
        self.assertEqual(self.fm0.num_boundary_connections(3), 1)
        self.assertEqual(self.fm1.num_boundary_connections(0), 1)
        self.assertEqual(self.fm1.num_boundary_connections(1), 0)
        self.assertEqual(self.fm1.num_boundary_connections(2), 0)
        self.assertEqual(self.fm1.num_boundary_connections(3), 0)
        self.assertEqual(self.fm0.num_boundary_connections(3,0), 1)
        self.assertEqual(self.fm0.num_boundary_connections(element=0), 1)

    def test_boundary_connection(self):
        bconn0 = self.fm0.boundary_connection
        bconn1 = self.fm1.boundary_connection
        self.assertEqual(bconn0(3,0).element, 0)
        self.assertEqual(bconn0(3,0,0).element, 0)
        self.assertEqual(bconn1(0,0).element, 0)
        self.assertEqual(bconn0(3,0).zone.index, 1)
        self.assertEqual(bconn0(3,0,0).zone.index, 1)
        self.assertEqual(bconn1(0,0).zone.index, 0)

        with self.assertRaises((TecplotLogicError, TecplotSystemError)):
            bconn0(0,0)


class TestFacemapPolyhedronsElementmap(unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        nodes = ((0, 0, 0), (1, 1, 0), (1, 0, 1), (0, 1, 1), (0, 0, 1))
        elementmap = (((0, 1, 2), (0, 1, 3), (1, 3, 2), (0, 2, 3)),
                      ((0, 2, 3), (2, 3, 4), (0, 2, 4), (0, 4, 3)))
        ds = tp.active_frame().create_dataset('Data', ['x','y','z'])
        z = ds.add_poly_zone(ZoneType.FEPolyhedron,
                             name='Z',
                             num_points=len(nodes),
                             num_elements=len(elementmap),
                             num_faces=7)
        z.values('x')[:] = [n[0] for n in nodes]
        z.values('y')[:] = [n[1] for n in nodes]
        z.values('z')[:] = [n[2] for n in nodes]
        z.facemap.set_elementmap(elementmap)
        self.fm = z.facemap

    def test_num_faces(self):
        self.assertEqual(self.fm.num_faces(), 7)
        self.assertEqual(self.fm.num_faces(0), 4)

    def test_num_unique_nodes(self):
        self.assertEqual(self.fm.num_unique_nodes, 5)

    def test_num_nodes(self):
        with self.assertRaises(TecplotNotImplementedError):
            self.assertEqual(self.fm.num_nodes(), 21)
        self.assertEqual(self.fm.num_nodes(0), 3)

    def test_failure(self):
        with patch_tecutil('DataFaceMapAssignElemToNodeMap', return_value=False):
            with self.assertRaises(TecplotSystemError):
                self.fm.set_elementmap([[[]]])


class TestBoundaryConnections(unittest.TestCase):
    @skip_on(TecplotOutOfDateEngineError)
    def setUp(self):
        tp.new_layout()
        nodes0 = ((0, 0, 0), (1, 0, 0.5), (0, 1, 0.5))
        scalar_data0 = (0, 1, 2)
        faces0 = ((0, 1), (1, 2), (2, 0))
        elements0 = ((0, 0, 0), (-1, -2, -1))
        num_elements0 = 1

        nodes1 = ((1, 0, 0.5), (1, 1, 1), (0, 1, 0.5))
        scalar_data1 = (1, 3, 2)
        faces1 = ((0, 1), (1, 2), (2, 0))
        elements1 = ((0, 0, 0), (-1, -1, -2))
        num_elements1 = 1

        boundary_elems0 = ((0,),)
        boundary_zones0 = ((1,),)

        boundary_elems1 = ((0,),)
        boundary_zones1 = ((0,),)

        ds = tp.active_frame().create_dataset('Data', ['x','y','z'])
        z0 = ds.add_poly_zone(ZoneType.FEPolygon,
                              name='0: FE Polygon Float (3,1,3) Nodal',
                              num_points=len(nodes0),
                              num_elements=num_elements0,
                              num_faces=len(faces0))
        z1 = ds.add_poly_zone(ZoneType.FEPolygon,
                              name='1: FE Polygon Float (3,1,3) Nodal',
                              num_points=len(nodes1),
                              num_elements=num_elements1,
                              num_faces=len(faces1))

        z0.values('x')[:] = [n[0] for n in nodes0]
        z0.values('y')[:] = [n[1] for n in nodes0]
        z0.values('z')[:] = [n[2] for n in nodes0]
        z1.values('x')[:] = [n[0] for n in nodes1]
        z1.values('y')[:] = [n[1] for n in nodes1]
        z1.values('z')[:] = [n[2] for n in nodes1]

        z0.facemap.set_mapping(faces0, elements0, boundary_elems0, boundary_zones0)
        z1.facemap.set_mapping(faces1, elements1, boundary_elems1, boundary_zones1)

        self.z0 = z0
        self.z1 = z1

    def test_num_boundary_connections(self):
        fm0 = self.z0.facemap
        fm1 = self.z1.facemap
        self.assertEqual(fm0.num_boundary_connections(0), 0)
        self.assertEqual(fm0.num_boundary_connections(1), 1)
        self.assertEqual(fm0.num_boundary_connections(2), 0)
        self.assertEqual(fm1.num_boundary_connections(0), 0)
        self.assertEqual(fm1.num_boundary_connections(1), 0)
        self.assertEqual(fm1.num_boundary_connections(2), 1)

    def test_boundary_connection(self):
        fm0 = self.z0.facemap
        fm1 = self.z1.facemap
        self.assertEqual(fm0.boundary_connection(1,0).element, 0)
        self.assertEqual(fm0.boundary_connection(1,0).zone.index, 1)
        self.assertEqual(fm1.boundary_connection(2,0).element, 0)
        self.assertEqual(fm1.boundary_connection(2,0).zone.index, 0)

    def test_set_failure(self):
        fm = self.z0.facemap

        with self.assertRaises(TecplotSystemError):
            with fm.assignment():
                with self.assertRaises(TecplotIndexError):
                    fm.set_boundary_connections(((1,),), ((0,),))

        with self.assertRaises(TecplotSystemError):
            with fm.assignment():
                with self.assertRaises(TecplotIndexError):
                    fm.set_boundary_connections(((0,),), ((2,),))



if __name__ == '__main__':
    from .. import main
    main()
