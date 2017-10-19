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
"""cubicweb-prov views/forms/actions/components for web ui"""

from logilab.mtconverter import xml_escape

from cubicweb.predicates import relation_possible
from cubicweb.web.views import tableview

from cubicweb_prov import views as prov

from . import SubviewsTabView


class LifeCycleTabView(SubviewsTabView):
    """Life-cycle tab for concept and concept scheme."""
    __regid__ = 'saem.lifecycle_tab'
    __select__ = relation_possible('generated', role='object')
    subvids = ('prov.activity-generated',
               'prov.activity-associated-with')


class ActivityGeneratedView(prov.ActivityGeneratedView):
    rql = ('Any E,T,DE,DEF,D,A,U ORDERBY D DESC '
           'WHERE E generated X, E agent A, E associated_with U?, E type T, E start D,'
           '      E description DE, E description_format DEF, X eid %(x)s')


class ActivityAgentColRenderer(tableview.MainEntityColRenderer):

    def render_header(self, w):
        w(self._cw.__('agent'))

    def render_entity(self, w, entity):
        if entity.associated_with:
            w(entity.associated_with[0].view('incontext'))
        elif entity.agent:
            w(xml_escape(entity.agent))
        else:
            w(self.empty_cell_content)

    def entity_sortvalue(self, entity):
        if entity.associated_with:
            return entity.associated_with[0].name()
        elif entity.agent:
            return entity.agent
        else:
            return None


class ActivityGeneratedTable(prov.ActivityGeneratedTable):
    column_renderers = {
        'agent': ActivityAgentColRenderer(),
    }


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__,
                      [ActivityGeneratedView, ActivityGeneratedTable])
    vreg.register_and_replace(ActivityGeneratedView, prov.ActivityGeneratedView)
    vreg.register_and_replace(ActivityGeneratedTable, prov.ActivityGeneratedTable)
