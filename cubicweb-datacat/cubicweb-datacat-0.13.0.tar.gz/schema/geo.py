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

"""cubicweb-datacat geo-spatial schema definitions"""

from cubicweb import _
from yams.buildobjs import (
    EntityType,
    RelationDefinition,
    String,
)

from cubes.postgis.schema import Geometry


class Location(EntityType):
    """A location is used to locate objects on the Earth's surface"""
    name = String(required=True, fulltextindexed=True,
                  description=_("Name of the location (eg. 'France', 'Boston', "
                                "'President Kennedy bus stop')"))
    geometry = Geometry(
        geom_type='GEOMETRYCOLLECTION', srid=4326, coord_dimension=2,
        description=_('Geospatial indication of the location')
    )


class locate_datasets(RelationDefinition):
    subject = 'Location'
    object = 'Dataset'
    cardinality = '**'
    description = _('relate a location to one or more datasets')
