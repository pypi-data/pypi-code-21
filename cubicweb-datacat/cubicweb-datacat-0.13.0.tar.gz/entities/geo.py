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

"""cubicweb-datacat geo-spatial entity's classes"""

import json

from rdflib import Literal
from rdflib.namespace import Namespace

from cubicweb.predicates import (
    has_related_entities,
    is_instance,
)
from cubicweb.view import EntityAdapter

from cubes.skos.entities import AbstractRDFAdapter
from cubes.datacat import register_location_rdf_mapping
from cubes.datacat.geoutils import merge_in_geojson_collection
from . import add_literal_to_graph


class GeoJSONLocationAdapter(EntityAdapter):
    """Adapt Location entities to the IGeoJSON interface."""

    __regid__ = 'IGeoJSON'
    __select__ = EntityAdapter.__select__ & is_instance('Location')

    def as_geojson(self):
        """Return a JSON object that is the GeoJSON representation of the location.

        Returned GeoJSON object is a ``Feature`` (or an empty object if the location cannot be
        converted to a valid GeoJSON feature).
        """
        # Compute geometry attribute
        rql = ('Any ST_ASGEOJSON(G) WHERE L geometry G, NOT L geometry NULL, '
               'L eid %(location_eid)s')
        rset = self._cw.execute(rql, {'location_eid': self.entity.eid})
        if not rset:  # A GeoJSON feature must have a geometry attribute
            return {}
        # Compute GeoJSON object
        jsonobj = {
            'type': 'Feature',
            'properties': {
                'name': self.entity.name,
                'html_info': u'<strong>{}</strong>'.format(self.entity.name),
            },
            'geometry': json.loads(rset.rows[0][0]),
        }
        if self.entity.cwuri:  # Optional identifier
            jsonobj['id'] = self.entity.cwuri
        return jsonobj


class GeoJSONDatasetAdapter(EntityAdapter):
    """Adapt Dataset entities to the IGeoJSON interface."""

    __regid__ = 'IGeoJSON'
    __select__ = EntityAdapter.__select__ & has_related_entities('locate_datasets', role='object')

    def as_geojson(self):
        """Return a JSON object that is the GeoJSON representation of the dataset.

        Returned GeoJSON object is a ``FeatureCollection`` (or an empty object if the dataset has
        no related locations).
        """
        # Compute feature list from related locations
        locations = self.entity.related('locate_datasets', role='object', entities=True,
                                        targettypes=('Location',))
        features = (location.cw_adapt_to('IGeoJSON').as_geojson() for location in locations)
        return merge_in_geojson_collection(features)


class LocationRDFAdapter(AbstractRDFAdapter):
    """Adapt Location entities to RDF using DCAT vocabulary."""
    __regid__ = 'RDFPrimary'
    __select__ = AbstractRDFAdapter.__select__ & is_instance('Location')
    register_rdf_mapping = staticmethod(register_location_rdf_mapping)

    def fill(self, graph):
        super(LocationRDFAdapter, self).fill(graph)
        reg = self.registry
        rset = self._cw.execute(
            'Any ST_ASTEXT(G) WHERE X geometry G, NOT X geometry NULL, X eid %(x)s',
            {'x': self.entity.eid},
        )
        if rset:
            wkt = rset[0][0]
            gsp = Namespace('http://www.opengis.net/ont/geosparql#')
            value = Literal(wkt, datatype=gsp.wktLiteral)
            add_literal_to_graph(
                self.entity.cwuri, reg.normalize_uri('locn:geometry'), value,
                graph)
