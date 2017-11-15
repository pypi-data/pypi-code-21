# copyright 2015 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""cubicweb-saem-ref RDF views"""

from cubicweb.predicates import adaptable
from cubicweb.web.views import VID_BY_MIMETYPE, rdf


VID_BY_MIMETYPE['application/rdf+xml'] = 'rdf'


class SAEMRDFView(rdf.RDFView):
    """Override cw's rdf view to dispatch to primary.rdf / list.rdf views, as implemented in the
    skos cube.
    """
    __select__ = adaptable('RDFPrimary')

    def call(self):
        vid = 'primary.rdf' if len(self.cw_rset) == 1 else 'list.rdf'
        self.wview(vid, self.cw_rset)


def registration_callback(vreg):
    vreg.register_and_replace(SAEMRDFView, rdf.RDFView)
