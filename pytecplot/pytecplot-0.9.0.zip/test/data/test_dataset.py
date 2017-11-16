# coding: utf-8
from __future__ import unicode_literals

import os
import platform
import sys
import unittest

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

from test import patch_tecutil, skip_on
from ..sample_data import sample_data_file, loaded_sample_data

class TestDataset(unittest.TestCase):

    def setUp(self):
        self.filenames = {
            '10x10x10' : sample_data_file('10x10x10'),
            '2x2x3_overlap' : sample_data_file('2x2x3_overlap')}

    def tearDown(self):
        for fname in self.filenames.values():
            os.remove(fname)

    def test___init__(self):
        page = tp.layout.Page(1)
        frame = tp.layout.Frame(2,page)
        dataset = tp.data.Dataset(3,frame)
        self.assertEqual(dataset.uid,3)
        self.assertEqual(dataset.frame.uid,2)
        self.assertEqual(dataset.frame.page.uid,1)

    def test___repr__(self):
        page = tp.layout.Page(1)
        frame = tp.layout.Frame(2,page)
        dataset = tp.data.Dataset(3,frame)
        self.assertEqual(repr(dataset), 'Dataset(uid=3, frame=Frame(uid=2, page=Page(uid=1)))')

    @skip_on(TecplotOutOfDateEngineError)
    def test_str(self):
        fmt = 'Dataset: {}\n  Zones: {}\n  Variables: {}'
        tp.new_layout()
        ds = tp.data.load_tecplot(self.filenames['10x10x10'])
        self.assertEqual(str(ds), fmt.format("'Internally created data set'",
            "'Rectangular zone'", "'X', 'Y', 'Z'"))
        ds = tp.data.load_tecplot(self.filenames['2x2x3_overlap'])
        self.assertEqual(str(ds), fmt.format("'Internally created data set'",
            "'Rectangular zone', 'Rectangular zone 1', 'Rectangular zone 2'",
            "'X', 'Y', 'Z', 'P'"))

    def test___contains__(self):
        tp.new_layout()
        ds0 = tp.data.load_tecplot(self.filenames['10x10x10'])
        tp.active_page().add_frame()
        ds1 = tp.data.load_tecplot(self.filenames['2x2x3_overlap'])
        self.assertIn(ds0.variable(0), ds0)
        self.assertNotIn(ds1.variable(0), ds0)
        self.assertIn(ds0.zone(0), ds0)
        self.assertNotIn(ds1.zone(0), ds0)
        class UnknownObj(object):
            def __init__(self, ds):
                self.dataset = ds
        unkobj = UnknownObj(ds0)
        self.assertNotIn(unkobj, ds0)

    def test___eq__(self):
        page = tp.layout.Page(1)
        frame = tp.layout.Frame(2,page)
        dataset3 = tp.data.Dataset(3,frame)
        dataset4 = tp.data.Dataset(4,frame)
        dataset3_copy = tp.data.Dataset(3,frame)
        self.assertEqual(dataset3, dataset3_copy)
        self.assertNotEqual(dataset3, dataset4)

    def test_aux_data(self):
        tp.new_layout()
        ds = tp.data.load_tecplot(self.filenames['10x10x10'])
        self.assertIsInstance(ds.aux_data, session.AuxData)
        self.assertEqual(ds.aux_data.object_type, AuxDataObjectType.Dataset)

    @skip_on(TecplotOutOfDateEngineError)
    def test_title(self):
        tp.new_layout()
        tp.data.load_tecplot(self.filenames['10x10x10'])
        ds = tp.active_frame().dataset

        with patch_tecutil('DataSetSetTitleByUniqueID', return_value=False):
            with self.assertRaises(TecplotSystemError):
                ds.title = 'test'

        self.assertEqual(ds.title, 'Internally created data set')
        ds.title = 'test'
        self.assertEqual(ds.title, 'test')
        ds.title = 'Test Τεστ'
        self.assertEqual(ds.title, 'Test Τεστ')
        ds.title = ''
        self.assertEqual(ds.title, '')

        ds.frame.uid -= 1
        with self.assertRaises((TecplotLogicError, TecplotSystemError)):
            ds.title = None

    def test_num_zones(self):
        tp.new_layout()
        ds = tp.data.load_tecplot(self.filenames['10x10x10'])
        self.assertEqual(ds.num_zones, 1)
        ds = tp.data.load_tecplot(self.filenames['2x2x3_overlap'])
        self.assertEqual(ds.num_zones, 3)

    def test_zone(self):
        tp.new_layout()
        ds = tp.data.load_tecplot(self.filenames['2x2x3_overlap'])
        z0 = ds.zone(0)
        z1 = ds.zone(1)
        self.assertIsInstance(z0, tp.data.OrderedZone)
        self.assertIsInstance(z1, tp.data.OrderedZone)
        self.assertEqual(z0, ds.zone('Rectangular zone 1'))
        self.assertEqual(z1, ds.zone('Rectangular zone 2'))
        self.assertEqual(z1, ds.zone(-1))
        self.assertEqual(z0, ds.zone(-2))
        with self.assertRaises(TecplotIndexError):
            ds.zone(2)
        with self.assertRaises(TecplotIndexError):
            ds.zone(-3)

    def test_zones(self):
        tp.new_layout()
        ds = tp.data.load_tecplot(self.filenames['2x2x3_overlap'])
        self.assertEqual(len(list(ds.zones())), 2)
        self.assertEqual(len(list(ds.zones('Rec*'))), 2)
        self.assertEqual(len(list(ds.zones('*1'))), 1)
        self.assertEqual(len(list(ds.zones('Z*'))), 0)
        tp.new_layout()
        ds = tp.data.load_tecplot(self.filenames['2x2x3_overlap'], zones=[1])
        self.assertEqual(ds.num_zones, 2)
        self.assertEqual(len(list(ds.zones())), 1)
        self.assertEqual(len(list(ds.zones('*2'))), 1)

    def test_num_variables(self):
        tp.new_layout()
        ds = tp.data.load_tecplot(self.filenames['10x10x10'])
        self.assertEqual(ds.num_variables, 3)
        ds = tp.data.load_tecplot(self.filenames['2x2x3_overlap'])
        self.assertEqual(ds.num_variables, 4)

    def test_variable(self):
        tp.new_layout()
        ds = tp.data.load_tecplot(self.filenames['2x2x3_overlap'])
        v0 = ds.variable(0)
        v1 = ds.variable(1)
        self.assertIsInstance(v0, tp.data.Variable)
        self.assertIsInstance(v1, tp.data.Variable)
        self.assertEqual(v0, ds.variable('X'))
        self.assertEqual(v1, ds.variable('Y'))
        self.assertEqual(ds.variable('P'), ds.variable(-1))
        self.assertEqual(ds.variable('Z'), ds.variable(-2))
        with self.assertRaises(TecplotIndexError):
            ds.variable(4)
        with self.assertRaises(TecplotIndexError):
            ds.variable(-5)

    def test_variables(self):
        tp.new_layout()
        ds = tp.data.load_tecplot(self.filenames['2x2x3_overlap'])
        self.assertEqual(len(list(ds.variables())), 4)
        self.assertEqual(len(list(ds.variables('X'))), 1)
        tp.new_layout()
        ds = tp.data.load_tecplot(self.filenames['2x2x3_overlap'], variables=[1,2])
        self.assertEqual(ds.num_variables, 3)
        self.assertEqual(len(list(ds.variables())), 2)
        self.assertEqual(len(list(ds.variables('Y'))), 1)

    @skip_on(TecplotOutOfDateEngineError)
    def test_copy_zones(self):
        tp.new_layout()
        tp.data.load_tecplot(self.filenames['10x10x10'])
        ds = tp.active_frame().dataset
        z = ds.copy_zones(ds.zones())[0]
        self.assertEqual(ds.num_zones, 2)
        self.assertEqual(ds.zone(0)._shape, z._shape)
        self.assertNotEqual(ds.zone(0).uid, z.uid)
        self.assertEqual(ds.zone(1).uid, z.uid)

    def test_delete_zones_and_variables(self):
        tp.new_layout()
        ds = tp.data.load_tecplot(self.filenames['2x2x3_overlap'])
        self.assertIn('P', [v.name for v in ds.variables()])
        self.assertIn('Rectangular zone 2', [z.name for z in ds.zones()])
        ds.delete_variables(ds.variables('P'))
        ds.delete_zones(ds.zones('*2'))
        self.assertNotIn('P', [v.name for v in ds.variables()])
        self.assertNotIn('Rectangular zone 2', [z.name for z in ds.zones()])

        tp.new_layout()
        ds = tp.data.load_tecplot(self.filenames['2x2x3_overlap'])
        self.assertIn('P', [v.name for v in ds.variables()])
        self.assertIn('Rectangular zone 1', [z.name for z in ds.zones()])
        ds.delete_variables(ds.variable('P').index)
        ds.delete_zones(ds.zone('Rectangular zone 1').index)
        self.assertNotIn('P', [v.name for v in ds.variables()])
        self.assertNotIn('Rectangular zone 1', [z.name for z in ds.zones()])

    def test_delete_all_zones(self):
        ds = tp.data.load_tecplot(self.filenames['2x2x3_overlap'], read_data_option=ReadDataOption.ReplaceInActiveFrame)
        self.assertEqual(ds.num_zones, 2)

        with self.assertRaises((TecplotLogicError, TecplotSystemError)):
            ds.delete_zones(ds.zones())

    def test_delete_all_variables(self):
        tp.new_layout()
        ds = tp.data.load_tecplot(self.filenames['2x2x3_overlap'])
        self.assertEqual(ds.num_variables, 4)
        with self.assertRaises((TecplotLogicError, TecplotSystemError)):
            ds.delete_variables(ds.variables())

    def test_VariablesNamedTuple(self):
        tp.new_layout()
        ds = tp.active_frame().create_dataset('D', ['x', 'y'])
        self.assertEqual(ds.VariablesNamedTuple._fields, tuple('x y'.split()))

        tp.new_layout()
        ds = tp.active_frame().create_dataset('D', ['x', 'x'])
        self.assertEqual(ds.VariablesNamedTuple._fields, tuple('x0 x1'.split()))

        tp.new_layout()
        ds = tp.active_frame().create_dataset('D', ['x']*20)
        t = tuple(['x{:02d}'.format(i) for i in  range(20)])
        self.assertEqual(ds.VariablesNamedTuple._fields, t)

        tp.new_layout()
        ds = tp.active_frame().create_dataset('D', ['X', 'Y=f(X)'])
        t = tuple(['X', 'Y_f_X_'])
        self.assertEqual(ds.VariablesNamedTuple._fields, t)

        tp.new_layout()
        ds = tp.active_frame().create_dataset('D', ['_', '_'])
        t = tuple(['v0', 'v1'])
        self.assertEqual(ds.VariablesNamedTuple._fields, t)

        tp.new_layout()
        ds = tp.active_frame().create_dataset('D', ['def', 'if'])
        t = tuple(['def_', 'if_'])
        self.assertEqual(ds.VariablesNamedTuple._fields, t)

        tp.new_layout()
        ds = tp.active_frame().create_dataset('D', ['1', '2', '3'])
        t = tuple(['v1', 'v2', 'v3'])
        self.assertEqual(ds.VariablesNamedTuple._fields, t)

    def test_add_variable(self):
        tp.new_layout()
        ds = tp.active_frame().create_dataset('D')
        x = ds.add_variable('x')
        self.assertEqual(ds.num_variables, 1)
        self.assertEqual(ds.variable(0).name, 'x')
        self.assertEqual(ds.variable(0), x)
        ds.add_ordered_zone('Z1', 3)
        ds.add_ordered_zone('Z2', 3)
        y = ds.add_variable('y', dtypes=FieldDataType.Double)
        z = ds.add_variable('z', dtypes=[FieldDataType.Double,
                                         FieldDataType.Int32])
        self.assertEqual(ds.num_variables, 3)
        p = ds.add_variable('p', locations=ValueLocation.Nodal)
        q = ds.add_variable('q', locations=[ValueLocation.CellCentered,
                                        ValueLocation.Nodal])
        self.assertEqual(len(q.values('Z1')), 2)
        self.assertEqual(len(q.values('Z2')), 3)

        with patch_tecutil('DataSetAddVarX', return_value=False):
            with self.assertRaises(TecplotSystemError):
                ds.add_variable('r')

    def test_add_zone(self):
        if __debug__:
            tp.new_layout()
            ds = tp.active_frame().create_dataset('D')
            with self.assertRaises(TecplotLogicError):
                ds.add_zone(ZoneType.Ordered, 'Z', 3)

        tp.new_layout()
        ds = tp.active_frame().create_dataset('D', ['x','y','z','p'])
        z1 = ds.add_zone(ZoneType.Ordered, 'Z1', (3,3,3))
        z2 = ds.add_zone(ZoneType.Ordered, 'Z2', (3,3,3),
            dtypes=FieldDataType.Double, locations=ValueLocation.Nodal,
            solution_time=3.14, strand_id=10, index=0)
        self.assertEqual(ds.num_zones, 1)
        self.assertEqual(z1.index, -1)
        self.assertEqual(z2.index, 0)
        z3 = ds.add_zone(ZoneType.Ordered, 'Z3', (3,3,3),
            dtypes=[FieldDataType.Double]*3 + [FieldDataType.Int32],
            locations=[ValueLocation.CellCentered]*4,
            solution_time=6.28, strand_id=5, index=1,
            face_neighbor_mode=FaceNeighborMode.LocalOneToOne)
        self.assertEqual(ds.num_zones, 2)
        self.assertEqual(z3.index, 1)

        z3_1 = ds.add_zone(ZoneType.Ordered, 'Z3.1', (3,3,3), parent_zone=z3)
        self.assertEqual(z3_1.index, 2)

        with patch_tecutil('DataSetAddZoneX', return_value=False):
            with self.assertRaises(TecplotSystemError):
                ds.add_zone(ZoneType.Ordered, 'Z', 3)

        z4 = ds.add_fe_zone(ZoneType.FELineSeg, 'Z4', 3, 2)
        self.assertEqual(z4.num_points, 3)

        z5 = ds.add_poly_zone(ZoneType.FEPolygon, 'Z5', 3, 2, 1)
        self.assertEqual(z5.num_points, 3)

    def test_create_dataset(self):
        tp.new_layout()
        fr = tp.active_frame()
        self.assertFalse(fr.has_dataset)
        ds = fr.dataset
        self.assertTrue(fr.has_dataset)
        self.assertEqual(ds, fr.dataset)

    @skip_on(TecplotOutOfDateEngineError)
    def test_solution_times(self):
        tp.new_layout()
        ds = tp.data.load_tecplot(self.filenames['2x2x3_overlap'])

        self.assertEqual(ds.num_solution_times, 0)
        self.assertEqual(ds.solution_times, [])

        ds.zone(0).solution_time = 1

        self.assertEqual(ds.num_solution_times, 0)
        self.assertEqual(ds.solution_times, [])

        for z in ds.zones():
            z.strand = 1

        self.assertEqual(ds.num_solution_times, 2)
        self.assertEqual(ds.solution_times, [0,1])

        ds.zone(1).solution_time += 1
        self.assertEqual(ds.num_solution_times, 1)
        self.assertEqual(ds.solution_times, [1])

        ds.zone(1).solution_time = 2
        self.assertEqual(ds.num_solution_times, 2)
        self.assertEqual(ds.solution_times, [1,2])

    @skip_on(TecplotOutOfDateEngineError)
    def test_solution_time_failures(self):
        tp.new_layout()
        ds = tp.data.load_tecplot(self.filenames['2x2x3_overlap'])
        for t, z in enumerate(ds.zones()):
            z.strand = 1
            z.solution_time = t

        if tp.sdk_version_info >= (2017, 3):
            with patch_tecutil('SolutionTimeGetNumTimeStepsByDataSetID',
                               return_value=(False,0)):
                with self.assertRaises(TecplotSystemError):
                    n = ds.num_solution_times

        with patch_tecutil('SolutionTimeGetSolutionTimesByDataSetID',
                           return_value=(False,0,0)):
            with patch_tecutil('ArrayDealloc'):
                with self.assertRaises(TecplotSystemError):
                    n = ds.solution_times

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

        zcopy2 = ds.copy_zones(z.index, share_variables=True)
        zcopy3 = ds.copy_zones(z, share_variables=False)
        self.assertEqual(zcopy2[0].values(0).shared_zones, [z,zcopy2[0]])
        self.assertEqual(zcopy2[0].values(1).shared_zones, [z,zcopy2[0]])
        self.assertEqual(zcopy3[0].values(0).shared_zones, [])
        self.assertEqual(zcopy3[0].values(1).shared_zones, [])

        zcopy4 = ds.copy_zones(z,share_variables=[ds.variable(1)])
        self.assertEqual(zcopy4[0].values(0).shared_zones, [])
        self.assertEqual(zcopy4[0].values(1).shared_zones, [z,zcopy2[0],zcopy4[0]])

        zcopy5 = ds.copy_zones(z,share_variables=[0])
        self.assertEqual(zcopy5[0].values(0).shared_zones, [z,zcopy2[0],zcopy5[0]])
        self.assertEqual(zcopy5[0].values(1).shared_zones, [])

        zcopy6 = ds.copy_zones([z,zcopy],share_variables=[])
        self.assertEqual(len(zcopy6), 2)
        self.assertEqual(zcopy6[0].values(0).shared_zones, [])
        self.assertEqual(zcopy6[0].values(1).shared_zones, [])
        self.assertEqual(zcopy6[1].values(0).shared_zones, [])
        self.assertEqual(zcopy6[1].values(1).shared_zones, [])

        # Cannot get TecplotSystemError, will get TecplotIndexError
        # or TecplotLogicError thrown by engine

        #with self.assertRaises(TecplotSystemError):
        #    ds.copy_zones([z,55],share_variables=[55])

    @skip_on(TecplotOutOfDateEngineError)
    def test_variable_sharing(self):
        tp.new_layout()
        ds = tp.active_page().add_frame().create_dataset('D', ['x','y'])
        z = ds.add_ordered_zone('Z1', (3,))
        zcopy1 = z.copy()
        self.assertEqual(z.values(0).shared_zones, [])
        self.assertEqual(z.values(1).shared_zones, [])
        ds.share_variables(z, zcopy1, ds.variable(0))
        ds.share_variables(0,[1],[1])
        self.assertEqual(z.values(0).shared_zones, [z,zcopy1])
        self.assertEqual(z.values(1).shared_zones, [z,zcopy1])
        ds.branch_variables(z,0, copy_data=False)
        self.assertEqual(z.values(0).shared_zones, [])
        self.assertEqual(z.values(0).passive, True)
        self.assertEqual(z.values(1).shared_zones, [z,zcopy1])
        ds.branch_variables([0],[ds.variable(1)])
        self.assertEqual(z.values(0).shared_zones, [])
        self.assertEqual(z.values(1).shared_zones, [])

        # Cannot get TecplotSystemError, will get TecplotIndexError
        # or TecplotLogicError thrown by engine
        #with self.assertRaises(TecplotSystemError):
        #    ds.share_variables(z, 55, ds.variable(0))

    @skip_on(TecplotOutOfDateEngineError)
    def test_connectivity_sharing(self):
        tp.new_layout()
        ds = tp.active_page().add_frame().create_dataset('D', ['x','y'])
        z_fe = ds.add_fe_zone(tp.constant.ZoneType.FELineSeg, 'Z1', 3, 2)
        z_poly = ds.add_poly_zone(tp.constant.ZoneType.FEPolygon, 'Z1', 3, 1, 1)

        with self.assertRaises(TecplotSystemError):
            ds.share_connectivity(z_fe,[z_poly])
        z_fe2 = z_fe.copy()
        z_poly2 = z_poly.copy()
        self.assertEqual(z_fe2.shared_connectivity, [z_fe,z_fe2])
        self.assertEqual(z_poly2.shared_connectivity, [z_poly,z_poly2])

        ds.branch_connectivity(z_fe)
        ds.branch_connectivity([3])
        self.assertEqual(z_fe2.shared_connectivity, [])
        self.assertEqual(z_poly.shared_connectivity, [])
        ds.share_connectivity(0, [2])
        ds.share_connectivity(z_poly,z_poly2)
        self.assertEqual(z_fe2.shared_connectivity, [z_fe,z_fe2])
        self.assertEqual(z_poly2.shared_connectivity, [z_poly,z_poly2])

    def test_no_matching_pattern(self):
        tp.new_layout()
        ds = tp.data.load_tecplot(self.filenames['2x2x3_overlap'])
        with self.assertRaises(TecplotPatternMatchError):
            z = ds.zone('No Zone')
        with self.assertRaises(TecplotPatternMatchError):
            v = ds.variable('No Va[r]iable')

    def test_out_of_date_sdk(self):
        if __debug__:
            oldver = tp.tecutil.tecutil_connector.SDKVersion(0,0,0,0)
            sdkver = tp.version.sdk_version_info
            try:
                tp.version.sdk_version_info = oldver

                tp.new_layout()
                ds = tp.data.load_tecplot(self.filenames['2x2x3_overlap'])

                with self.assertRaises(TecplotOutOfDateEngineError):
                    n = ds.num_solution_times
                with self.assertRaises(TecplotOutOfDateEngineError):
                    x = ds.solution_times

            finally:
                tp.version.sdk_version_info = sdkver


class TestDatasetExamples(unittest.TestCase):
    def test_doc_VariablesNamedTuple(self):
        tp.new_layout()
        with loaded_sample_data('3x3x3_p'):
            dataset = tp.active_frame().dataset
            result = tp.data.query.probe_at_position(0,0.1,0.3)
            data = dataset.VariablesNamedTuple(*result.data)
            msg = '(x, p) = ({:.2f}, {:.2f})'.format(data.X, data.P)
            self.assertEqual(msg, '(x, p) = (0.00, -0.02)')


if __name__ == '__main__':
    from .. import main
    main()
