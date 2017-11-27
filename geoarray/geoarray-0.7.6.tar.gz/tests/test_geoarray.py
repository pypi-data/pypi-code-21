#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_geoarray
----------------------------------

Tests for the functions of the "GeoArray"-class in the "geoarray" module.
For this purpose the TIFF-file "L8_2bands_extract10x11.tif" and the array of
the TIFF-image "L8_2bands_extract10x11_array.txt" in the directory "../tests/data"
is used. The outputs of the "GeoArray"-class functions are tested against the well
known properties of the test-image.

The tests are divided into a total of two test cases. The order of execution is as
follows:
test case 1 (path) - test case 2 (path) - test case 1 (array) - test case 2 (array).

Note that the tests in the test case "Test_GeoarrayAppliedOnPathArray" and
"Test_GeoarrayFunctions" follow - with a few exceptions - the same order as in the
"GeoArray"-class (but they are executed in alphanumeric order inside the test case).
Functions that depend on each other are tested together.

Program started in Mai 2017.
"""
from __future__ import print_function
from collections import OrderedDict
import dill
import geopandas
import numpy as np
import os
from os import path
import osgeo.osr
from shapely.geometry import Polygon
import time
import unittest
from unittest import TestLoader
import matplotlib
from typing import Iterable
from importlib import util

# Imports regarding the created python module.
from py_tools_ds.geo.vector import geometry
from py_tools_ds.compatibility.python.os import makedirs
matplotlib.use('Template')  # disables matplotlib figure popups
from geoarray import GeoArray, masks, __file__  # noqa E402 module level import not at top of file

__author__ = 'Jessica Palka'

# Path of the tests-directory in the geoarray-package.
tests_path = os.path.abspath(path.join(__file__, "..", ".."))


############################################
# Test case: Test_GeoarrayAppliedOnPathArray
############################################

class Test_GeoarrayAppliedOnPathArray(unittest.TestCase):
    """
    The class "Test_GeoarrayAppliedOnPathArray" tests the basic functions of the
    "GeoArray"-class from which the other functions depend on. The functions that
    are being tested are stated in the docstrings located at the beginning of each
    test. Note that the function set_gdalDataset_meta is tested indirectly by a
    couple of tests in the test case (a notation is applied).

    Since the "GeoArray"-class can be instanced with a file path or with a numpy
    array and the corresponding geoinformation, the tests in this test case will
    be executed two times in a row (the test case is parametrized). The order is
    as follows: In the first/second round the tests will be executed using the
    "GeoArray"-instance created with a file path/numpy array.
    """

    # Expected results concerning the used TIFF-image.
    expected_bandnames = OrderedDict([('B1', 0), ('B2', 1)])
    (R_exp, C_exp, B_exp) = expected_shape = (10, 11, 2)
    expected_result = (3, R_exp, C_exp, B_exp)  # dimensions, rows, columns, bands
    expected_dtype = np.dtype('float32')
    given_geotransform = [365985.0, 30.0, 0.0, 5916615.0, 0.0, -30.0]
    expected_resolution = (30, 30)
    expected_grid = [[365985.0, 366015.0], [5916615.0, 5916585.0]]
    given_pszProj4_string = '+proj=utm +zone=33 +datum=WGS84 +units=m +no_defs'
    expected_epsg = 32633
    given_nodata = -9999.0
    given_bandnames = ['B1', 'B2']

    # Variable for the parametrization of the test case.
    k = 0

    @classmethod
    def setUpClass(cls):
        # First line of the test case output to ease the distinction between the test cases using different
        # instances of the "GeoArray"-class.
        print(' ')
        print("Geoarray instanced with {i}, TEST CASE 1 ('basic functions'):".format(i=('PATH', 'NUMPY ARRAY')[cls.k]))

        # Creating the instances of the "GeoArray"-class.
        if cls.k == 0:
            # Creating the "GeoArray"-instance with a FILE PATH.
            cls.L8_2bands_extract10x11 = os.path.join(tests_path, "tests", "data", "L8_2bands_extract10x11.tif")
            cls.testtiff = GeoArray(cls.L8_2bands_extract10x11)

            # Serialize the "GeoArray"-class to the "../tests/data/output"-directory
            serialized_testtiff_path = os.path.join(tests_path, "tests", "data", "output", "testtiff_path.tmp")
            makedirs(os.path.dirname(serialized_testtiff_path), exist_ok=True)
            with open(serialized_testtiff_path, "wb") as f:
                dill.dump(cls.testtiff, f)

        if cls.k == 1:
            # Loading the TIFF-image array from the "data"-directory.
            array_path = os.path.join(tests_path, "tests", "data", "L8_2bands_extract10x11_array.txt")
            cls.L8_2bands_extract10x11 = np.loadtxt(array_path, 'float32').reshape(10, 11, 2)

            # Change the pszProj4-string in a WKT-string.
            srs = osgeo.osr.SpatialReference()
            srs.ImportFromProj4(cls.given_pszProj4_string)
            cls.given_projection = srs.ExportToWkt()

            # Creating the "GeoArray"-instance with a NUMPY ARRAY.
            # The notdata-value will be set in the test "test_NoDataValueOfTiff".
            cls.testtiff = GeoArray(cls.L8_2bands_extract10x11, geotransform=cls.given_geotransform,
                                    projection=cls.given_projection, bandnames=cls.given_bandnames)

            # Serialize the "GeoArray"-class to the "../tests/data/output"-directory
            serialized_testtiff_array = os.path.join(tests_path, "tests", "data", "output", "testtiff_array.tmp")
            makedirs(os.path.dirname(serialized_testtiff_array))
            with open(serialized_testtiff_array, "wb") as f:
                dill.dump(cls.testtiff, f)

        cls.TiffIsInstanceOfGeoarray(cls)
        cls.ArrOfTiffIsInMemory(cls)

    def TiffIsInstanceOfGeoarray(self):
        """
        Indirect test.
        Testing, whether the object "testtiff" is an instance of the class "GeoArray" or not. If an exception is
        raised for an error, all tests of the test case "Test_GeoarrayAppliedOnTiffPath" will be skipped.
        """

        try:
            assert isinstance(self.testtiff, GeoArray)
        except AssertionError:
            self.skipTest(Test_GeoarrayAppliedOnPathArray,
                          reason="The created object 'testtiff' is not an instance of class 'GeoArray'. "
                                 "All tests of the Test Case 'Test_GeoarrayAppliedOnTiffPath' will be skipped!")

    def ArrOfTiffIsInMemory(self):
        """
        Testing the functions: arr - is_inmem, indirect test with 2 stages.
        Stage 1: Checking, if the argument passed to the "GeoArray"-class is a file path or a numpy.ndarray.
        Stage 2: It is tested, if the arr- and is_inmem-function give the expected output.
        If, for any possibility that was tested, an exception is raised for an error, all tests of the test case
        "Test_GeoarrayAppliedOnTiffPath" will be skipped.
        """

        testtiff_basicfunctions = (self.testtiff.arr, self.testtiff.is_inmem)
        expected_conditions = ((None, False), (True, True))
        equal_arr_L8 = np.array_equal(testtiff_basicfunctions[0], self.L8_2bands_extract10x11)

        # FILE PATH
        if isinstance(self.L8_2bands_extract10x11, str) and os.path.isfile(self.L8_2bands_extract10x11):
            try:
                assert (testtiff_basicfunctions[0] == expected_conditions[0][0]) and \
                       (testtiff_basicfunctions[1] == expected_conditions[0][1])
            except AssertionError:
                self.skipTest(Test_GeoarrayAppliedOnPathArray,
                              reason="A path is passed to 'GeoArray'. But the output of the functions "
                                     "arr and is_inmem %s do not match as expected %s!"
                                     % (testtiff_basicfunctions, expected_conditions[0]))

        # NUMPY ARRAY
        elif isinstance(self.L8_2bands_extract10x11, np.ndarray):
            try:
                assert (isinstance(testtiff_basicfunctions[0], np.ndarray) == expected_conditions[1][0]) and \
                       equal_arr_L8 and \
                       (testtiff_basicfunctions[1] == expected_conditions[1][1])
            except (AssertionError, AttributeError):
                self.skipTest(Test_GeoarrayAppliedOnPathArray,
                              reason="A numpy.ndarray is passed to 'GeoArray'. But the output of the functions "
                                     "arr and is_inmem do not match the expected output "
                                     "(arr == given array? %s, is_inmem: %s/%s)!"
                                     % (equal_arr_L8,
                                        testtiff_basicfunctions[1], expected_conditions[1][1]))

        else:
            self.skipTest(Test_GeoarrayAppliedOnPathArray,
                          reason="The variable committed to the 'GeoArray'-class is neither a path nor a numpy.ndarray."
                                 "All tests of the Test Case 'Test_GeoarrayAppliedOnTiffPath' will be skipped!")

    def test_bandnames(self):
        """
        Testing the function: bandnames.
        Test, if the default (for k=0) and set (for k=1) band names respectively were correctly assigned.
        """
        self.assertEqual(self.testtiff.bandnames, self.expected_bandnames,
                         msg="The bandnames of the Tiff-file are different than ['B1', 'B2'] (format: OrderedDict)")

    def test_shape(self):
        """
        Testing the functions: shape - ndim - rows - columns - bands,
        indirect testing of the function: set_gdalDataset_meta(!),
        test with 2 stages.
        Stage 1: Comparing the shape of the testtiff-image with the output of the shape-function.
                    When identical, induction of stage 2...
        Stage 2: Comparing the output of the ndim-, rows-, columns- and bands-function with the expected results.
        If the the shape of the image is not as expected (Stage 1), the whole test will be skipped.
        """

        testtiff_shapefunctions = (self.testtiff.ndim, self.testtiff.rows, self.testtiff.columns, self.testtiff.bands)
        shape_property = ('DIMENSIONS', 'ROWS', 'COLUMNS', 'BANDS')

        if self.testtiff.shape == self.expected_shape:
            for i in range(0, 4, 1):
                with self.subTest(i=i):
                    self.assertEqual(testtiff_shapefunctions[i], self.expected_result[i],
                                     msg='The number of {i} is different from the expected result!'.format(
                                         i=shape_property[i]))

        else:
            self.skipTest("The shape of the array behind the 'Geoarray'-object is not as expected! "
                          "The test 'test_ShapeOfTiffArray' will be skipped.")

    def test_dtype(self):
        """
        Testing the function: dtype,
        indirect testing of the function: set_gdalDataset_meta(!).
        Test, if the data type of the .ndarray behind the "GeoArray"-class was correctly assigned.
        """

        self.assertEqual(self.testtiff.dtype, self.expected_dtype,
                         msg='The dtype of the corresponding array is not as expected!')

    def test_geotransform(self):
        """
        Testing the functions: geotransform - xgsd - ygsd - xygrid_specs,
        indirect testing of the function: set_gdalDataset_meta(!),
        test with 3 stages.
        Stage 1: Comparing the geotransform-tupel of the geotransform-function with the expected result.
                    When identical, induction of stage 2...
        Stage 2: Comparing the resolution from the geotransform-tupel with the expected resolution.
                    When identical, induction of stage 3...
        Stage 3: Comparing the x/y coordinate grid by the xygrid_specs-function with the expected result.
        If an exception is raised as an error in stage 1 or 2, the test will be skipped.
        """

        testtiff_resolutionfunctions = (self.testtiff.xgsd, self.testtiff.ygsd)

        if self.testtiff.geotransform == self.given_geotransform:
            if testtiff_resolutionfunctions == self.expected_resolution:
                self.assertEqual(self.testtiff.xygrid_specs, self.expected_grid,
                                 msg='The [[xOrigin, xGSD], [yOrigin, yGSD]]-grid is not as expected!')

            else:
                self.skipTest("The x/y-resolution %s of the grid of the tested Tiff-file is not as expected %s! "
                              "The function 'XYGRID_SPECS' will not be tested."
                              % (testtiff_resolutionfunctions, self.expected_resolution))
        else:
            self.skipTest("The geotransform-tuple of the array behind the 'GeoArray'-object is not as expected! "
                          "The test 'test_GeotransformTiff' will be skipped.")

    def test_projection(self):
        """
        Testing the functions: projection - epsg,
        indirect testing of the function: set_gdalDataset_meta(!),
        test with 2 stages.
        Stage 1: After translating the projection-string provided by the projection-function to a pszProj4-string,
                    it is compared to the expected pszProj4-string. When identical, induction of stage 2...
        Stage 2: Comparing the EPSG-code provided by the epsg-function with the expected EPSG-code.
        If the pszProj4-string is not as expected (Stage 1), the whole test will be skipped.
        """

        # Convert WKT-string of the projection to a pszProj4_string
        # Code adapted from source:
        # mgleahy, 21 November 2010, "SpatialNotes". [Online].
        # URL: http://spatialnotes.blogspot.de/2010/11/converting-wkt-projection-info-to-proj4.html
        # [Accessed 23 Mai 2017].
        srs = osgeo.osr.SpatialReference()
        srs.ImportFromWkt(self.testtiff.projection)
        testtiff_pszProj4_string = srs.ExportToProj4()

        if testtiff_pszProj4_string.strip(' /t/n/r') == self.given_pszProj4_string:
            self.assertEqual(self.testtiff.epsg, self.expected_epsg,
                             msg="The EPSG-code returned by the 'GeoArray' epsg-function (%s) is not "
                                 "equal to the expected code (%s)." % (self.testtiff.epsg, self.expected_epsg))

        else:
            self.skipTest("The projections of the 'GeoArray'-object is not as expected! "
                          "The test 'test_ProjectionTiff' will be skipped.")

    def test_nodata(self):
        """
        Testing the function: nodata,
        indirect testing of the functions: find_noDataVal(), set_gdalDataset_meta(!).
        Test, if the set/default nodata value of the GeoArray-instance was correctly assigned.
        """

        if self.k == 1:
            self.assertIsNone(self.testtiff.nodata,
                              msg="The nodata-value of the 'GeoArray'-object instanced with a numpy.array and without "
                                  "declaring a nodata-value is not automatically set to 'None'! "
                                  "The remaining assertion in the test 'test_NoDataValueOfTiff' will not be executed.")
            self.testtiff.nodata = self.given_nodata

        self.assertEqual(self.testtiff.nodata, self.given_nodata,
                         msg="The nodata-value of the tested Tiff-file (%s) is not as expected (%s)!"
                             % (self.testtiff.nodata, self.given_nodata))

    def test___getitem__(self):
        def validate(array, exp_shape):
            self.assertIsInstance(array, np.ndarray)
            self.assertEqual(array.shape, exp_shape)

        R, C, B = self.testtiff.shape  # (10, 11, 2)

        # test full array
        validate(self.testtiff[:], (R, C, B))

        # test row/col subset
        validate(self.testtiff[2:5, :3], (3, 3, B))  # third dimension is not given
        validate(self.testtiff[2:5, :3, :], (3, 3, B))

        # test band subset
        validate(self.testtiff[:, :, 0:1], (R, C, 1))  # band slice  # FIXME returns 3D array
        validate(self.testtiff[1], (R, C))  # only band is given  # FIXME returns 2D
        validate(self.testtiff['B1'], (R, C))  # only bandname is given

        # test wrong inputs
        self.assertRaises(ValueError, self.testtiff.__getitem__, 'B01')

        # TODO: add further tests


###################################
# Test case: Test_GeoarrayFunctions
###################################

class Test_GeoarrayFunctions(unittest.TestCase):
    """
    *** !!!
    Note that the class "Test_GeoarrayFunctions" is NOT complete. Furthermore,
    part of the tests that are contained in this test case are not completely
    independent - some dependencies that can be found in the source code of the
    function that is being tested is not yet considered. A respective comment
    can be found at the beginning of the affected tests in the "TODO"-statement. ***


    The class "Test_GeoarrayFunctions" is the second test case of the
    "test_geoarray"-script and tests the functions of the "GeoArray"-class that are
    not yet tested in the first test case. Since the basic functions on which most
    functions of the "GeoArray"-class depend on were already tested in test case 1,
    the tests of test case 2 can be considered moderately independent from these
    functions. Note that if an error, failure or skip occurs in test case 1, test
    case 2 will not be executed. If test case 1 was successful, test case 2 will be
    executed twice - like test case 1 test case 2 is parametrized. The order of
    execution is as follows:
    After the first test case is executed using the "GeoArray"-instance created
    with a file path, the second test case is executed using the same instance.
    The second execution of the test cases uses the "GeoArray"-instance created
    with a numpy array.
    """
    # TODO: Complete the test case!
    # Variable for the parametrization of the test case (the same variable as in test case 1).
    k = 0

    @classmethod
    def setUpClass(cls):

        # Adaption of the source code from the setUpClass of test case 1 to ease the distinction between
        # the test cases using different instances of the "GeoArray"-class.
        # First line of the test case output.
        print(' ')
        print("Geoarray instanced with {i}, TEST CASE 2 ('functions'):".format(i=('PATH', 'NUMPY ARRAY')[cls.k]))

        # Opening the temporary serialized variables (see setUpClass of test case 1) to re-use in the new test case
        # without the need to inherit the variables from test case 1.
        if cls.k == 0:
            with open(os.path.join(tests_path, "tests", "data", "output", "testtiff_path.tmp"), "rb") as f:
                cls.testtiff = dill.load(f)

        if cls.k == 1:
            with open(os.path.join(tests_path, "tests", "data", "output", "testtiff_array.tmp"), "rb") as f:
                cls.testtiff = dill.load(f)

    @classmethod
    def tearDownClass(cls):
        # Removing the "../tests/data/output"-directory with all files. If test case 2 is not executed, the files
        # will be removed at the end of this script in the "if __name__ == '__main__'"-code segment.
        out_dir = os.path.join(tests_path, "tests", "data", "output")

        for file in os.listdir(out_dir):
            os.remove(path.join(out_dir, file))
        os.rmdir(out_dir)

    def test_box(self):
        """
        Testing the function: box.
        Test, if the output of the box-function is an instance boxObj (class, defined in geometry.py, py_tools_ds).
        """

        self.assertIsInstance(self.testtiff.box, geometry.boxObj)

    def test_mask_nodata(self):
        # TODO: Consider the dependency of mask_nodata on the calc_mask_nodata-function.
        """
        Testing the function: mask_nodata.
        Test, if the output of the mask_nodata-function is an instance of "NoDataMask"(class, defined in masks.py).
        """

        self.assertIsInstance(self.testtiff.mask_nodata, masks.NoDataMask)

    def test_mask_baddata(self):
        """
        Testing the function: mask_baddata.
        Test,
        a) if the output of the mask_baddata-function is "None", when the baddata-mask is not set, and
        b) if the output of the mask_baddata-function is an instance of "BadDataMask"(class, defined in masks.py).
        """
        self.L8_BadDataMask10x11 = os.path.join(tests_path, "tests", "data", "L8_BadDataMask10x11.tif")
        bdm = masks.BadDataMask(self.L8_BadDataMask10x11)

        for i in range(0, 2, 1):
            with self.subTest(i=1):
                if i == 0:
                    self.assertIsNone(self.testtiff.mask_baddata)
                if i == 1:
                    self.testtiff.mask_baddata = bdm
                    self.assertIsInstance(self.testtiff.mask_baddata, masks.BadDataMask)

    def test_footprint_poly(self):
        # TODO: Test the validation of the footprint_poly-function.
        # TODO: Consider the dependencies of the footprint_poly-function on mask_nodata, boxObj.
        """
        Testing the function: footprint_poly.
        Test, if the output of the footprint_poly-function is an instance of shapely.geometry.
        """

        self.assertIsInstance(self.testtiff.footprint_poly, Polygon)

    def test_metadata(self):
        # TODO: Create a metadata-file for the tested TIFF-Image.
        # TODO: Test, if the metadata-function gives an output
        """
        Testing the function: metadata.
        Test, if the output of the metadata-function is an instance of GeoDataFrame.
        """

        self.assertIsInstance(self.testtiff.metadata, geopandas.GeoDataFrame)

    def test_tiles(self):
        tiles = self.testtiff.tiles(tilesize=(50, 50))
        self.assertIsInstance(tiles, Iterable)

        for ((rS, rE), (cS, cE)), tile in tiles:
            self.assertTrue(np.array_equal(tile, self.testtiff[rS: rE + 1, cS: cE + 1]))

    def test_get_subset(self):
        # test without resetting band names
        sub_gA = self.testtiff.get_subset(xslice=slice(2, 5), yslice=slice(None, 3), zslice=slice(1, 2))
        self.assertIsInstance(sub_gA, GeoArray)
        self.assertTrue(list(sub_gA.bandnames), list(self.testtiff.bandnames)[1])

        # test without providing zslice
        sub_gA = self.testtiff.get_subset(xslice=slice(2, 5), yslice=slice(None, 3))
        self.assertIsInstance(sub_gA, GeoArray)

        # test with resetting band names
        sub_gA = self.testtiff.get_subset(xslice=slice(2, 5), yslice=slice(None, 3), zslice=slice(1, 2),
                                          reset_bandnames=True)
        self.assertTrue(list(sub_gA.bandnames), ['B1'])

        # test not to return GeoArray
        out = self.testtiff.get_subset(xslice=slice(2, 5), yslice=slice(None, 3), zslice=slice(1, 2),
                                       return_GeoArray=False)
        self.assertIsInstance(out, tuple)
        self.assertTrue(len(out), 3)
        self.assertIsInstance(out[0], np.ndarray)
        self.assertIsInstance(out[1], tuple)
        self.assertIsInstance(out[2], str)

    def test_save(self):
        """
        Testing the function: save,
        test with 2 stages.
        Stage 1: After saving the original TIFF-Image (output format "GTiff") to the "../tests/data/output"-directory
                    with the "save"-function and then instancing the copied TIFF-Image as "GeoArray"-object, it is
                    first tested, if the file exists in the aforementioned directory.
                    When the file exists, induction of stage 2...
        Stage 2: Testing, whether a) the object "testtiff_copy" is an instance of the "GeoArray"-class, and b) if the
                    numpy.array of the copied TIFF-Image is identical to the numpy.array of the original TIFF-Image.
        If the newly created file does not exist in the "../tests/data/output"-directory (Stage 1), the whole test
        will be skipped.
        """

        # Saving the "GeoArray"-instance "testtiff" with the "save"-function of the "GeoArray"-class to the
        # "../tests/data/output"-directory of this repository and instancing it again as a "GeoArray"-object.
        L8_2bands_extract10x11_copy = os.path.join(tests_path, "tests", "data", "output",
                                                   "L8_BadDataMask10x11_copy.tif")
        self.testtiff.save(L8_2bands_extract10x11_copy, fmt="GTiff")
        testtiff_copy = GeoArray(L8_2bands_extract10x11_copy)

        if path.exists(L8_2bands_extract10x11_copy):
            assert isinstance(testtiff_copy, GeoArray) and \
                   np.array_equal(self.testtiff[:], testtiff_copy[:]), \
                   "The copy of the original TIFF-Image, saved by the 'GeoArray' save-function, %s an instance of " \
                   "class 'GeoArray'. Its numpy.array %s identical to the numpy.array of the original TIFF-Image." \
                   % ("IS" if isinstance(testtiff_copy, GeoArray) else "IS NOT",
                      "IS" if np.array_equal(self.testtiff[:], testtiff_copy[:]) else "IS NOT")

        else:
            self.skipTest("The file '%s' does not exists in the directory '%s'. "
                          "The test 'test_SaveTiffToDisk' will be skipped."
                          % (path.basename(L8_2bands_extract10x11_copy), path.dirname(L8_2bands_extract10x11_copy)))

    def test_PlottingFunctions(self):
        # FIXME: This test-function is not yet complete! + TODO: Use other parameters of the plot functions!
        # TODO: Idea: Testing of plot-functions with "from matplotlib.testing.decorators import image_comparison" (?),
        # TODO: example of matplotlib.testing.decorators under:
        # TODO: https://github.com/ketch/griddle/blob/master/tests/plot_tests.py
        self.testtiff.show()
        # self.testtiff.show(interactive=True) # only works if test is started with ipython.

        if util.find_spec('mpl_toolkits.basemap'):
            self.testtiff.show_map()
            self.testtiff.show_map_utm()  # Function still under construction.
        self.testtiff.show_histogram()

        # ----> TODO: Write tests for the remaining functions!


# Parametrizing the test case to run twice.
# Note that 'time.sleep(0.5)' is called several times throughout the following code segment to prevent that the
# standard output of the tests is mixed up with the generated print-commandos.

# Source: renzop, 04 March 2016, "Python Testing how to run parameterised Testcases and pass a parameter to setupClass".
# [Online]. URL: https://stackoverflow.com/questions/35773976/python-testing-how-to-run-parameterised-testcases-and-
#                pass-a-parameter-to-setupc
# [Accessed 30 Mai 2017].
if __name__ == '__main__':
    for k in range(0, 2, 1):
        # Creating a test suite for the first test case
        suite = unittest.TestSuite()
        loader = TestLoader()
        test = None
        test = Test_GeoarrayAppliedOnPathArray
        test.k = k

        tests = loader.loadTestsFromTestCase(test)
        suite.addTest(tests)
        time.sleep(0.5)
        testResult = unittest.TextTestRunner(verbosity=1).run(suite)
        # Source End

        # Extending the display of the test result of test case 1 since the verbosity of the test case output is 1.
        time.sleep(0.5)
        print("Summary:", testResult)
        print("Test successful (errors, failures)? ", testResult.wasSuccessful(),
              " (", len(testResult.errors), ",", len(testResult.failures), ")", sep="")
        if not testResult.skipped:
            print("Test(s) skipped? No")
        else:
            print("Test(s) skipped? Yes")
            for j in range(0, len(testResult.skipped), 1):
                print(j + 1, ".Skipping occurred in: ", testResult.skipped[j][0], sep="")
                print("Reason for ", j + 1, ".skip: ", testResult.skipped[j][1], sep="")

        # If-else loop: Creating and executing the second test suite (created with the tests of the test case 2), only
        # if the first test case was successful and no test was skipped. Otherwise, a note will be printed as output to
        # inform the user that test case 2 was skipped. Additionally, the "../tests/data/output"-directory with files
        # will be removed in the else-statement.
        if testResult.wasSuccessful() and testResult.skipped == []:
            other_suite = unittest.TestSuite()
            more_test = None
            more_test = Test_GeoarrayFunctions
            more_test.k = k

            more_tests = loader.loadTestsFromTestCase(more_test)
            other_suite.addTest(more_tests)
            time.sleep(0.5)
            more_testResult = unittest.TextTestRunner(verbosity=2).run(other_suite)

            # TODO: Extent the output of test case 2 (similar to test case 1) and
            # TODO: Change the verbosity of the TextTestRunner to 1

        else:
            data_dir = os.path.join(tests_path, "tests", "data", "output")
            data_dir_list = os.listdir(data_dir)

            for files in data_dir_list:
                os.remove(path.join(data_dir, files))
            os.rmdir(data_dir)

            print("Test case 2: Since %s error/ %s failure/ %s skip occured in the first test case the second test "
                  "case 'Test_GeoarrayFunctions' will be skipped."
                  % (len(testResult.errors), len(testResult.failures), len(testResult.skipped)))

        time.sleep(0.5)
