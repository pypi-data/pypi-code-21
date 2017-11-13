# copyright 2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-datacat tests for geoutils module."""

from cubicweb.devtools.testlib import BaseTestCase

from cubes.datacat.geoutils import (
    is_geometry, geometry,
    merge_in_geojson_collection,
    ogr_geom,
    srs_from_epsg,
)


class WorkingWithGeometryTC(BaseTestCase):
    """Test case for working with Geometry data."""

    def test_srs_from_epsg(self):
        """Check that we get a correct ``osr.SpatialReference`` from an EPSG code."""
        srs = srs_from_epsg(4326)
        self.assertEqual(srs.GetAttrValue('AUTHORITY', 0), 'EPSG')
        self.assertEqual(srs.GetAttrValue('AUTHORITY', 1), '4326')
        srs = srs_from_epsg('2154')
        self.assertEqual(srs.GetAttrValue('AUTHORITY', 0), 'EPSG')
        self.assertEqual(srs.GetAttrValue('AUTHORITY', 1), '2154')
        srs = srs_from_epsg(-1)
        self.assertIsNone(srs.GetAttrValue('AUTHORITY', 0))
        self.assertIsNone(srs.GetAttrValue('AUTHORITY', 1))
        with self.assertRaises(ValueError) as cm:
            srs_from_epsg('abcd')
        self.assertIn('Invalid EPSG', str(cm.exception))

    def test_ogr_geom(self):
        """Check that we get correct a ``ogr.Geometry`` from a given value."""
        # (x, y) value
        geom = ogr_geom((2, 46))
        self.assertEqual(geom.ExportToWkt(), 'POINT (2 46)')
        # WKT value
        geom = ogr_geom('POINT (2 46)')
        self.assertEqual(geom.ExportToWkt(), 'POINT (2 46)')
        # GeoJSON value
        geom = ogr_geom('{"type": "Point", "coordinates": [2.0, 46.0]}')
        self.assertEqual(geom.ExportToWkt(), 'POINT (2 46)')
        # Invalid value
        with self.assertRaises(ValueError) as cm:
            ogr_geom('POINT (2, 46)')
        self.assertIn('Invalid value for Geometry', str(cm.exception))

    def test_is_geometry(self):
        """Check that we can determine if geometry value is valid for cubicweb-postgis."""
        # When valid WKT
        self.assertTrue(is_geometry('POINT (2 46)'))
        # When invalid WKT
        self.assertFalse(is_geometry('POINT (2, 46)'))
        # When not WKT
        self.assertFalse(is_geometry('{"type": "Point", "coordinates": [2.0, 46.0]}'))
        # When geom types are the same
        self.assertTrue(is_geometry('POINT (2 46)', expected_geom_type='Point'))
        # When geom types are not the same
        self.assertFalse(is_geometry('POINT (2 46)', expected_geom_type='MultiPoint'))
        # When epsgs are the same
        self.assertTrue(is_geometry('POINT (2 46)', epsg=4326, expected_epsg=4326))
        # When epsgs are not the same
        self.assertFalse(is_geometry('POINT (2 46)', epsg=4326, expected_epsg=2154))
        # When epsg is expected but not given
        self.assertFalse(is_geometry('POINT (2 46)', expected_epsg=4326))
        # When epsg is not integer
        self.assertFalse(is_geometry('POINT (2 46)', epsg='abcd', expected_epsg='abcd'))
        # When invalid geometry (eg. not closed polygon)
        self.assertFalse(is_geometry('POLYGON ((30 10, 40 40, 20 40, 10 20))'))

    def test_convert_geometry(self):
        """Check that we get correct Geometry value from given value."""
        # When value is lat/long
        self.assertEqual(geometry((2, 46)), ('POINT (2 46)', 0))
        # When EPSG is given
        self.assertEqual(geometry((2, 46), epsg=4326), ('POINT (2 46)', 4326))
        # When expected geom type is the same
        value = 'MULTIPOINT (2 46,2.5 45.5)'
        self.assertEqual(geometry(value, expected_geom_type='MultiPoint'), (value, 0))
        # Point -> MultiPoint
        self.assertEqual(geometry('POINT (2.0 46.0)', epsg=4326, expected_geom_type='MultiPoint'),
                         ('MULTIPOINT (2 46)', 4326))
        # LineString -> MultiLineString
        self.assertEqual(geometry('LINESTRING (30 10, 10 30, 40 40)', epsg=4326,
                                  expected_geom_type='MultiLineString'),
                         ('MULTILINESTRING ((30 10,10 30,40 40))', 4326))
        # Polygon -> MultiPolygon
        self.assertEqual(geometry('POLYGON ((30 10, 40 40, 20 40, 10 20, 30 10))', epsg=4326,
                                  expected_geom_type='MultiPolygon'),
                         ('MULTIPOLYGON (((30 10,40 40,20 40,10 20,30 10)))', 4326))
        # -> GeometryCollection
        value = 'POINT (2 46)'
        self.assertEqual(geometry(value, epsg=4326, expected_geom_type='GeometryCollection'),
                         ('GEOMETRYCOLLECTION ({})'.format(value), 4326))
        # Reprojection
        self.assertEqual(geometry('POINT (2 46)', epsg=4326, expected_epsg=2154),
                         ('POINT (622609.119992160820402 6544963.910583730787039)', 2154))
        # Reprojection and type tranformation
        self.assertEqual(geometry('POINT (2 46)', epsg=4326,
                                  expected_geom_type='multipoint', expected_epsg=2154),
                         ('MULTIPOINT (622609.119992160820402 6544963.910583730787039)', 2154))

    def test_cannot_convert_geometry(self):
        """Check that in some cases a ValueError is raised."""
        # When value is invalid WKT
        with self.assertRaises(ValueError) as cm:
            geometry('POINT (2.0, 46.0)')
        self.assertIn('Invalid value for Geometry', str(cm.exception))
        # When geom_types are incompatible
        with self.assertRaises(ValueError) as cm:
            geometry('LINESTRING (2.0 46.0,2.5 45.5)', expected_geom_type='MultiPolygon')
        self.assertIn('Cannot convert LINESTRING', str(cm.exception))
        self.assertIn('to MULTIPOLYGON', str(cm.exception))
        # When invalid epsg
        with self.assertRaises(ValueError) as cm:
            geometry('POINT (2 46)', epsg='abcd')
        self.assertIn('Invalid EPSG', str(cm.exception))
        with self.assertRaises(ValueError) as cm:
            geometry('POINT (2 46)', epsg=2154, expected_epsg='abcd')
        self.assertIn('Invalid EPSG', str(cm.exception))
        # When missing origin epsg
        with self.assertRaises(ValueError) as cm:
            geometry('POINT (2 46)', expected_epsg=2154)
        self.assertIn('Invalid or missing origin EPSG', str(cm.exception))

    def test_convert_geometry_from_geojson(self):
        """Check that we get correct geometry value from GeoJSON."""
        value = '{"type": "Point", "coordinates": [2.0, 46.0]}'
        self.assertEqual(geometry(value, expected_geom_type='MultiPoint'),
                         ('MULTIPOINT (2 46)', 0))
        # Embbed srs
        value = ('{"type": "Point", "coordinates": [2.0, 46.0], '
                 '"crs": {"type": "name", "properties": {"name": "EPSG:4326"}}}')
        self.assertEqual(geometry(value), ('POINT (2 46)', 4326))
        self.assertEqual(geometry(value, expected_geom_type='MultiPoint', expected_epsg=2154),
                         ('MULTIPOINT (622609.119992160820402 6544963.910583730787039)', 2154))


class WorkingWithGeoJSONTC(BaseTestCase):
    """Test case for working with GeoJSON objects."""

    def test_merge_in_geojson_collection(self):
        """Check that merging GeoJSON features return correct feature collection."""
        # One empty object
        geojson = {}
        actual = merge_in_geojson_collection([geojson])
        self.assertEqual(actual, {})
        self.assertIsNot(actual, geojson)
        # One Feature object
        geojson = {'type': u'Feature', 'properties': {'name': u'France'},
                   'geometry': {'type': u'Point', 'coordinates': [2, 46]}}
        expected = {'type': u'FeatureCollection', 'features': [geojson]}
        actual = merge_in_geojson_collection([geojson])
        self.assertEqual(actual, expected)
        # One FeatureCollection object
        geojson = {'type': u'FeatureCollection', 'features': [
            {'type': u'Feature', 'properties': {'name': u'France'},
             'geometry': {'type': u'Point', 'coordinates': [2, 46]}}
        ]}
        actual = merge_in_geojson_collection([geojson])
        self.assertEqual(actual, geojson)
        self.assertIsNot(actual, geojson)
        # Two objects, both empty
        geojson1 = {}
        geojson2 = {}
        actual = merge_in_geojson_collection([geojson1, geojson2])
        self.assertEqual(actual, {})
        self.assertIsNot(actual, geojson1)
        self.assertIsNot(actual, geojson2)
        # Two objects, one empty
        geojson1 = {}
        geojson2 = {'type': u'Feature', 'properties': {'name': u'France'},
                    'geometry': {'type': u'Point', 'coordinates': [2, 46]}}
        expected = {'type': u'FeatureCollection', 'features': [geojson2]}
        actual = merge_in_geojson_collection([geojson1, geojson2])
        self.assertEqual(actual, expected)
        # Two objects, other empty
        geojson1 = {'type': u'Feature', 'properties': {'name': u'France'},
                    'geometry': {'type': u'Point', 'coordinates': [2, 46]}}
        geojson2 = {}
        expected = {'type': u'FeatureCollection', 'features': [geojson1]}
        actual = merge_in_geojson_collection([geojson1, geojson2])
        self.assertEqual(actual, expected)
        # Feature with feature
        geojson1 = {'type': u'Feature', 'properties': {'name': u'France'},
                    'geometry': {'type': u'Point', 'coordinates': [2, 46]}}
        geojson2 = {'type': u'Feature', 'properties': {'name': u'France'},
                    'geometry': {'type': u'Point', 'coordinates': [3, 47]}}
        expected = {'type': u'FeatureCollection', 'features': [geojson1, geojson2]}
        actual = merge_in_geojson_collection([geojson1, geojson2])
        self.assertEqual(actual, expected)
        # FeatureCollection with Feature
        geojson1 = {'type': u'FeatureCollection', 'features': [
            {'type': u'Feature', 'properties': {'name': u'France'},
             'geometry': {'type': u'Point', 'coordinates': [2, 46]}}
        ]}
        geojson2 = {'type': u'Feature', 'properties': {'name': u'France'},
                    'geometry': {'type': u'Point', 'coordinates': [3, 47]}}
        features = geojson1['features']
        expected = {'type': 'FeatureCollection', 'features': features + [geojson2]}
        actual = merge_in_geojson_collection([geojson1, geojson2])
        self.assertEqual(actual['type'], expected['type'])
        self.assertCountEqual(actual['features'], expected['features'])
        # Feature with FeatureCollection
        geojson1 = {'type': u'Feature', 'properties': {'name': u'France'},
                    'geometry': {'type': u'Point', 'coordinates': [2, 46]}}
        geojson2 = {'type': u'FeatureCollection', 'features': [
            {'type': u'Feature', 'properties': {'name': u'France'},
             'geometry': {'type': u'Point', 'coordinates': [3, 47]}}
        ]}
        features = geojson2['features']
        expected = {'type': 'FeatureCollection', 'features': features + [geojson1]}
        actual = merge_in_geojson_collection([geojson1, geojson2])
        self.assertEqual(actual['type'], expected['type'])
        self.assertCountEqual(actual['features'], expected['features'])
        # FeatureCollection with FeatureCollection
        geojson1 = {'type': u'FeatureCollection', 'features': [
            {'type': u'Feature', 'properties': {'name': u'France'},
             'geometry': {'type': u'Point', 'coordinates': [2, 46]}}
        ]}
        geojson2 = {'type': u'FeatureCollection', 'features': [
            {'type': u'Feature', 'properties': {'name': u'France'},
             'geometry': {'type': u'Point', 'coordinates': [3, 47]}}
        ]}
        features1 = geojson1['features']
        features2 = geojson2['features']
        expected = {'type': 'FeatureCollection', 'features': features1 + features2}
        actual = merge_in_geojson_collection([geojson1, geojson2])
        self.assertEqual(actual['type'], expected['type'])
        self.assertCountEqual(actual['features'], expected['features'])


if __name__ == '__main__':
    from unittest import main
    main()
