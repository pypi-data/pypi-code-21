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

"""cubicweb-datacat tests for geo-spatial entities"""

from cubicweb.devtools import (
    PostgresApptestConfiguration,
    startpgcluster,
    stoppgcluster,
    testlib,
)


def setUpModule():
    startpgcluster(__file__)


def tearDownModule():
    stoppgcluster(__file__)


class IGeoJSONTC(testlib.CubicWebTC):
    """Test case for converting entities to IGeoJSON interface."""

    configcls = PostgresApptestConfiguration

    def test_location_as_geojson(self):
        """Check that locations are correctly converted to IGeoJSON interface."""
        with self.admin_access.repo_cnx() as cnx:
            # No geometry
            loc1 = cnx.create_entity('Location', name=u'Location 1')
            cnx.commit()
            igeojson1 = loc1.cw_adapt_to('IGeoJSON')
            self.assertEqual(igeojson1.as_geojson(), {})
            # With geometry
            loc2 = cnx.create_entity('Location', name=u'Location 2',
                                     geometry=(u'GEOMETRYCOLLECTION (POINT (2 46))', 4326))
            cnx.commit()
            igeojson2 = loc2.cw_adapt_to('IGeoJSON')
            self.assertEqual(igeojson2.as_geojson(),
                             {'type': u'Feature', u'id': loc2.cwuri,
                              'properties': {'name': u'Location 2',
                                             'html_info': u'<strong>Location 2</strong>'},
                              'geometry': {'type': u'GeometryCollection',
                                           'geometries': [{'type': u'Point',
                                                           'coordinates': [2, 46]}]}})

    def test_dataset_as_geojson(self):
        """Check that datasets correctly return a GeoJSON object."""
        with self.admin_access.repo_cnx() as cnx:
            # No related location
            publisher = cnx.create_entity('Agent', name=u'publisher')
            catalog = cnx.create_entity('DataCatalog', title=u'cata',
                                        description=u'catalog',
                                        catalog_publisher=publisher)
            dset = cnx.create_entity('Dataset', title=u'My Dataset',
                                     description=u'desc', in_catalog=catalog)
            cnx.commit()
            self.assertIsNone(dset.cw_adapt_to('IGeoJSON'))
            # One related location with no geometry
            cnx.create_entity('Location', name=u'Location 1', locate_datasets=dset.eid)
            cnx.commit()
            dset.cw_clear_all_caches()
            igeojson = dset.cw_adapt_to('IGeoJSON')
            self.assertEqual(igeojson.as_geojson(), {})
            # One related location with geometry
            loc2 = cnx.create_entity('Location', name=u'Location 2',
                                     geometry=(u'GEOMETRYCOLLECTION (POINT (2 46))', 4326),
                                     locate_datasets=dset.eid)
            cnx.commit()
            igeojson2 = loc2.cw_adapt_to('IGeoJSON')
            self.assertEqual(igeojson.as_geojson(),
                             {'type': 'FeatureCollection', 'features': [igeojson2.as_geojson()]})


if __name__ == '__main__':
    from unittest import main
    main()
