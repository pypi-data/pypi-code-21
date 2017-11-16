from __future__ import unicode_literals

import base64
import numpy as np
import os
import unittest
import zlib

from tempfile import NamedTemporaryFile

import tecplot as tp
from tecplot.tecutil import _tecutil, sv, IndexSet
from tecplot.constant import *
from tecplot.exception import *
from .. import patch_tecutil
from tecplot.tecutil import ArgList

from ..sample_data import sample_data_file, loaded_sample_layout

class TestProbeAtPosition(unittest.TestCase):

    def setUp(self):
        self.filenames = {
            '3x3x3_p' : sample_data_file('3x3x3_p'),
            '3x3x1_p' : sample_data_file('3x3x1_p'),
            '3x1x3_p' : sample_data_file('3x1x3_p'),
            '1x3x3_p' : sample_data_file('1x3x3_p'),
            '2x2x3_overlap' :sample_data_file('2x2x3_overlap')}

    def tearDown(self):
        for f in self.filenames.values():
            os.remove(f)

    def test_probe_3d(self):
        tp.new_layout()
        ds = tp.data.load_tecplot(self.filenames['3x3x3_p'])
        fr = tp.active_frame()
        fr.plot_type = PlotType.Cartesian3D
        data,cell,zone = tp.data.query.probe_at_position(.1,.3,.5)
        self.assertTrue(np.allclose(data, [.1,.3,.5,.125]))
        self.assertTrue(np.allclose(cell,[0,0,0]))
        self.assertEqual(zone, ds.zone(0))
        self.assertEqual(data[0], 0.1)
        self.assertEqual(data[1], 0.3)
        self.assertEqual(data[2], 0.5)
        self.assertEqual(data[3], 0.125)

        self.assertEqual(data[3], data[ds.variable('P').index])
        self.assertEqual(data[3], data[list(ds.variables('P'))[0].index])

        res = tp.data.query.probe_at_position(.1,.35,.5,starting_cell=cell,
                                        starting_zone=zone)
        data,cell,zone = res
        self.assertTrue(np.allclose(data, [.1,.35,.5,.15]))
        self.assertTrue(np.allclose(cell,[0,0,0]))
        self.assertEqual(zone, ds.zone(0))
        self.assertEqual(data[0], 0.1)
        self.assertEqual(data[1], 0.35)
        self.assertEqual(data[2], 0.5)
        self.assertEqual(data[3], 0.15)

    def test_probe_overlapping_zones(self):
        tp.new_layout()
        ds = tp.data.load_tecplot(self.filenames['2x2x3_overlap'])
        zone1,zone2 = ds.zones()

        # probe_at_position in zone1 only region
        res = tp.data.query.probe_at_position(.1,.3,.5)
        self.assertTrue(np.allclose(res.data,[0.1, 0.3, 0.5, 0.35]))
        self.assertEqual(res.cell, (0,0,0))
        self.assertEqual(res.zone, zone1)

        res = tp.data.query.probe_at_position(.1,.3,.5,
            starting_cell=res.cell,starting_zone=res.zone)
        self.assertTrue(np.allclose(res.data,[0.1, 0.3, 0.5, 0.35]))
        self.assertEqual(res.cell, (0,0,0))
        self.assertEqual(res.zone, zone1)

        res = tp.data.query.probe_at_position(.1,.3,.5,
            starting_cell=res.cell,starting_zone=zone2)
        self.assertTrue(np.allclose(res.data,[0.1, 0.3, 0.5, 0.35]))
        self.assertEqual(res.cell, (0,0,0))
        self.assertEqual(res.zone, zone1)

        # probe_at_position in shared region
        res = tp.data.query.probe_at_position(.1,.3,1.5)
        self.assertTrue(np.allclose(res.data,[0.1, 0.3, 1.5, 0.15]))
        self.assertEqual(res.cell, (0,0,1))
        self.assertEqual(res.zone, zone1)

        res = tp.data.query.probe_at_position(.1,.3,1.5,
            starting_cell=res.cell,starting_zone=res.zone)
        self.assertTrue(np.allclose(res.data,[0.1, 0.3, 1.5, 0.15]))
        self.assertEqual(res.cell, (0,0,1))
        self.assertEqual(res.zone, zone1)

        res = tp.data.query.probe_at_position(.1,.3,1.5,
            starting_cell=res.cell,starting_zone=zone1)
        self.assertTrue(np.allclose(res.data,[0.1, 0.3, 1.5, 0.15]))
        self.assertEqual(res.cell, (0,0,1))
        self.assertEqual(res.zone, zone1)

        res = tp.data.query.probe_at_position(.1,.3,1.5,
            starting_cell=res.cell,starting_zone=zone2)
        self.assertTrue(np.allclose(res.data,[0.1, 0.3, 1.5, 0.05]))
        self.assertEqual(res.cell, (0,0,0))
        self.assertEqual(res.zone, zone2)

        # probe_at_position in zone2 only region
        res = tp.data.query.probe_at_position(.1,.3,2.5)
        self.assertTrue(np.allclose(res.data,[0.1, 0.3, 2.5, 0.45]))
        self.assertEqual(res.cell, (0,0,1))
        self.assertEqual(res.zone, zone2)

        res = tp.data.query.probe_at_position(.1,.3,2.5,
            starting_cell=res.cell,starting_zone=res.zone)
        self.assertTrue(np.allclose(res.data,[0.1, 0.3, 2.5, 0.45]))
        self.assertEqual(res.cell, (0,0,1))
        self.assertEqual(res.zone, zone2)

        res = tp.data.query.probe_at_position(.1,.3,2.5,
            starting_cell=res.cell,starting_zone=zone1)
        self.assertTrue(np.allclose(res.data,[0.1, 0.3, 2.5, 0.45]))
        self.assertEqual(res.cell, (0,0,1))
        self.assertEqual(res.zone, zone2)

    def test_probe_3d_data_in_2d(self):
        tp.new_layout()
        ds = tp.data.load_tecplot(self.filenames['3x3x3_p'])
        fr = tp.active_frame()
        fr.plot_type = PlotType.Cartesian2D
        result = tp.data.query.probe_at_position(.15,.8)
        data,cell,zone = result.data,result.cell,result.zone
        self.assertTrue(np.allclose(data, [.15,.8,0,.85]))
        self.assertTrue(np.allclose(cell,[0,1,0]))
        self.assertEqual(zone, ds.zone(0))
        self.assertEqual(data[0], 0.15)
        self.assertEqual(data[1], 0.8)
        self.assertEqual(data[2], 0.)
        self.assertEqual(data[3], 0.85)

    def test_probe_2d(self):
        tp.new_layout()
        ds = tp.data.load_tecplot(self.filenames['3x3x1_p'])
        fr = tp.active_frame()
        fr.plot_type = PlotType.Cartesian2D

        data,cell,zone = tp.data.query.probe_at_position(.1,.7)
        self.assertTrue(np.allclose(data, [.1,.7,.65]))
        self.assertEqual(cell, (0,1,0))
        self.assertEqual(zone, ds.zone(0))


        ds = tp.data.load_tecplot(self.filenames['3x1x3_p'], read_data_option=ReadDataOption.ReplaceInActiveFrame)
        fr = tp.active_frame()
        fr.plot_type = PlotType.Cartesian2D
        fr.plot().axes.y_axis.variable = ds.variable('Z')

        data,cell,zone = tp.data.query.probe_at_position(.1,.7)
        self.assertTrue(np.allclose(data, [.1,0,.7,.65]))
        self.assertEqual(cell, (0,0,1))
        self.assertEqual(zone, ds.zone(0))
        self.assertEqual(data[3], data[ds.variable('P').index])


        ds = tp.data.load_tecplot(self.filenames['1x3x3_p'], read_data_option=ReadDataOption.ReplaceInActiveFrame)
        fr = tp.active_frame()
        fr.plot_type = PlotType.Cartesian2D
        fr.plot().axes.x_axis.variable = ds.variable('Y')
        fr.plot().axes.y_axis.variable = ds.variable('Z')

        data,cell,zone = tp.data.query.probe_at_position(.1,.7)
        self.assertTrue(np.allclose(data, [0,.1,.7,.65]))
        self.assertEqual(cell, (0,0,1))
        self.assertEqual(zone, ds.zone(0))
        self.assertEqual(data[3], data[ds.variable('P').index])

    def DISABLED_test_logic_errors(self):
        tp.new_layout()
        fr0 = tp.active_frame()
        ds0 = tp.data.load_tecplot(self.filenames['3x3x3_p'])
        fr1 = tp.active_page().add_frame()
        ds1 = tp.data.load_tecplot(self.filenames['3x3x3_p'])
        with self.assertRaises(TecplotValueError):
            tp.data.query.probe_at_position(.1,.3,.5,dataset=ds0,frame=fr1)
        with self.assertRaises(TecplotLogicError):
            tp.data.query.probe_at_position(.1,.3,.5, starting_cell=(0,0,0))
        with self.assertRaises(TecplotLogicError):
            class A():
                index = -10
            tp.data.query.probe_at_position(.1,.3,.5,starting_cell=(0,0,0),
                                      starting_zone=A())

    def test_probe_zones(self):
        ds = tp.data.load_tecplot(self.filenames['2x2x3_overlap'], read_data_option=ReadDataOption.ReplaceInActiveFrame)
        fr = tp.active_frame()
        fr.plot_type = PlotType.Cartesian3D
        zone1,zone2 = ds.zones()

        res = tp.data.query.probe_at_position(.1,.3,1.5,zones=[zone1])
        self.assertTrue(np.allclose(res.data,[0.1, 0.3, 1.5, 0.15]))
        self.assertEqual(res.cell, (0,0,1))
        self.assertEqual(res.zone, zone1)

        res = tp.data.query.probe_at_position(.1,.3,1.5,zones=[zone2])
        self.assertTrue(np.allclose(res.data,[0.1, 0.3, 1.5, 0.05]))
        self.assertEqual(res.cell, (0,0,0))
        self.assertEqual(res.zone, zone2)

    def test_probe_dataset(self):
        tp.new_layout()
        fr0 = tp.active_frame()
        ds0 = tp.data.load_tecplot(self.filenames['3x3x3_p'])
        fr1 = tp.active_page().add_frame()
        ds1 = tp.data.load_tecplot(self.filenames['3x3x3_p'])

        fr1.activate()
        res_a = tp.data.query.probe_at_position(.1,.3,.7,dataset=ds0)
        fr1.activate()
        res_b = tp.data.query.probe_at_position(.1,.3,.7,frame=fr0)
        fr1.activate()
        res_c = tp.data.query.probe_at_position(.1,.3,.7,dataset=ds0,frame=fr0)

        self.assertTrue(np.allclose(res_a.data,res_b.data))
        self.assertEqual(res_a.cell, res_b.cell)
        self.assertEqual(res_a.zone, res_b.zone)

        self.assertTrue(np.allclose(res_a.data,res_c.data))
        self.assertEqual(res_a.cell, res_c.cell)
        self.assertEqual(res_a.zone, res_c.zone)

    def test_non_successful_probe_at_position(self):
        ds0 = tp.data.load_tecplot(self.filenames['3x3x3_p'],
                        read_data_option=ReadDataOption.ReplaceInActiveFrame)
        with self.assertRaises(TecplotSystemError):
            tp.data.query.probe_at_position(-1,0,0)

    def test_assertions(self):
        if __debug__:
            ds = tp.data.load_tecplot(self.filenames['3x3x3_p'])
            with self.assertRaises(TecplotLogicError):
                tp.data.query.probe_at_position(1,2,3,starting_cell=(1,2,3))
            with self.assertRaises(TecplotLogicError):
                tp.data.query.probe_at_position(1,2,3,starting_zone=ds.zone(0))
            with self.assertRaises(TecplotValueError):
                fr = tp.active_page().add_frame()
                tp.data.query.probe_at_position(1,2,3,frame=fr,dataset=ds)

    def test_assert_on_xyline(self):
        tp.new_layout()
        with loaded_sample_layout('3pt_xyline_text') as dataset:
            with self.assertRaises((TecplotLogicError, TecplotSystemError)):
                tp.data.query.probe_at_position(1,2)

if __name__ == '__main__':
    from .. import main
    main()
