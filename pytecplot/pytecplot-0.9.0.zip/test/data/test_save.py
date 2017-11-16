from __future__ import unicode_literals

import base64
import numpy
import os
import unittest
import zlib

from tempfile import NamedTemporaryFile
from unittest.mock import patch

import tecplot as tp
from tecplot.tecutil import sv
from tecplot.constant import *
from tecplot.exception import *
from .. import patch_tecutil
from tecplot.tecutil import ArgList

from test import skip_on
from ..sample_data import sample_data_file


class TestSaveTecplot(unittest.TestCase):

    def setUp(self):
        self.datafiles = [
            sample_data_file('10x10x10_anno'),
            sample_data_file('4zones')]

    def tearDown(self):
        for f in self.datafiles:
            os.remove(f)

    def _test_save(self, tecutil_save):
        tp.new_layout()
        ds = tp.data.load_tecplot(self.datafiles[1])
        x = ds.zone(0).values('X').as_numpy_array()
        with NamedTemporaryFile(suffix='.plt', delete=False) as file_out:
            file_out.close()
            tecutil_save(file_out.name)
            tp.new_layout()
            ds = tp.data.load_tecplot(file_out.name)
            xcopy = ds.zone(0).values('X').as_numpy_array()
            self.assertTrue(numpy.allclose(x, xcopy))
            os.remove(file_out.name)

    def _test_save_non_active_frame(self, tecutil_save):
        tp.new_layout()
        ds = tp.data.load_tecplot(self.datafiles[0])
        ds_desc = str(ds)
        tp.active_page().add_frame()
        ds2 = tp.data.load_tecplot(self.datafiles[1])
        with self.assertRaises(TecplotValueError):
            tp.data.save_tecplot_plt('', frame=ds2.frame, dataset=ds)
        with NamedTemporaryFile(suffix='.plt', delete=False) as file_out:
            file_out.close()
            self.assertFalse(ds.frame.active)
            tecutil_save(file_out.name, frame=ds.frame)
            tp.new_layout()
            ds = tp.data.load_tecplot(file_out.name)
            self.assertEqual(ds_desc, str(ds))
            os.remove(file_out.name)

    def _test_save_partial_zones(self, tecutil_save):
        tp.new_layout()
        ds = tp.data.load_tecplot(self.datafiles[1])
        self.assertNotEqual(ds.num_zones, 2)
        with NamedTemporaryFile(suffix='.plt', delete=False) as file_out:
            file_out.close()
            tecutil_save(file_out.name, zones=ds.zones('Rect*'))
            tp.new_layout()
            ds = tp.data.load_tecplot(file_out.name)
            self.assertEqual(ds.num_zones, 2)
            os.remove(file_out.name)

    def _test_save_partial_one_zone(self, tecutil_save):
        tp.new_layout()
        ds = tp.data.load_tecplot(self.datafiles[1])
        self.assertNotEqual(ds.num_zones, 1)
        with NamedTemporaryFile(suffix='.plt', delete=False) as file_out:
            file_out.close()
            tecutil_save(file_out.name, zones=ds.zone('Rect*3D'))
            tp.new_layout()
            ds = tp.data.load_tecplot(file_out.name)
            self.assertEqual(ds.num_zones, 1)
            os.remove(file_out.name)

    def _test_save_partial_variables(self, tecutil_save):
        tp.new_layout()
        ds = tp.data.load_tecplot(self.datafiles[1])
        self.assertNotEqual(ds.num_variables, 2)
        with NamedTemporaryFile(suffix='.plt', delete=False) as file_out:
            file_out.close()
            variable_list = [ds.variable(v) for v in ['X', 'Y']]
            tecutil_save(file_out.name, dataset=ds, variables=variable_list)
            tp.new_layout()
            ds = tp.data.load_tecplot(file_out.name)
            self.assertEqual(ds.num_variables, 2)
            os.remove(file_out.name)

    def _test_save_include_non_data(self, tecutil_save):
        tp.new_layout()
        tp.data.load_tecplot(self.datafiles[0])
        with NamedTemporaryFile(suffix='.plt', delete=False) as file_out:
            file_out.close()
            with self.assertRaises((TecplotLogicError, TecplotSystemError)):
                # nothing to write out
                tecutil_save(file_out.name, include_text=False,
                             include_geom=False, include_data=False)
            # save only text and geom (no data)
            tecutil_save(file_out.name, include_text=True, include_geom=True,
                         include_data=False)
            tp.new_layout()
            ds = tp.data.load_tecplot(file_out.name)
            self.assertEqual(ds.num_variables, 0)
            self.assertEqual(ds.num_zones, 0)
            os.remove(file_out.name)

    def _test_save_all_includes(self, tecutil_save):
        tp.new_layout()
        tp.data.load_tecplot(self.datafiles[0])
        with NamedTemporaryFile(suffix='.plt', delete=False) as file_out:
            file_out.close()
            with self.assertRaises((TecplotLogicError, TecplotSystemError)):
                # nothing to write out
                tecutil_save(file_out.name, include_text=False,
                             include_geom=False,
                             include_data=False,
                             include_data_share_linkage=True,
                             include_autogen_face_neighbors=True)
            os.remove(file_out.name)

    def _test_invalid_filename(self, tecutil_save):
        with self.assertRaises((TecplotTypeError, TecplotLogicError,
                                TecplotSystemError)):
            tecutil_save(2)

    def test_invalid_binary_version(self):
        with self.assertRaises((TecplotTypeError, TecplotLogicError,
                                TecplotSystemError)):
            tp.data.save_tecplot_plt(filename='test', version=2.3)

    @skip_on(TecplotOutOfDateEngineError)
    def test_save_tecplot(self):
        for tecutil_save in [tp.data.save_tecplot_ascii,
                             tp.data.save_tecplot_plt]:
            for test in [self._test_save,
                         self._test_save_non_active_frame,
                         self._test_save_all_includes,
                         self._test_save_include_non_data,
                         self._test_save_partial_one_zone,
                         self._test_save_partial_variables,
                         self._test_invalid_filename,
                         ]:
                test(tecutil_save)

    @skip_on(TecplotOutOfDateEngineError)
    def test_save_binary_versioned(self):
        tp.new_layout()
        ds = tp.data.load_tecplot(self.datafiles[0])
        ds_desc = str(ds)
        with NamedTemporaryFile(suffix='.plt', delete=False) as file_out:
            file_out.close()
            self.assertEqual(ds.frame.dataset.uid, ds.uid)
            self.assertEqual(ds, ds.frame.dataset)
            tp.data.save_tecplot_plt(file_out.name, frame=ds.frame,
                                        dataset=ds,
                                        version=BinaryFileVersion.Tecplot2006)
            tp.new_layout()
            ds = tp.data.load_tecplot(file_out.name)
            self.assertEqual(ds_desc, str(ds))
            os.remove(file_out.name)

    def test_default_options(self):
        # noinspection PyStatementEffect
        def fake_save_tecplot(arglist):
            for option in [sv.ZONELIST, sv.VARLIST,
                           sv.INCLUDETEXT, sv.INCLUDEGEOM,
                           sv.INCLUDEDATA, sv.INCLUDEDATASHARELINKAGE,
                           sv.INCLUDEAUTOGENFACENEIGHBORS, sv.USEPOINTFORMAT,
                           sv.ASSOCIATELAYOUTWITHDATAFILE]:
                with self.assertRaises(TypeError):
                    # Accessing the option should raise a TypeError
                    # since that option should not exist in the incoming
                    # arglist.
                    arglist[option]
            return True

        with patch_tecutil('DataSetWriteX', side_effect=fake_save_tecplot):
            tp.data.save_tecplot_plt('filename')
            tp.data.save_tecplot_ascii('filename')

    def test_common_arglist_options(self):
        tp.new_layout()
        filename = 'the filename'
        dataset = tp.data.load_tecplot(self.datafiles[1])
        zones = list(dataset.zones())
        variables = list(dataset.variables())
        include_text = True
        include_geom = True
        include_data = True
        include_data_share_linkage = True
        include_autogen_face_neighbors = True

        def fake_save_tecplot(arglist):
            self.assertIsInstance(arglist, ArgList)
            self.assertEqual(arglist[sv.FNAME], filename)
            self.assertListEqual([Z.index for Z in zones],
                                 list(arglist[sv.ZONELIST]))
            self.assertListEqual([V.index for V in variables],
                                 list(arglist[sv.VARLIST]))
            self.assertTrue(arglist[sv.INCLUDETEXT])
            self.assertTrue(arglist[sv.INCLUDEGEOM])
            self.assertTrue(arglist[sv.INCLUDEDATASHARELINKAGE])
            self.assertTrue(arglist[sv.INCLUDEAUTOGENFACENEIGHBORS])

            return True

        with patch_tecutil('DataSetWriteX', side_effect=fake_save_tecplot):
            for tecutil_function in [tp.data.save_tecplot_ascii,
                                     tp.data.save_tecplot_plt]:
                tecutil_function(filename=filename, zones=zones,
                                 dataset=dataset,
                                 variables=variables,
                                 include_text=include_text,
                                 include_geom=include_geom,
                                 include_data=include_data,
                                 include_data_share_linkage=include_data_share_linkage,
                                 include_autogen_face_neighbors=include_autogen_face_neighbors)

    def test_ascii_options(self):
        precision = 3
        use_point_format = True

        def fake_save_tecplot(arglist):
            self.assertEqual(precision, arglist[sv.PRECISION])
            self.assertTrue(use_point_format, arglist[sv.USEPOINTFORMAT])
            return True

        with patch_tecutil('DataSetWriteX', side_effect=fake_save_tecplot):
            tp.data.save_tecplot_ascii('the filename', precision=precision,
                                       use_point_format=use_point_format)

    def test_binary_options(self):
        associate_with_layout = True
        version = BinaryFileVersion.Current

        def fake_save_tecplot(arglist):
            self.assertTrue(sv.ASSOCIATELAYOUTWITHDATAFILE)
            self.assertEqual(version, BinaryFileVersion(
                arglist[sv.TECPLOTVERSIONTOWRITE]))
            return True

        with patch_tecutil('DataSetWriteX', side_effect=fake_save_tecplot):
            tp.data.save_tecplot_plt('the filename',
                                        associate_with_layout=associate_with_layout,
                                        version=version)

    def test_invalid_zones(self):
        if tp.sdk_version_info >= (16, 3, 0, 73356):
            for save_tecplot in (tp.data.save_tecplot_ascii,
                                 tp.data.save_tecplot_plt):
                ds = tp.data.load_tecplot(self.datafiles[1])
                with NamedTemporaryFile(suffix='.plt', delete=False) as file_out:
                    file_out.close()
                    with self.assertRaises((TecplotLogicError, TecplotSystemError)):
                        save_tecplot(file_out.name, zones=set([ds.num_zones + 1]))
                os.remove(file_out.name)

    def test_invalid_variables(self):
        if tp.sdk_version_info >= (16, 3, 0, 73356):
            for save_tecplot in (tp.data.save_tecplot_ascii,
                                 tp.data.save_tecplot_plt):
                ds = tp.data.load_tecplot(self.datafiles[1])
                with NamedTemporaryFile(suffix='.plt', delete=False) as file_out:
                    file_out.close()
                    with self.assertRaises((TecplotLogicError, TecplotSystemError)):
                        save_tecplot(file_out.name,
                                     variables=set([ds.num_variables + 1]))
                os.remove(file_out.name)


class TestSaveTecplotSZL(unittest.TestCase):

    def setUp(self):
        self.datafiles = [
            sample_data_file('10x10x10_anno'),
            sample_data_file('4zones')]

    def tearDown(self):
        tp.new_layout()
        for f in self.datafiles:
            os.remove(f)

    def test_save_szl(self):
        tp.new_layout()
        ds0 = tp.data.load_tecplot(self.datafiles[0])
        fout = NamedTemporaryFile(suffix='.szplt', delete=False)
        try:
            fout.close()
            tp.data.save_tecplot_szl(fout.name)
            tp.active_page().add_frame()
            ds1 = tp.data.load_tecplot_szl(fout.name)
            self.assertEqual(ds0.zone(0).dimensions, ds1.zone(0).dimensions)
        finally:
            tp.new_layout()
            os.remove(fout.name)

    def test_save_szl_dataset(self):
        tp.new_layout()
        ds0 = tp.data.load_tecplot(self.datafiles[0])
        fr0 = tp.active_frame()
        fr1 = tp.active_page().add_frame()
        fout = NamedTemporaryFile(suffix='.szplt', delete=False)
        try:
            fout.close()

            with patch('tecplot.macro.execute_extended_command'):
                tp.data.save_tecplot_szl(fout.name, dataset=ds0)
                tp.data.save_tecplot_szl(fout.name, frame=fr0)

                with self.assertRaises(TecplotValueError):
                    tp.data.save_tecplot_szl(fout.name, dataset=ds0, frame=fr1)

            tp.data.save_tecplot_szl(fout.name, dataset=ds0, frame=fr0)
            ds1 = tp.data.load_tecplot_szl(fout.name)
            self.assertEqual(ds0.zone(0).dimensions, ds1.zone(0).dimensions)
            self.assertEqual(ds1.frame, fr1)
        finally:
            tp.new_layout()
            os.remove(fout.name)


if __name__ == '__main__':
    from .. import main
    main()
