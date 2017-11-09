#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_map_info
-------------

Tests for `py_tools_ds.geo.map_info` module.
"""

import unittest

from py_tools_ds.geo.map_info import geotransform2mapinfo, mapinfo2geotransform


geotransform_utm = [331185.0, 30.0, -0.0, 5840115.0, -0.0, -30.0]
map_info_utm = ['UTM', 1, 1, 331185.0, 5840115.0, 30.0, 30.0, 33, 'North', 'WGS-84']
geotransform_local = [0, 1, 0, 0, 0, -1]
map_info_local = ['Arbitrary', 1, 1, 0, 0, 1, 1, 0, 'North']

wkt_utm = \
    """
    PROJCS["WGS 84 / UTM zone 33N",
           GEOGCS["WGS 84",
                  DATUM["WGS_1984",
                        SPHEROID["WGS 84", 6378137, 298.257223563,
                                 AUTHORITY["EPSG", "7030"]],
                        AUTHORITY["EPSG", "6326"]],
                  PRIMEM["Greenwich", 0,
                         AUTHORITY["EPSG", "8901"]],
                  UNIT["degree", 0.0174532925199433,
                       AUTHORITY["EPSG", "9122"]],
                  AUTHORITY["EPSG", "4326"]],
           PROJECTION["Transverse_Mercator"],
           PARAMETER["latitude_of_origin", 0],
           PARAMETER["central_meridian", 15],
           PARAMETER["scale_factor", 0.9996],
           PARAMETER["false_easting", 500000],
           PARAMETER["false_northing", 0],
           UNIT["metre", 1,
                AUTHORITY["EPSG", "9001"]],
           AXIS["Easting", EAST],
           AXIS["Northing", NORTH],
           AUTHORITY["EPSG", "32633"]]
    """


class Test_geotransform2mapinfo(unittest.TestCase):

    # TODO implement test in case of geographic prj

    def test_UTM_gt_prj(self):
        map_info = geotransform2mapinfo(gt=geotransform_utm, prj=wkt_utm)
        self.assertTrue(isinstance(map_info, list))
        self.assertEqual(map_info, map_info_utm)

    def test_gt_is_arbitrary_or_none(self):
        # test gt=None
        map_info = geotransform2mapinfo(gt=None, prj=wkt_utm)
        self.assertTrue(isinstance(map_info, list))
        self.assertEqual(map_info, map_info_local)

        # test gt=[0, 1, 0, 0, 0, -1]
        map_info = geotransform2mapinfo(gt=geotransform_local, prj=wkt_utm)
        self.assertTrue(isinstance(map_info, list))
        self.assertEqual(map_info, map_info_local)

    def test_prj_is_empty(self):
        exp_map_info = ['Arbitrary', 1, 1, 331185.0, 5840115.0, 30.0, 30.0, 0, 'North']
        map_info = geotransform2mapinfo(gt=geotransform_utm, prj='')
        self.assertTrue(isinstance(map_info, list))
        self.assertEqual(map_info, exp_map_info)


class Test_mapinfo2geotransform(unittest.TestCase):

    def test_map_info_is_valid(self):
        gt = mapinfo2geotransform(map_info_utm)
        self.assertTrue(isinstance(gt, list))
        self.assertEqual(gt, geotransform_utm)

        # test
        gt = mapinfo2geotransform(['Arbitrary', 1, 1, 5, -7, 1, 1, 0, 'North'])
        self.assertTrue(isinstance(gt, list))
        self.assertEqual(gt, [5, 1, 0, -7, 0, -1])

    def test_map_info_is_empty(self):
        gt = mapinfo2geotransform(None)
        self.assertTrue(isinstance(gt, list))
        self.assertEqual(gt, geotransform_local)
