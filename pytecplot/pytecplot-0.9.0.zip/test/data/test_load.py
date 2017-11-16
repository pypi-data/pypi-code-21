from __future__ import unicode_literals

import base64
import getpass
import numpy as np
import os
import platform
import sys
import unittest
import warnings
import zlib
import os

from contextlib import contextmanager
from ctypes import *
from os import path
from tempfile import NamedTemporaryFile
from unittest.mock import patch, Mock, PropertyMock

from test import patch_tecutil, skip_on
import tecplot as tp
from tecplot.data import Dataset
from tecplot.tecutil import sv
from tecplot.constant import *
from tecplot.exception import *
from tecplot.layout import Frame

from ..sample_data import sample_data_file


class TestLoadTecplot(unittest.TestCase):

    def setUp(self):
        self.datafiles = [
            sample_data_file('10x10x10_anno'),
            sample_data_file('4zones'),
            sample_data_file('3x3x3_text')]

    def tearDown(self):
        for f in self.datafiles:
            os.remove(f)

    def test_load(self):
        tp.new_layout()
        frame = tp.active_frame()
        dataset = tp.data.load_tecplot(self.datafiles[0])
        self.assertEqual(frame.plot_type, PlotType.Cartesian3D)
        z = dataset.zone(0)
        self.assertEqual(z.name, 'Rectangular zone')
        self.assertEqual(z._shape, (10,10,10))
        vnames = [v.name for v in dataset.variables()]
        self.assertEqual(vnames, ['X','Y','Z'])

    def test_partial_load_zones(self):
        tp.new_layout()
        dataset = tp.data.load_tecplot(self.datafiles[1], zones=[0],
                                       collapse=True)
        zones = [z.name for z in dataset.zones()]
        self.assertEqual(len(zones), 1)
        self.assertIn('Rectangular3D',zones)
        x = dataset.zone('Rectangular3D').values('X')
        self.assertTrue(np.allclose(x[:], [0,.5,1]*9))

        dataset = tp.data.load_tecplot(self.datafiles[1],
            read_data_option=ReadDataOption.ReplaceInActiveFrame, zones=[1,2],
            collapse=True)
        tp.active_frame().plot_type = PlotType.Cartesian3D
        zones = [z.name for z in dataset.zones()]
        self.assertEqual(len(zones), 2)
        self.assertEqual(dataset.zone(0),list(dataset.zones())[0])
        self.assertEqual(dataset.zone(1),list(dataset.zones())[1])
        self.assertIn('Rectangular2D',zones)
        self.assertIn('Line',zones)

        dataset = tp.data.load_tecplot(self.datafiles[1],
        read_data_option=ReadDataOption.ReplaceInActiveFrame, zones=[1,2],
            collapse=False)
        tp.active_frame().plot_type = PlotType.Cartesian3D
        zones = [z.name for z in dataset.zones()]
        self.assertEqual(len(zones), 2)
        self.assertEqual(dataset.zone(1),list(dataset.zones())[0])
        self.assertEqual(dataset.zone(2),list(dataset.zones())[1])
        self.assertIn('Rectangular2D',zones)
        self.assertIn('Line',zones)

    def test_partial_load_variables(self):
        tp.new_layout()
        dataset = tp.data.load_tecplot(self.datafiles[1], zones=[0],
                                       variables=['X','Y'], collapse=True)
        zones = [z.name for z in dataset.zones()]
        self.assertEqual(len(zones),1)
        self.assertIn('Rectangular3D',zones)
        zone = dataset.zone('Rectangular3D')
        variables = [v.name for v in dataset.variables()]
        self.assertEqual(len(variables),2)
        self.assertIn('X', variables)
        self.assertIn('Y', variables)
        y = zone.values('Y')
        self.assertTrue(np.allclose(y[:], [0,0,0,.5,.5,.5,1,1,1]*3))

        dataset = tp.data.load_tecplot(self.datafiles[1], read_data_option=ReadDataOption.ReplaceInActiveFrame, zones=[0],
            variables=[1,2], collapse=True)
        zones = [z.name for z in dataset.zones()]
        self.assertEqual(len(zones),1)
        self.assertIn('Rectangular3D',zones)
        zone = dataset.zone('Rectangular3D')
        variables = [v.name for v in dataset.variables()]
        self.assertEqual(len(variables),2)
        self.assertEqual(dataset.variable(0),list(dataset.variables())[0])
        self.assertEqual(dataset.variable(1),list(dataset.variables())[1])
        self.assertIn('Y', variables)
        self.assertIn('Z', variables)
        z = zone.values('Z')
        self.assertTrue(np.allclose(z[:], [0]*9 + [.5]*9 + [1]*9))

        dataset = tp.data.load_tecplot(self.datafiles[1], read_data_option=ReadDataOption.ReplaceInActiveFrame, zones=[0],
            variables=[1,2], collapse=False)
        zones = [z.name for z in dataset.zones()]
        self.assertEqual(len(zones),1)
        self.assertIn('Rectangular3D',zones)
        zone = dataset.zone('Rectangular3D')
        variables = [v.name for v in dataset.variables()]
        self.assertEqual(len(variables),2)
        self.assertEqual(dataset.variable(1),list(dataset.variables())[0])
        self.assertEqual(dataset.variable(2),list(dataset.variables())[1])
        self.assertIn('Y', variables)
        self.assertIn('Z', variables)
        itr = dataset.variables('Z')
        z = zone.values('Z')
        self.assertTrue(np.allclose(z[:], [0]*9 + [.5]*9 + [1]*9))

    def test_partial_load_skip(self):
        tp.new_layout()
        dataset = tp.data.load_tecplot(self.datafiles[1], zones=[0],
                                       variables=[1,2], collapse=True,
                                       skip=(3,1,1))
        z = dataset.zone(0).values(1)
        self.assertTrue(np.allclose(z[:], [0]*6 + [.5]*6 + [1]*6))

        dataset = tp.data.load_tecplot(self.datafiles[1], read_data_option=ReadDataOption.Replace, zones=[0],
            variables=[1,2], collapse=True, skip=(1,1,3), reset_style=True)
        z = dataset.zone(0).values(1)
        self.assertTrue(np.allclose(z[:], [0]*9 + [1]*9))

    def test_replace(self):
        tp.new_layout()
        dataset = tp.data.load_tecplot(self.datafiles[1], zones=[0],
                                       variables=[1])
        frame1 = tp.active_frame()  # type: Frame
        frame2 = tp.active_page().add_frame()  # type: Frame
        frame2.plot_type = PlotType.Cartesian3D  # force dataset sharing
        ds1 = frame1.dataset
        ds2 = frame2.dataset
        self.assertEqual(dataset, ds1)
        self.assertEqual(ds1, ds2)
        frame1.activate()
        dataset = tp.data.load_tecplot(self.datafiles[0], zones=[0],
                                       variables=[2], read_data_option=ReadDataOption.Replace)
        # Should replace dataset in both frames
        ds1 = frame1.dataset
        ds2 = frame2.dataset
        self.assertEqual(dataset, ds1)
        self.assertEqual(ds1, ds2)

    def test_append_variables(self):

        def create_sample_dataset(dataset_name, var_name):
            dataset = tp.active_frame().create_dataset(dataset_name)
            dataset.add_variable(var_name)
            zone = dataset.add_ordered_zone('Zone', 2)
            zone.values(var_name)[:] = [1, 1]

        plt_1 = NamedTemporaryFile(suffix='.plt', delete=False)
        plt_2 = NamedTemporaryFile(suffix='.plt', delete=False)

        try:
            tp.new_layout()
            create_sample_dataset('ds1', 'A')
            tp.data.save_tecplot_plt(plt_1.name)
            tp.new_layout()
            create_sample_dataset('ds2', 'B')
            tp.data.save_tecplot_plt(plt_2.name)

            tp.new_layout()
            tp.data.load_tecplot(plt_1.name)
            dataset = tp.data.load_tecplot(plt_2.name)

            # Should load vars from both files by default
            self.assertListEqual([V.name for V in dataset.variables()],
                                 ['I', 'A', 'B'])

        finally:
            for file in (plt_1, plt_2):
                if os.path.exists(file.name):
                    file.close()
                    os.remove(file.name)

    def test_append(self):
        tp.new_layout()
        dataset = tp.data.load_tecplot(self.datafiles[1], zones=[0],
                                       collapse=True)
        tp.data.load_tecplot(self.datafiles[1], zones=[1],
                             collapse=True)
        self.assertEqual(len(list(dataset.zones())), 2)
        zones = [z.name for z in dataset.zones()]
        self.assertIn('Rectangular3D', zones)
        self.assertIn('Rectangular2D', zones)

        tp.new_layout()
        ds = tp.data.load_tecplot(self.datafiles[0])
        tp.data.load_tecplot(self.datafiles[1])
        self.assertEqual(len(list(ds.zones())), 5)

        tp.new_layout()
        ds = tp.active_frame().dataset
        ds = tp.data.load_tecplot(self.datafiles[1])
        self.assertEqual(len(list(ds.zones())), 4)

        tp.new_layout()
        fr0 = tp.active_frame()
        ds = tp.data.load_tecplot(self.datafiles[0])
        fr1 = tp.active_page().add_frame()
        fr1.plot_type = PlotType.Cartesian2D
        tp.data.load_tecplot(self.datafiles[1], read_data_option=ReadDataOption.ReplaceInActiveFrame)
        self.assertNotEqual(fr0.dataset, fr1.dataset)

    def test_all_options(self):
        tp.new_layout()
        ds = tp.data.load_tecplot(self.datafiles[1],
            frame=tp.active_frame(),
            read_data_option=ReadDataOption.ReplaceInActiveFrame,
            reset_style=True,
            initial_plot_first_zone_only=False,
            initial_plot_type=PlotType.Automatic,
            include_text=True,
            include_geom=True,
            include_custom_labels=True,
            include_data=True,
            assign_strand_ids=False,
            add_zones_to_existing_strands=False,
            zones=[0,1,2,3],
            variables=[0,1,2],
            collapse=False,
            skip=(1,1,1))
        self.assertIsInstance(ds, tp.data.Dataset)

        tp.new_layout()
        ds = tp.data.load_tecplot(self.datafiles[1],
            frame=tp.active_frame(),
            read_data_option=ReadDataOption.ReplaceInActiveFrame,
            reset_style=False,
            initial_plot_first_zone_only=True,
            initial_plot_type=PlotType.Sketch,
            include_text=False,
            include_geom=False,
            include_custom_labels=False,
            include_data=False,
            assign_strand_ids=True,
            add_zones_to_existing_strands=True,
            zones=[2,3],
            variables=[1,2],
            collapse=True,
            skip=(2,2,2))
        self.assertIsInstance(ds, tp.data.Dataset)
        self.assertEqual(len(list(ds.zones())), 0)

    def test_multiple(self):
        tp.new_layout()
        ds = tp.data.load_tecplot(self.datafiles[:2])
        self.assertEqual(len(list(ds.zones())),5)

    def test_ascii(self):
        tp.new_layout()
        ds = tp.data.load_tecplot(self.datafiles[2])
        self.assertEqual(len(list(ds.zones())),1)
        z = ds.zone(0)
        self.assertEqual(z.name, 'Rectangular zone')
        self.assertEqual(z._shape, (3,3,3))
        vnames = [v.name for v in ds.variables()]
        self.assertEqual(vnames, ['X','Y','Z'])

    def test_multiple_ascii_bin(self):
        tp.new_layout()
        ds = tp.data.load_tecplot(self.datafiles[1:3])
        self.assertEqual(len(list(ds.zones())),5)

    def test_bad_variable_type(self):
        with self.assertRaises(TecplotTypeError):
            tp.data.load_tecplot(self.datafiles[0], variables=[None])

    def test_readx_failure(self):
        def mock_datasetreadx(arglist):
            return False
        with patch('tecplot.data.load._tecutil.DataSetReadX',
                   Mock(side_effect=mock_datasetreadx)):
            with self.assertRaises(TecplotSystemError):
                tp.data.load_tecplot(self.datafiles[0])

    def test_timestrands(self):
        instr = []
        def mock_datasetreadx(arglist, instr=instr):
            instr *= 0 # clear the list
            instr += [arglist[sv.ASSIGNSTRANDIDS]]
            return True
        with patch('tecplot.data.load._tecutil.DataSetReadX',
                   Mock(side_effect=mock_datasetreadx)):
            tp.data.load_tecplot('data.plt')
            self.assertEqual(instr, [True])


class TestLoadCGNS(unittest.TestCase):

    def test_file_combinations(self):
        instr = []
        def mock_datasetreadx(arglist, instr=instr):
            instr *= 0 # clear the list
            instr += list(arglist[sv.FILENAMESORINSTRUCTIONS])
            return True
        with patch('tecplot.data.load._tecutil.DataSetReadX',
                   Mock(side_effect=mock_datasetreadx)):

            tp.data.load_cgns(['one.cgns', 'two.cgns'])
            self.assertEqual(instr,['STANDARDSYNTAX','1.0','LoaderVersion','V3',
                'CgnsLibraryVersion', '3.1.4',
                'FILELIST_CGNSFILES','2', path.abspath('one.cgns'),
                path.abspath('two.cgns'), 'LoadBCs', 'Yes'])

    def test_assertions(self):
        if __debug__:
            with self.assertRaises(TecplotTypeError):
                tp.data.load_cgns('one.cas', average_to_nodes=True)

    def test_zone_variable_selection(self):
        instr = []
        def mock_datasetreadx(arglist, instr=instr):
            instr *= 0 # clear the list
            instr += list(arglist[sv.FILENAMESORINSTRUCTIONS])
            return True

        with patch('tecplot.data.load._tecutil.DataSetReadX',
                   Mock(side_effect=mock_datasetreadx)):
            tp.data.load_cgns('one.cgns', zones=[0,1])
            self.assertEqual(instr,['STANDARDSYNTAX','1.0','LoaderVersion','V3',
                                    'CgnsLibraryVersion', '3.1.4',
                'FILELIST_CGNSFILES','1',path.abspath('one.cgns'),'ZoneList',
                '0,1', 'LoadBCs', 'Yes'])

            tp.data.load_cgns('one.cgns', variables=[0,1])
            self.assertEqual(instr,['STANDARDSYNTAX','1.0','LoaderVersion','V3',
                                    'CgnsLibraryVersion', '3.1.4',
                'FILELIST_CGNSFILES','1',path.abspath('one.cgns'),'VarList',
                '0,1', 'LoadBCs', 'Yes'])

    def test_all_options(self):
        instr = []
        def mock_datasetreadx(arglist, instr=instr):
            instr *= 0 # clear the list
            instr += list(arglist[sv.FILENAMESORINSTRUCTIONS])
            return True
        with patch('tecplot.data.load._tecutil.DataSetReadX',
                   Mock(side_effect=mock_datasetreadx)):
            tp.data.load_cgns(['one.cgns', 'two.cgns'],
                frame=tp.active_frame(),
                read_data_option=ReadDataOption.ReplaceInActiveFrame, reset_style=True,
                initial_plot_first_zone_only=True,
                initial_plot_type=PlotType.Automatic, zones=[0,1],
                variables=[0,1], load_convergence_history=True,
                combine_fe_sections=True, average_to_nodes='Arithmetic',
                uniform_grid=True, assign_strand_ids=True,
                add_zones_to_existing_strands=True,
                include_boundary_conditions=True)
            self.assertEqual(instr,['STANDARDSYNTAX', '1.0', 'LoaderVersion',
                'V3', 'CgnsLibraryVersion', '3.1.4',
                'FILELIST_CGNSFILES', '2', path.abspath('one.cgns'),
                path.abspath('two.cgns'), 'ZoneList', '0,1', 'VarList', '0,1',
                'UniformGridStructure', 'Yes',
                'SectionLoad', 'SeparateZones', 'LoadBCs', 'Yes',
                'LoadConvergenceHistory', 'Yes', 'AssignStrandIDs', 'Yes'])

        with patch('tecplot.data.load._tecutil.DataSetReadX',
                   Mock(side_effect=mock_datasetreadx)):
            tp.data.load_cgns(['one.cgns', 'two.cgns'],
                frame=tp.active_frame(),
                read_data_option=ReadDataOption.ReplaceInActiveFrame,
                              reset_style=True,
                initial_plot_first_zone_only=True,
                initial_plot_type=PlotType.Automatic, zones=[0,1],
                variables=[0,1], load_convergence_history=True,
                average_to_nodes=None,
                combine_fe_sections=True,
                uniform_grid=True, assign_strand_ids=True,
                add_zones_to_existing_strands=True,
                include_boundary_conditions=True)
            self.assertEqual(instr,['STANDARDSYNTAX', '1.0', 'LoaderVersion',
                'V3', 'CgnsLibraryVersion', '3.1.4',
                'FILELIST_CGNSFILES', '2', path.abspath('one.cgns'),
                path.abspath('two.cgns'), 'ZoneList', '0,1', 'VarList', '0,1',
                'AverageToNodes', 'No',
                'UniformGridStructure', 'Yes',
                'SectionLoad', 'SeparateZones', 'LoadBCs', 'Yes',
                'LoadConvergenceHistory', 'Yes', 'AssignStrandIDs', 'Yes'])

        with patch('tecplot.data.load._tecutil.DataSetReadX',
                   Mock(side_effect=mock_datasetreadx)):
            tp.data.load_cgns(['one.cgns', 'two.cgns'],
                frame=tp.active_frame(),
                read_data_option=ReadDataOption.ReplaceInActiveFrame,
                              reset_style=True,
                initial_plot_first_zone_only=True,
                initial_plot_type=PlotType.Automatic, zones=[0,1],
                variables=[0,1], load_convergence_history=True,
                average_to_nodes='Laplacian',
                combine_fe_sections=True,
                uniform_grid=True, assign_strand_ids=True,
                add_zones_to_existing_strands=True,
                include_boundary_conditions=True)
            self.assertEqual(instr,['STANDARDSYNTAX', '1.0', 'LoaderVersion',
                'V3', 'CgnsLibraryVersion', '3.1.4',
                'FILELIST_CGNSFILES', '2', path.abspath('one.cgns'),
                path.abspath('two.cgns'), 'ZoneList', '0,1', 'VarList', '0,1',
                'AveragingMethod', 'Laplacian',
                'UniformGridStructure', 'Yes',
                'SectionLoad', 'SeparateZones', 'LoadBCs', 'Yes',
                'LoadConvergenceHistory', 'Yes', 'AssignStrandIDs', 'Yes'])



class TestLoadFluent(unittest.TestCase):
    def tearDown(self):
        warnings.simplefilter('default')

    def test_file_combinations(self):
        instr = []
        def mock_datasetreadx(arglist, instr=instr):
            instr *= 0 # clear the list
            instr += list(arglist[sv.FILENAMESORINSTRUCTIONS])
            return True

        warnings.simplefilter('ignore')
        SDKVER = tp.sdk_version_info

        def assert_instr(instr, expected):
            if SDKVER >= (2017, 2):
                expected += ['LoadAdditionalQuantities','Yes']
            self.assertEqual(instr,expected)

        with patch('tecplot.data.load._tecutil.DataSetReadX',
                   Mock(side_effect=mock_datasetreadx)):

            tp.data.load_fluent(['one.cas', 'two.cas'],
                data_filenames=['one.dat', 'two.xml'],
                                save_uncompressed_files=True)
            assert_instr(instr, ['STANDARDSYNTAX', '1.0', 'Append', 'Yes',
                'LoadOption', 'MultipleCaseAndData', 'FILELIST_Files', '4',
                'one.cas', 'two.cas', 'one.dat', 'two.xml', 'AssignStrandIDs',
                'Yes', 'SaveUncompressedFiles', 'Yes'])

            tp.data.load_fluent(['one.cas', 'two.cas'],
                data_filenames=['one.dat', 'two.xml'])
            assert_instr(instr, ['STANDARDSYNTAX', '1.0', 'Append', 'Yes',
                'LoadOption', 'MultipleCaseAndData', 'FILELIST_Files', '4',
                'one.cas', 'two.cas', 'one.dat', 'two.xml', 'AssignStrandIDs',
                'Yes', 'SaveUncompressedFiles', 'No'])

            tp.data.load_fluent(['one.cas', 'two.cas'])
            assert_instr(instr, ['STANDARDSYNTAX', '1.0', 'Append', 'Yes',
                'LoadOption', 'MultipleCaseAndData', 'FILELIST_Files', '2',
                'one.cas', 'two.cas', 'AssignStrandIDs', 'Yes',
                                 'SaveUncompressedFiles', 'No'])

            tp.data.load_fluent('one.cas')
            assert_instr(instr, ['STANDARDSYNTAX', '1.0', 'Append', 'Yes',
                'LoadOption', 'MultipleCaseAndData', 'FILELIST_Files', '1',
                'one.cas', 'AssignStrandIDs', 'Yes',
                                 'SaveUncompressedFiles', 'No'])

            tp.data.load_fluent(data_filenames=['one.dat'])
            assert_instr(instr, ['STANDARDSYNTAX', '1.0', 'Append', 'Yes',
                'LoadOption', 'ResidualsOnly', 'FILENAME_DataFile', 'one.dat',
                'AssignStrandIDs', 'Yes', 'SaveUncompressedFiles', 'No'])

            tp.data.load_fluent(data_filenames='one.dat')
            assert_instr(instr, ['STANDARDSYNTAX', '1.0', 'Append', 'Yes',
                'LoadOption', 'ResidualsOnly', 'FILENAME_DataFile', 'one.dat',
                'AssignStrandIDs', 'Yes', 'SaveUncompressedFiles', 'No'])

            tp.data.load_fluent('one.cas',
                data_filenames=['one.dat', 'two.xml'])
            assert_instr(instr, ['STANDARDSYNTAX', '1.0', 'Append', 'Yes',
                'LoadOption', 'MultipleCaseAndData', 'FILELIST_Files', '3',
                'one.cas', 'one.dat', 'two.xml', 'AssignStrandIDs', 'Yes',
                                 'SaveUncompressedFiles', 'No'])

            tp.data.load_fluent('one.cas', data_filenames=['one.dat'])
            assert_instr(instr, ['STANDARDSYNTAX', '1.0', 'Append', 'Yes',
                'LoadOption', 'MultipleCaseAndData', 'FILELIST_Files', '2',
                'one.cas', 'one.dat', 'AssignStrandIDs', 'Yes',
                                 'SaveUncompressedFiles', 'No'])

            tp.data.load_fluent('one.cas', data_filenames='one.dat')
            assert_instr(instr, ['STANDARDSYNTAX', '1.0', 'Append', 'Yes',
                'LoadOption', 'MultipleCaseAndData', 'FILELIST_Files', '2',
                'one.cas', 'one.dat', 'AssignStrandIDs', 'Yes',
                                 'SaveUncompressedFiles', 'No'])

    def test_assertions(self):
        if __debug__:
            with self.assertRaises(TecplotTypeError):
                tp.data.load_fluent(data_filenames=['a','b'])
            with self.assertRaises(TecplotTypeError):
                tp.data.load_fluent('one.cas', zones='blah')
            with self.assertRaises(TecplotTypeError):
                tp.data.load_fluent('one.cas', zones='BoundariesOnly',
                    variables=['a'])
            with self.assertRaises(TecplotTypeError):
                tp.data.load_fluent()
            with self.assertRaises(TecplotTypeError):
                tp.data.load_fluent('one.cas', average_to_nodes=True)

    def test_sdk_version_differences(self):
        instr = []
        def mock_datasetreadx(arglist, instr=instr):
            instr *= 0 # clear the list
            instr += list(arglist[sv.FILENAMESORINSTRUCTIONS])
            return True
        expected = ['STANDARDSYNTAX','1.0','Append','Yes',
                    'LoadOption','MultipleCaseAndData','FILELIST_Files','1',
                    'one.cas','AssignStrandIDs','Yes',
                    'SaveUncompressedFiles', 'No']
        if tp.sdk_version_info >= (2017, 2):
            expected += ['LoadAdditionalQuantities','Yes']

        tp.data.load.__warningregistry__ = {}
        warnings.simplefilter("always")
        with warnings.catch_warnings(record=True) as w:
            with patch('tecplot.data.load._tecutil.DataSetReadX',
                       Mock(side_effect=mock_datasetreadx)):
                tp.data.load_fluent('one.cas')
                self.assertEqual(instr, expected)

                if __debug__:
                    #if tp.sdk_version_info < (2017, 2):
                    #    self.assertEqual(len(w), 1)
                    #else:
                    #    self.assertEqual(len(w), 0)

                    w *= 0

                    sdkver = tp.version.sdk_version_info
                    try:
                        tp.version.sdk_version_info = (0, 0, 0)
                        tp.data.load_fluent('one.cas')
                        self.assertEqual(len(w), 1)
                    finally:
                        tp.version.sdk_version_info = sdkver

    def test_zone_variable_selection(self):
        warnings.simplefilter('ignore')
        instr = []
        def mock_datasetreadx(arglist, instr=instr):
            instr *= 0 # clear the list
            instr += list(arglist[sv.FILENAMESORINSTRUCTIONS])
            return True

        with patch('tecplot.data.load._tecutil.DataSetReadX',
                   Mock(side_effect=mock_datasetreadx)):
            tp.data.load_fluent('one.cas', zones='CellsOnly')
            expected = ['STANDARDSYNTAX','1.0','Append','Yes',
                'LoadOption','MultipleCaseAndData','FILELIST_Files','1',
                'one.cas','GridZones','CellsOnly','AssignStrandIDs','Yes',
                        'SaveUncompressedFiles', 'No']
            if tp.sdk_version_info >= (2017, 2):
                expected += ['LoadAdditionalQuantities','Yes']
            self.assertEqual(instr,expected)

            tp.data.load_fluent('one.cas', zones=[0,1])
            expected = ['STANDARDSYNTAX','1.0', 'Append', 'Yes',
                'LoadOption','MultipleCaseAndData','FILELIST_Files','1',
                'one.cas','GridZones','SelectedZones','ZoneList','1,2',
                'AssignStrandIDs','Yes',
                        'SaveUncompressedFiles', 'No']
            if tp.sdk_version_info >= (2017, 2):
                expected += ['LoadAdditionalQuantities','Yes']
            self.assertEqual(instr,expected)

            tp.data.load_fluent('one.cas', variables=['aa','bb'])
            expected = ['STANDARDSYNTAX','1.0','Append','Yes',
                'LoadOption','MultipleCaseAndData','FILELIST_Files','1',
                'one.cas','GridZones','SelectedZones','VarNameList','aa\nbb',
                'AssignStrandIDs','Yes', 'SaveUncompressedFiles', 'No']
            if tp.sdk_version_info >= (2017, 2):
                expected += ['LoadAdditionalQuantities','Yes']
            self.assertEqual(instr,expected)

            tp.data.load_fluent('one.cas', zones=[0,1],
                variables=['aa','bb'])
            expected = ['STANDARDSYNTAX','1.0','Append','Yes',
                'LoadOption','MultipleCaseAndData','FILELIST_Files','1',
                'one.cas','GridZones','SelectedZones','ZoneList','1,2',
                'VarNameList','aa\nbb','AssignStrandIDs','Yes',
                        'SaveUncompressedFiles', 'No']
            if tp.sdk_version_info >= (2017, 2):
                expected += ['LoadAdditionalQuantities','Yes']
            self.assertEqual(instr,expected)
        warnings.simplefilter('always')

    # def test_average_to_nodes_option(self):
    #     warnings.simplefilter('ignore')
    #     instr = []
    #     def mock_datasetreadx(arglist, instr=instr):
    #         instr *= 0 # clear the list
    #         instr += list(arglist[sv.FILENAMESORINSTRUCTIONS])
    #         return True
    #     with patch('tecplot.data.load._tecutil.DataSetReadX',
    #                Mock(side_effect=mock_datasetreadx)):
    #
    #         tp.data.load_fluent(
    #             case_filenames=['one.cas', 'two.cas'],
    #             append=False,
    #             data_filenames=['one.dat', 'two.xml'], frame=tp.active_frame(),
    #             average_to_nodes=None)
    #
    #         expected = ['STANDARDSYNTAX','1.0','LoadOption',
    #             'MultipleCaseAndData','FILELIST_Files','4','one.cas',
    #             'two.cas','one.dat','two.xml','UnsteadyOption',
    #             'AverageToNodes','No']
    #
    #         self.assertEqual(instr, expected)


    def test_all_options(self):
        warnings.simplefilter('ignore')
        instr = []
        def mock_datasetreadx(arglist, instr=instr):
            instr *= 0 # clear the list
            instr += list(arglist[sv.FILENAMESORINSTRUCTIONS])
            return True
        with patch('tecplot.data.load._tecutil.DataSetReadX',
                   Mock(side_effect=mock_datasetreadx)):

            tp.data.load_fluent(
                case_filenames=['one.cas', 'two.cas'],
                data_filenames=['one.dat', 'two.xml'], frame=tp.active_frame(),
                append=False, assign_strand_ids=True,
                add_zones_to_existing_strands=True, time_interval=3.14,
                variables=['aa','bb'], zones=[0,1], include_particle_data=True,
                all_poly_zones=True, average_to_nodes='Arithmetic',
                include_additional_quantities=False)
            expected = ['STANDARDSYNTAX','1.0','LoadOption',
                'MultipleCaseAndData','FILELIST_Files','4','one.cas',
                'two.cas','one.dat','two.xml','UnsteadyOption',
                'ApplyConstantTimeInterval','TimeInterval','3.14',
                'GridZones','SelectedZones','ZoneList','1,2','VarNameList',
                'aa\nbb','IncludeParticleData','Yes','AllPolyZones','Yes',
                'AssignStrandIDs','Yes',
                'AddZonesToExistingStrands','Yes',
                'SaveUncompressedFiles', 'No']
            if tp.sdk_version_info >= (2017, 2):
                expected += ['LoadAdditionalQuantities', 'No']

            self.assertEqual(instr, expected)

            tp.data.load_fluent('one.cas', assign_strand_ids=None)
            expected = ['STANDARDSYNTAX','1.0', 'Append', 'Yes',
                'LoadOption','MultipleCaseAndData','FILELIST_Files','1',
                'one.cas', 'SaveUncompressedFiles', 'No']
            if tp.sdk_version_info >= (2017, 2):
                expected += ['LoadAdditionalQuantities','Yes']
            self.assertEqual(instr, expected)

            tp.data.load_fluent('one.cas', assign_strand_ids=None,
                                average_to_nodes=None)

            expected = ['STANDARDSYNTAX','1.0', 'Append', 'Yes',
                'LoadOption','MultipleCaseAndData','FILELIST_Files','1',
                'one.cas', 'AverageToNodes', 'No',
                        'SaveUncompressedFiles', 'No']

            if tp.sdk_version_info >= (2017, 2):
                expected += ['LoadAdditionalQuantities', 'Yes']

            self.assertEqual(instr, expected)

            tp.data.load_fluent('one.cas', assign_strand_ids=None,
                                average_to_nodes='Arithmetic')

            expected = ['STANDARDSYNTAX','1.0', 'Append', 'Yes',
                'LoadOption','MultipleCaseAndData','FILELIST_Files','1',
                'one.cas', 'SaveUncompressedFiles', 'No']

            if tp.sdk_version_info >= (2017, 2):
                expected += ['LoadAdditionalQuantities', 'Yes']

            self.assertEqual(instr, expected)

            tp.data.load_fluent('one.cas', assign_strand_ids=None,
                                average_to_nodes='Laplacian')

            expected = ['STANDARDSYNTAX','1.0', 'Append', 'Yes',
                'LoadOption','MultipleCaseAndData','FILELIST_Files','1',
                'one.cas', 'AveragingMethod', 'Laplacian',
                        'SaveUncompressedFiles', 'No']

            if tp.sdk_version_info >= (2017, 2):
                expected += ['LoadAdditionalQuantities', 'Yes']

            self.assertEqual(instr, expected)

class TestLoadPlot3D(unittest.TestCase):

    def setUp(self):
        tp.new_layout()

    def test_file_combinations(self):
        instr = []
        def mock_datasetreadx(arglist, instr=instr):
            instr *= 0 # clear the list
            instr += list(arglist[sv.FILENAMESORINSTRUCTIONS])
            return True
        with patch('tecplot.data.load._tecutil.DataSetReadX',
                   Mock(side_effect=mock_datasetreadx)):

            if sys.version_info < (3,):
                text = unicode
            else:
                text = str

            for fgrid in ['a.g', ['a.g'], ['a.g','b.g']]:
                if isinstance(fgrid,list):
                    flgrid = fgrid
                else:
                    flgrid = [fgrid]

                tp.data.load_plot3d(fgrid)
                cmds = ['STANDARDSYNTAX','1.0',
                        'FILELIST_GRIDFILES', text(len(flgrid))] + flgrid
                cmds += ['AUTODETECT', 'Yes', 'ASSIGNSTRANDIDS', 'Yes',
                         'LOADBOUNDARY', 'Yes']
                self.assertEqual(instr, cmds)

                for fsol in ['a.q', ['a.q'], ['a.q','b.q']]:
                    if isinstance(fsol,list):
                        flsol = fsol
                    else:
                        flsol = [fsol]
                    if isinstance(fsol,list):
                        ffunc = [f.replace('.q','.f') for f in fsol]
                        flfunc = ffunc
                    else:
                        ffunc = fsol.replace('.q','.f')
                        flfunc = [ffunc]

                    tp.data.load_plot3d(solution_filenames=fsol)
                    cmds = ['STANDARDSYNTAX','1.0',
                            'FILELIST_SOLUTIONFILES', text(len(flsol))]
                    cmds += flsol
                    cmds += ['AUTODETECT', 'Yes', 'ASSIGNSTRANDIDS', 'Yes',
                             'LOADBOUNDARY', 'Yes']
                    self.assertEqual(instr, cmds)

                    tp.data.load_plot3d(function_filenames=ffunc)
                    cmds = ['STANDARDSYNTAX','1.0',
                            'FILELIST_FUNCTIONFILES', text(len(flfunc))]
                    cmds += flfunc
                    cmds += ['AUTODETECT', 'Yes', 'ASSIGNSTRANDIDS', 'Yes',
                             'LOADBOUNDARY', 'Yes']
                    self.assertEqual(instr, cmds)

                    tp.data.load_plot3d(fgrid, function_filenames=ffunc,
                                        append_function_variables=True)
                    cmds = ['STANDARDSYNTAX','1.0',
                            'FILELIST_GRIDFILES', text(len(flgrid))]
                    cmds += flgrid
                    cmds += ['FILELIST_FUNCTIONFILES', text(len(flfunc))]
                    cmds += flfunc
                    cmds += ['AUTODETECT', 'Yes', 'ASSIGNSTRANDIDS', 'Yes',
                             'LOADBOUNDARY', 'Yes']
                    self.assertEqual(instr, cmds)

                    if len(flgrid) <= len(flsol):
                        tp.data.load_plot3d(fgrid, fsol)
                        cmds  = ['STANDARDSYNTAX','1.0',
                                 'FILELIST_GRIDFILES', text(len(flgrid))]
                        cmds += flgrid
                        cmds += ['FILELIST_SOLUTIONFILES', text(len(flsol))]
                        cmds += flsol
                        cmds += ['AUTODETECT', 'Yes', 'ASSIGNSTRANDIDS',
                                 'Yes', 'LOADBOUNDARY', 'Yes']
                        self.assertEqual(instr, cmds)

                        tp.data.load_plot3d(fgrid, fsol, ffunc)
                        cmds  = ['STANDARDSYNTAX','1.0',
                                 'FILELIST_GRIDFILES', text(len(flgrid))]
                        cmds += flgrid
                        cmds += ['FILELIST_SOLUTIONFILES', text(len(flsol))]
                        cmds += flsol
                        cmds += ['FILELIST_FUNCTIONFILES', text(len(flfunc))]
                        cmds += flfunc
                        cmds += ['AUTODETECT', 'Yes', 'ASSIGNSTRANDIDS',
                                 'Yes', 'LOADBOUNDARY', 'Yes']
                        self.assertEqual(instr, cmds)

    def test_with_preexisting_dataset(self):
        instr = []
        def mock_datasetreadx(arglist, instr=instr):
            instr *= 0 # clear the list
            instr += list(arglist[sv.FILENAMESORINSTRUCTIONS])
            return True
        with patch('tecplot.data.load._tecutil.DataSetReadX',
                   Mock(side_effect=mock_datasetreadx)):
            with patch('tecplot.layout.Frame.has_dataset',
                       Mock(return_value=True)):
                class MockDataset(Mock):
                    @property
                    def num_zones(self):
                        return 1
            with patch('tecplot.layout.Frame.has_dataset',
                       Mock(return_value=True)):
                with patch('tecplot.layout.Frame.dataset',
                           PropertyMock(return_value=MockDataset())):
                    # at this point we've mocked that the active frame has
                    # a dataset and that it has one zone.
                    tp.data.load_plot3d('f.g', append=True)
                    cmds = ['STANDARDSYNTAX','1.0', 'Append', 'Yes',
                            'FILELIST_GRIDFILES', '1', 'f.g', 'AUTODETECT',
                            'Yes', 'ASSIGNSTRANDIDS', 'Yes',
                            'ADDTOEXISTINGSTRANDS', 'Yes', 'LOADBOUNDARY',
                            'Yes']
                    self.assertEqual(instr, cmds)

                    tp.data.load_plot3d('f.g', append=False,
                                        add_zones_to_existing_strands=False)
                    cmds = ['STANDARDSYNTAX','1.0', 'Append', 'No',
                            'FILELIST_GRIDFILES', '1', 'f.g', 'AUTODETECT',
                            'Yes', 'ASSIGNSTRANDIDS', 'Yes',
                            'ADDTOEXISTINGSTRANDS', 'No', 'LOADBOUNDARY',
                            'Yes']
                    self.assertEqual(instr, cmds)

                    tp.data.load_plot3d('f.g', append=None,
                                        add_zones_to_existing_strands=None)
                    cmds = ['STANDARDSYNTAX','1.0',
                            'FILELIST_GRIDFILES', '1', 'f.g', 'AUTODETECT',
                            'Yes', 'ASSIGNSTRANDIDS', 'Yes',
                            'LOADBOUNDARY', 'Yes']
                    self.assertEqual(instr, cmds)


    def test_not_including_boundaries(self):
        instr = []
        def mock_datasetreadx(arglist, instr=instr):
            instr *= 0 # clear the list
            instr += list(arglist[sv.FILENAMESORINSTRUCTIONS])
            return True
        with patch('tecplot.data.load._tecutil.DataSetReadX',
                   Mock(side_effect=mock_datasetreadx)):
            tp.data.load_plot3d('f.g')
            cmds = ['STANDARDSYNTAX','1.0',
                    'FILELIST_GRIDFILES', '1', 'f.g', 'AUTODETECT', 'Yes',
                    'ASSIGNSTRANDIDS', 'Yes', 'LOADBOUNDARY', 'Yes']
            self.assertEqual(instr, cmds)

            tp.data.load_plot3d('f.g', assign_strand_ids=False,
                                include_boundaries=False)
            cmds = ['STANDARDSYNTAX','1.0',
                    'FILELIST_GRIDFILES', '1', 'f.g', 'AUTODETECT', 'Yes',
                    'ASSIGNSTRANDIDS', 'No', 'LOADBOUNDARY', 'No']
            self.assertEqual(instr, cmds)

            tp.data.load_plot3d('f.g', assign_strand_ids=None,
                                include_boundaries=None)
            cmds = ['STANDARDSYNTAX','1.0',
                    'FILELIST_GRIDFILES', '1', 'f.g', 'AUTODETECT', 'Yes']
            self.assertEqual(instr, cmds)



    def test_assertions(self):
        if __debug__:
            with self.assertRaises(TecplotValueError):
                tp.data.load_plot3d(grid_filenames=['a.g','b.g'],
                                    solution_filenames=['a.q'])
            with self.assertRaises(TecplotValueError):
                tp.data.load_plot3d(grid_filenames=['a.g','b.g'],
                                    solution_filenames=['a.q'])
            with self.assertRaises(TecplotValueError):
                tp.data.load_plot3d(function_filenames=['a.g','b.g'],
                                    solution_filenames=['a.q'])

            with self.assertRaises(TecplotValueError):
                tp.data.load_plot3d(data_structure='blah')
            with self.assertRaises(TecplotValueError):
                tp.data.load_plot3d(style='blah')

            with self.assertRaises(TecplotValueError):
                tp.data.load_plot3d(data_structure='1D')
            with self.assertRaises(TecplotValueError):
                tp.data.load_plot3d(is_multi_grid=True)
            with self.assertRaises(TecplotValueError):
                tp.data.load_plot3d(style='PLOT3DCLASSIC')

    def test_all_options(self):
        instr = []
        def mock_datasetreadx(arglist, instr=instr):
            instr *= 0 # clear the list
            instr += list(arglist[sv.FILENAMESORINSTRUCTIONS])
            return True
        with patch('tecplot.data.load._tecutil.DataSetReadX',
                   Mock(side_effect=mock_datasetreadx)):

            tp.data.load_plot3d(grid_filenames='a.g', solution_filenames=['a.q','b.q'],
                function_filenames=['a.f','b.f'], name_filename='a.name',
                frame=tp.active_frame(), append=True,
                assign_strand_ids=False, add_zones_to_existing_strands=True,
                data_structure='3DP', is_multi_grid=False,
                style='PLOT3DCLASSIC', ascii_is_double=True,
                ascii_has_blanking=False, uniform_grid=True,
                append_function_variables=True)
            self.assertEqual(instr,['STANDARDSYNTAX', '1.0',
            'FILELIST_GRIDFILES', '1', 'a.g', 'FILELIST_SOLUTIONFILES', '2',
            'a.q', 'b.q', 'FILELIST_FUNCTIONFILES', '2', 'a.f', 'b.f',
            'FILENAME_NAMEFILE', 'a.name', 'AUTODETECT', 'No', 'DATASTRUCTURE',
            '3DP', 'ISMULTIGRID', 'No', 'STYLE', 'PLOT3DCLASSIC',
            'ASCIIISDOUBLE', 'Yes', 'ASCIIHASBLANK', 'No',
            'UNIFORMGRIDSTRUCTURE', 'Yes', 'ASSIGNSTRANDIDS', 'No',
            'APPENDFUNCTIONVARIABLES', 'Yes', 'LOADBOUNDARY', 'Yes'])

            tp.data.load_plot3d('a.g', 'a.q', assign_strand_ids=None)
            self.assertEqual(instr,['STANDARDSYNTAX', '1.0',
            'FILELIST_GRIDFILES', '1', 'a.g', 'FILELIST_SOLUTIONFILES', '1',
            'a.q', 'AUTODETECT', 'Yes', 'LOADBOUNDARY', 'Yes'])

    def test_no_boundary_file(self):
        e = TecplotLogicError('The boundary file does not...')
        with patch('tecplot.data.load._tecplot_loader_load_data', Mock()) as load:
            load.side_effect = e
            ds = tp.data.load_plot3d('a.g', 'a.q', 'a.f')
            self.assertIsInstance(ds, tp.data.Dataset)
            load.side_effect = TecplotLogicError('error')
            with self.assertRaises(TecplotLogicError):
                ds = tp.data.load_plot3d('a.g', 'a.q')


class TestLoadTecplotSZL(unittest.TestCase):

    def setUp(self):
        self._username = os.environ.get('USERNAME', None)
        os.environ['USERNAME'] = 'test'
        tp.new_layout()

    def tearDown(self):
        if self._username is None:
            del os.environ['USERNAME']
        else:
            os.environ['USERNAME'] = self._username

    def test_options(self):
        instr = []
        def mock_datasetreadx(arglist, instr=instr):
            instr *= 0 # clear the list
            instr += list(arglist[sv.FILENAMESORINSTRUCTIONS])
            return True
        with patch('tecplot.data.load._tecutil.DataSetReadX',
                   Mock(side_effect=mock_datasetreadx)):
            tp.data.load_tecplot_szl('a.szplt')
            self.assertEqual(instr,['STANDARDSYNTAX', '1.0',
                'FILELIST_DATAFILES', '1', 'a.szplt'])

            tp.data.load_tecplot_szl('a.szplt', frame=None,
                read_data_option=ReadDataOption.ReplaceInActiveFrame,
                reset_style=False,
                initial_plot_first_zone_only=True,
                initial_plot_type=PlotType.PolarLine,
                assign_strand_ids=False,
                add_zones_to_existing_strands=True)
            self.assertEqual(instr,['STANDARDSYNTAX', '1.0',
                'FILELIST_DATAFILES', '1', 'a.szplt'])

            tp.data.load_tecplot_szl('a.szplt',
                server='server.domain',
                connection_method=RemoteConnectionMethod.Direct,
                user='username',
                ssh_private_keyfile='keyfile')
            self.assertEqual(instr,['STANDARDSYNTAX', '1.0',
                'Connection Method', 'Direct', 'MACHINE', 'server.domain',
                'USER', 'username', 'KEY_PATH', 'keyfile',
                'FILELIST_DATAFILES', '1', 'a.szplt'])

            tp.data.load_tecplot_szl('a.szplt',
                server='server.domain',
                connection_method='Manual',
                user='username',
                ssh_private_keyfile='keyfile')
            self.assertEqual(instr,['STANDARDSYNTAX', '1.0',
                'Connection Method', 'Manual', 'MACHINE', 'server.domain',
                'USER', 'username', 'KEY_PATH', 'keyfile',
                'FILELIST_DATAFILES', '1', 'a.szplt'])

            tp.data.load_tecplot_szl('a.szplt',
                server='server.domain',
                user='username',
                ssh_private_keyfile='keyfile')
            self.assertEqual(instr,['STANDARDSYNTAX', '1.0',
                'Connection Method', 'Tunneled', 'MACHINE', 'server.domain',
                'USER', 'username', 'KEY_PATH', 'keyfile',
                'FILELIST_DATAFILES', '1', 'a.szplt'])

            user = getpass.getuser()
            homedir = path.expanduser('~')
            keyfile = path.join(homedir, '.ssh', 'id_rsa')

            tp.data.load_tecplot_szl(['a.szplt', 'b.szplt'], server='server.domain')
            self.assertEqual(instr,['STANDARDSYNTAX', '1.0',
                'Connection Method', 'Tunneled', 'MACHINE', 'server.domain',
                'USER', user, 'KEY_PATH', keyfile,
                'FILELIST_DATAFILES', '2', 'a.szplt', 'b.szplt'])

if __name__ == '__main__':
    from .. import main
    main()
