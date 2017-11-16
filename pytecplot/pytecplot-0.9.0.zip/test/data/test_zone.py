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

from test import patch_tecutil, skip_on
from ..sample_data import sample_data_file


class _TestZone(object):
    def test_str(self):
        self.assertRegex(str(self.zone), r'Zone:.*')

    def test_repr(self):
        self.assertRegex(repr(self.zone), r'Zone\(.*')

    def test_eq(self):
        ds = tp.active_page().add_frame().create_dataset('D', ['x','y'])
        z1 = ds.add_ordered_zone('Z1', (3,))
        z2 = ds.add_ordered_zone('Z2', (3,))
        self.assertTrue(ds.zone(0) == z1)
        self.assertFalse(ds.zone(0) != z1)
        self.assertFalse(ds.zone(0) == z2)
        self.assertTrue(ds.zone(0) != z2)

    def test_aux_data(self):
        self.assertIsInstance(self.zone.aux_data, session.AuxData)
        self.assertEqual(self.zone.aux_data.object_type, AuxDataObjectType.Zone)

    def test_index(self):
        ds = tp.active_page().add_frame().create_dataset('D', ['x','y'])
        z1 = ds.add_ordered_zone('Z1', (3,))
        z2 = ds.add_ordered_zone('Z2', (3,))
        self.assertEqual(z1.index, 0)
        self.assertEqual(z2.index, 1)

    def test_strand(self):
        for val in [0,1,100]:
            self.zone.strand = val
            self.assertEqual(self.zone.strand, val)
        with self.assertRaises((TecplotLogicError, TecplotSystemError)):
            self.zone.strand = -1
        if __debug__:
            with self.assertRaises(TecplotTypeError):
                self.zone.strand = 3.14
        else:
            self.zone.strand = 3.14
            self.assertEqual(self.zone.strand, 3)

    def test_solution_time(self):
        for val in [-1,0,0.5,1,100]:
            self.zone.solution_time = val
            self.assertEqual(self.zone.solution_time, val)

    def test_zone_type(self):
        self.assertIsInstance(self.zone.zone_type, tp.constant.ZoneType)

    def test_name(self):
        ds = tp.active_page().add_frame().create_dataset('D', ['x','y'])
        z = ds.add_ordered_zone('Rectangular zone', (3,))
        zone = ds.zone('Rectangular zone')
        self.assertEqual(zone.name, 'Rectangular zone')
        zone.name = 'Ζονε'
        self.assertEqual(zone.name, 'Ζονε')
        zone = ds.zone('Ζονε')
        self.assertEqual(zone.name, 'Ζονε')
        zone.name = ''
        self.assertEqual(zone.name, '')

        # trick this zone to point to a non-existent dataset
        zone.dataset.uid += 1

        with self.assertRaises((TecplotLogicError, TecplotSystemError)):
            zone.name

        with self.assertRaises((TecplotLogicError, TecplotSystemError)):
            zone.name = 'Test'

        with self.assertRaises((TecplotLogicError, TecplotSystemError)):
            zone.name = None

        with patch_tecutil('ZoneGetNameByDataSetID', return_value=(False,'')):
            with self.assertRaises(TecplotSystemError):
                n = zone.name

    def test_num_variables(self):
        ds = tp.active_page().add_frame().create_dataset('D', ['x','y'])
        z = ds.add_ordered_zone('Z1', (3,))
        self.assertEqual(self.zone.num_variables, 2)

    def test_values(self):
        ds = tp.active_page().add_frame().create_dataset('D', ['x','y'])
        z = ds.add_ordered_zone('Z1', (3,))
        a = z.values('x')
        self.assertIsInstance(a, tp.data.Array)
        self.assertEqual(a.zone, z)
        self.assertEqual(a.variable, ds.variable('x'))

        x = ds.variable('x')
        self.assertEqual(z.values(x), a)
        self.assertEqual(z.values(x), x.values(z))

    @skip_on(TecplotOutOfDateEngineError)
    def test_copy(self):
        ds = tp.active_page().add_frame().create_dataset('D', ['x','y'])
        z = ds.add_ordered_zone('Z1', (3,))
        zcopy = z.copy()
        self.assertEqual(ds.num_zones, 2)
        self.assertNotEqual(z, zcopy)
        self.assertEqual(z.dataset, zcopy.dataset)
        self.assertEqual(z.zone_type, zcopy.zone_type)
        self.assertEqual(z.strand, zcopy.strand)
        self.assertEqual(z.solution_time, zcopy.solution_time)
        self.assertEqual(z.name, zcopy.name)
        self.assertEqual(z.values(0).shared_zones, [])
        self.assertEqual(z.values(1).shared_zones, [])
        zcopy2 = z.copy(share_variables=True)
        self.assertEqual(zcopy2.values(0).shared_zones, [z,zcopy2])
        self.assertEqual(zcopy2.values(1).shared_zones, [z,zcopy2])

    def test_num_points(self):
        ds = tp.active_page().add_frame().create_dataset('D', ['x','y'])
        z = ds.add_ordered_zone('Z1', (3,))
        self.assertEqual(z.num_points, 3)
        z = ds.add_fe_zone(tp.constant.ZoneType.FELineSeg, 'Z1', 3, 2)
        self.assertEqual(z.num_points, 3)


class TestOrderedZone(_TestZone, unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        ds = tp.active_frame().create_dataset('D', ['x','y'])
        self.zone = ds.add_ordered_zone('Z', (3,))

    def test_dimensions(self):
        ds = tp.active_page().add_frame().create_dataset('D', ['x','y'])
        z = ds.add_ordered_zone('Z1', (3,2,5))
        self.assertEqual(z.dimensions, (3,2,5))

    def test_rank(self):
        ds = tp.active_page().add_frame().create_dataset('D', ['x','y'])
        z = ds.add_ordered_zone('Z1', (3,2,1))
        self.assertEqual(z.rank, 2)

    def test_num_elements(self):
        ds = tp.active_page().add_frame().create_dataset('D', ['x','y'])
        z = ds.add_ordered_zone('Z', (1,1,1))
        self.assertEqual(z.num_elements, 0)
        z = ds.add_ordered_zone('Z', (3,1,1))
        self.assertEqual(z.num_elements, 2)
        z = ds.add_ordered_zone('Z1', (3,7,1))
        self.assertEqual(z.num_elements, 2*6)
        z = ds.add_ordered_zone('Z1', (3,7,13))
        self.assertEqual(z.num_elements, 2*6*12)

        z = ds.add_ordered_zone('Z', (1,1,3))
        self.assertEqual(z.num_elements, 2)
        z = ds.add_ordered_zone('Z1', (1,7,3))
        self.assertEqual(z.num_elements, 2*6)

    def test_num_points_per_element(self):
        ds = tp.active_page().add_frame().create_dataset('D', ['x','y'])
        z = ds.add_ordered_zone('Z', (1,1,1))
        self.assertEqual(z.num_points_per_element, 0)
        z = ds.add_ordered_zone('Z', (3,1,1))
        self.assertEqual(z.num_points_per_element, 2)
        z = ds.add_ordered_zone('Z1', (3,7,1))
        self.assertEqual(z.num_points_per_element, 2**2)
        z = ds.add_ordered_zone('Z1', (3,7,13))
        self.assertEqual(z.num_points_per_element, 2**3)

    def test_face_neighbors(self):
        self.assertIsInstance(self.zone.face_neighbors, tp.data.FaceNeighbors)

    def test_num_faces_per_element(self):
        ds = self.zone.dataset
        z = ds.add_ordered_zone('Z', (1,))
        self.assertEqual(z.num_faces_per_element, 0)
        self.assertEqual(z.num_faces, 0)
        z = ds.add_ordered_zone('Z', (2,))
        self.assertEqual(z.num_faces_per_element, 1)
        self.assertEqual(z.num_faces, 1)
        z = ds.add_ordered_zone('Z', (2,2))
        self.assertEqual(z.num_faces_per_element, 4)
        self.assertEqual(z.num_faces, 4)
        z = ds.add_ordered_zone('Z', (2,2,2))
        self.assertEqual(z.num_faces_per_element, 6)
        self.assertEqual(z.num_faces, 6)



class TestClassicFEZone(_TestZone, unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        ds = tp.active_frame().create_dataset('D', ['x','y'])
        self.zone = ds.add_fe_zone(tp.constant.ZoneType.FELineSeg, 'Z1', 3, 2)

    def test_shape(self):
        self.assertEqual(self.zone._shape, (3,2,2))

    def test_num_points_per_element(self):
        ds = tp.active_page().add_frame().create_dataset('D', ['x','y'])
        z = ds.add_fe_zone(tp.constant.ZoneType.FELineSeg, 'Z1', 3, 2)
        self.assertEqual(z.num_points_per_element, 2)
        z = ds.add_fe_zone(tp.constant.ZoneType.FETriangle, 'Z1', 3, 2)
        self.assertEqual(z.num_points_per_element, 3)
        z = ds.add_fe_zone(tp.constant.ZoneType.FEQuad, 'Z1', 3, 2)
        self.assertEqual(z.num_points_per_element, 4)
        z = ds.add_fe_zone(tp.constant.ZoneType.FETetra, 'Z1', 3, 2)
        self.assertEqual(z.num_points_per_element, 4)
        z = ds.add_fe_zone(tp.constant.ZoneType.FEBrick, 'Z1', 3, 2)
        self.assertEqual(z.num_points_per_element, 8)

    def test_rank(self):
        ds = tp.active_page().add_frame().create_dataset('D', ['x','y'])
        z = ds.add_fe_zone(tp.constant.ZoneType.FELineSeg, 'Z1', 3, 2)
        self.assertEqual(z.rank, 1)
        z = ds.add_fe_zone(tp.constant.ZoneType.FETriangle, 'Z1', 3, 2)
        self.assertEqual(z.rank, 2)
        z = ds.add_fe_zone(tp.constant.ZoneType.FEQuad, 'Z1', 3, 2)
        self.assertEqual(z.rank, 2)
        z = ds.add_fe_zone(tp.constant.ZoneType.FETetra, 'Z1', 3, 2)
        self.assertEqual(z.rank, 3)
        z = ds.add_fe_zone(tp.constant.ZoneType.FEBrick, 'Z1', 3, 2)
        self.assertEqual(z.rank, 3)

    def test_num_faces_per_element(self):
        ds = tp.active_page().add_frame().create_dataset('D', ['x','y'])
        z = ds.add_fe_zone(tp.constant.ZoneType.FELineSeg, 'Z1', 3, 2)
        self.assertEqual(z.num_faces_per_element, 1)
        z = ds.add_fe_zone(tp.constant.ZoneType.FETriangle, 'Z1', 3, 2)
        self.assertEqual(z.num_faces_per_element, 3)
        z = ds.add_fe_zone(tp.constant.ZoneType.FEQuad, 'Z1', 3, 2)
        self.assertEqual(z.num_faces_per_element, 4)
        z = ds.add_fe_zone(tp.constant.ZoneType.FETetra, 'Z1', 3, 2)
        self.assertEqual(z.num_faces_per_element, 4)
        z = ds.add_fe_zone(tp.constant.ZoneType.FEBrick, 'Z1', 3, 2)
        self.assertEqual(z.num_faces_per_element, 6)

    def test_nodemap(self):
        self.assertIsInstance(self.zone.nodemap, tp.data.Nodemap)

    def test_num_points(self):
        self.assertEqual(self.zone.num_points, 3)

    def test_num_elements(self):
        self.assertEqual(self.zone.num_elements, 2)

    def test_face_neighbors(self):
        self.assertIsInstance(self.zone.face_neighbors, tp.data.FaceNeighbors)

    @skip_on(TecplotOutOfDateEngineError)
    def test_connectivity_sharing(self):
        z2 = self.zone.copy()
        self.assertEqual(z2.shared_connectivity, [self.zone,z2])
        self.assertEqual(self.zone.nodemap, z2.nodemap)


class TestPolyFEZone(_TestZone, unittest.TestCase):
    def setUp(self):
        tp.new_layout()
        ds = tp.active_frame().create_dataset('D', ['x','y'])
        self.zone = ds.add_poly_zone(tp.constant.ZoneType.FEPolygon, 'Z1', 3, 2, 1)

    def test_shape(self):
        self.assertEqual(self.zone._shape, (3,2,1))

    def test_rank(self):
        ds = tp.active_page().add_frame().create_dataset('D', ['x','y'])
        z = ds.add_poly_zone(tp.constant.ZoneType.FEPolygon, 'Z1', 3, 2, 1)
        self.assertEqual(z.rank, 2)
        z = ds.add_poly_zone(tp.constant.ZoneType.FEPolyhedron, 'Z1', 3, 2, 1)
        self.assertEqual(z.rank, 3)

    def test_num_faces(self):
        self.assertEqual(self.zone.num_faces, 1)

    def test_facemap(self):
        self.assertIsInstance(self.zone.facemap, tp.data.Facemap)

    def test_num_points(self):
        self.assertEqual(self.zone.num_points, 3)

    def test_num_elements(self):
        self.assertEqual(self.zone.num_elements, 2)

    @skip_on(TecplotOutOfDateEngineError)
    def test_connectivity_sharing(self):
        z2 = self.zone.copy()
        self.assertEqual(z2.shared_connectivity, [self.zone,z2])
        self.assertEqual(self.zone.facemap, z2.facemap)


if __name__ == '__main__':
    from .. import main
    main()
