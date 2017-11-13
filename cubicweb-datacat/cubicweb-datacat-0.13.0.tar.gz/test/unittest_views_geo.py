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

"""cubicweb-datacat tests for geo-spatial views."""

import json

from cubicweb.devtools import (
    PostgresApptestConfiguration,
    startpgcluster,
    stoppgcluster,
    testlib,
)
from cubicweb.web import facet as cwfacet

from cubes.datacat.views.geo import (
    ExtentFacet,
    RelationExtentFacet,
)


def setUpModule():
    startpgcluster(__file__)


def tearDownModule():
    stoppgcluster(__file__)


class ExtentFacetTC(testlib.CubicWebTC):
    """Test case for the geographical extent facet."""

    configcls = PostgresApptestConfiguration

    def setup_database(self):
        polygon = (
            u'MULTIPOLYGON(((1 1,5 1,5 5,1 5,1 1),(2 2,2 3,3 3,3 2,2 2)),((6 3,9 2,9 4,6 3)))',
            2154,
        )
        with self.admin_access.cnx() as cnx:
            thing = cnx.create_entity(
                'Thing', title=u'thing',
                polygon=polygon,
            )
            cnx.create_entity(
                'OtherThing', name=u'other',
                thing_related=thing,
                geomcoll=(u'GEOMETRYCOLLECTION (POINT (2 46))', 2154),
            )
            cnx.commit()

    def _new_facet(self, req, facet_cls, initial_rql, mainvar, rtype, role=None, target_attr=None):
        """Return a new facet with the given parameters.

        ``req`` is the web request using the facet.

        The new facet will belong to the ``facet_cls`` class.

        The new facet will be initialized with the ``initial_rql`` RQL query in which ``mainvar`` is
        the main variable, and with ``rtype``, ``role``, and ``target_attr`` class attributes.
        """
        rset = req.cnx.execute(initial_rql)
        rqlst = rset.syntax_tree().copy()
        filtered_variable, baserql = cwfacet.init_facets(rset, rqlst.children[0], mainvar=mainvar)
        facet = facet_cls(req, rset=rset, select=rqlst.children[0],
                          filtered_variable=filtered_variable)
        facet.__regid__ = 'extent_facet'
        facet.rtype = rtype
        if role is not None:
            facet.role = role
        if target_attr is not None:
            facet.target_attr = target_attr
        return facet

    def test_no_widget_if_no_geometry(self):
        with self.admin_access.cnx() as cnx:
            catalog = cnx.create_entity('DataCatalog', title=u'cat')
            cnx.create_entity('Dataset', in_catalog=catalog)
            cnx.commit()
        with self.admin_access.web_request() as req:
            facet = self._new_facet(req,
                                    facet_cls=ExtentFacet,
                                    initial_rql='Location X',
                                    mainvar='X',
                                    rtype='geometry')
            self.assertIsNone(facet.get_widget())
            facet = self._new_facet(req,
                                    facet_cls=RelationExtentFacet,
                                    initial_rql='Dataset X',
                                    mainvar='X',
                                    rtype='locate_datasets',
                                    role='object',
                                    target_attr='geometry')
            self.assertIsNone(facet.get_widget())

    def test_convex_hull_relation(self):
        """Check that widget is displayed with convex hull geospatial data (relation case)."""
        with self.admin_access.web_request() as req:
            # Create facet
            facet = self._new_facet(req,
                                    facet_cls=RelationExtentFacet,
                                    initial_rql='OtherThing X',
                                    mainvar='X',
                                    rtype='thing_related',
                                    role='subject',
                                    target_attr='polygon')
            # Check convex hull
            widget = facet.get_widget()
            rset = widget.rset
            self.assertEqual(rset.rql,
                             u'DISTINCT Any ST_ASGEOJSON(ST_CONVEXHULL(ST_COLLECT(B))) '
                             u'WHERE X is OtherThing, X thing_related A, A polygon B '
                             u'HAVING ST_COLLECT(B) != ""')
            expected = {
                u'type': u'Polygon',
                u'coordinates': [[[1, 1], [1, 5], [5, 5],
                                  [9, 4], [9, 2], [5, 1], [1, 1]]],
            }
            self.assertEqual(len(rset), 1)
            self.assertEqual(json.loads(rset[0][0]), expected)

    def test_convex_hull(self):
        """Check that widget is displayed with convex hull geospatial data (no relation case)."""
        with self.admin_access.web_request() as req:
            # Create facet
            facet = self._new_facet(req,
                                    facet_cls=ExtentFacet,
                                    initial_rql='Thing X',
                                    mainvar='X',
                                    rtype='polygon')
            # Check convex hull
            widget = facet.get_widget()
            rset = widget.rset
            self.assertEqual(rset.rql,
                             u'DISTINCT Any ST_ASGEOJSON(ST_CONVEXHULL(ST_COLLECT(A))) '
                             u'WHERE X is Thing, X polygon A HAVING ST_COLLECT(A) != ""')
            expected = {
                u'type': u'Polygon',
                u'coordinates': [[[1, 1], [1, 5], [5, 5],
                                  [9, 4], [9, 2], [5, 1], [1, 1]]],
            }
            self.assertEqual(len(rset), 1)
            self.assertEqual(json.loads(rset[0][0]), expected)

    def test_rql_restriction_relation(self):
        """Check RQL restriction when a geometry is drawn in the facet (relation case)."""
        with self.admin_access.web_request() as req:
            # Create facet
            facet = self._new_facet(req,
                                    facet_cls=RelationExtentFacet,
                                    initial_rql='OtherThing X',
                                    mainvar='X',
                                    rtype='thing_related',
                                    role='subject',
                                    target_attr='polygon')
            self.assertEqual(facet.select.as_string(), 'DISTINCT Any  WHERE X is OtherThing')
            # Nothing drawn -> no new restriction
            facet.add_rql_restrictions()
            self.assertEqual(facet.select.as_string(), 'DISTINCT Any  WHERE X is OtherThing')
            # Geometry drawn if the facet
            facet._cw.form[facet.__regid__ + 'Input'] = '<geojson_geom_str>'
            facet.add_rql_restrictions()
            self.assertEqual(facet.select.as_string(),
                             u'DISTINCT Any  WHERE X is OtherThing, X thing_related A, '
                             u'A polygon B HAVING ST_INTERSECTS('
                             u'ST_COLLECTIONEXTRACT(ST_GEOMFROMGEOJSON("<geojson_geom_str>"), 3), '
                             u'B) = TRUE')

    def test_rql_restriction(self):
        """Check RQL restriction when a geometry is drawn in the facet (no relation case)."""
        with self.admin_access.web_request() as req:
            # Create facet
            facet = self._new_facet(req,
                                    facet_cls=ExtentFacet,
                                    initial_rql='Thing X',
                                    mainvar='X',
                                    rtype='polygon')
            self.assertEqual(facet.select.as_string(), 'DISTINCT Any  WHERE X is Thing')
            # Nothing drawn -> no new restriction
            facet.add_rql_restrictions()
            self.assertEqual(facet.select.as_string(), 'DISTINCT Any  WHERE X is Thing')
            # Geometry drawn if the facet
            facet._cw.form[facet.__regid__ + 'Input'] = '<geojson_geom_str>'
            facet.add_rql_restrictions()
            self.assertEqual(facet.select.as_string(),
                             u'DISTINCT Any  WHERE X is Thing, X polygon A '
                             u'HAVING ST_INTERSECTS('
                             u'ST_COLLECTIONEXTRACT(ST_GEOMFROMGEOJSON("<geojson_geom_str>"), 3), '
                             u'A) = TRUE')

    def test_rql_restriction_existing_having(self):
        """Check RQL restriction when a geometry is drawn in the facet (existing having clause)."""
        with self.admin_access.web_request() as req:
            # Create facet
            facet = self._new_facet(req,
                                    facet_cls=ExtentFacet,
                                    initial_rql='Thing X WHERE X title T HAVING T = "My Title"',
                                    mainvar='X',
                                    rtype='polygon')
            self.assertEqual(facet.select.as_string(),
                             'DISTINCT Any  WHERE X title T, X is Thing HAVING T = "My Title"')
            # Geometry drawn if the facet
            facet._cw.form[facet.__regid__ + 'Input'] = '<geojson_geom_str>'
            facet.add_rql_restrictions()
            self.assertEqual(facet.select.as_string(),
                             u'DISTINCT Any  WHERE X title T, X is Thing, X polygon A '
                             u'HAVING ST_INTERSECTS('
                             u'ST_COLLECTIONEXTRACT(ST_GEOMFROMGEOJSON("<geojson_geom_str>"), 3), '
                             u'A) = TRUE, T = "My Title"')

    def test_rql_restriction_geometry_collection(self):
        """Check RQL restriction when a geometry is drawn in the facet (geometry collection
        case)."""
        with self.admin_access.web_request() as req:
            # Create facet
            facet = self._new_facet(req,
                                    facet_cls=ExtentFacet,
                                    initial_rql='OtherThing X',
                                    mainvar='X',
                                    rtype='geomcoll')
            self.assertEqual(facet.select.as_string(), 'DISTINCT Any  WHERE X is OtherThing')
            # Geometry drawn if the facet
            facet._cw.form[facet.__regid__ + 'Input'] = '<geojson_geom_str>'
            facet.add_rql_restrictions()
            self.assertEqual(facet.select.as_string(),
                             'DISTINCT Any  WHERE X is OtherThing, X geomcoll A HAVING '
                             '((ST_INTERSECTS('
                             'ST_COLLECTIONEXTRACT(ST_GEOMFROMGEOJSON("<geojson_geom_str>"), 3), '
                             'ST_COLLECTIONEXTRACT(A, 1)) = TRUE) OR '
                             '(ST_INTERSECTS('
                             'ST_COLLECTIONEXTRACT(ST_GEOMFROMGEOJSON("<geojson_geom_str>"), 3), '
                             'ST_COLLECTIONEXTRACT(A, 2)) = TRUE)) OR '
                             '(ST_INTERSECTS('
                             'ST_COLLECTIONEXTRACT(ST_GEOMFROMGEOJSON("<geojson_geom_str>"), 3), '
                             'ST_COLLECTIONEXTRACT(A, 3)) = TRUE)')


if __name__ == '__main__':
    from unittest import main
    main()
