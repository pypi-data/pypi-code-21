# copyright 2017 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
"""Views related to edition management (dashboard, custom edition forms / display, etc).
"""

from logilab.mtconverter import xml_escape

from cubicweb import tags
from cubicweb.predicates import (authenticated_user, is_instance, non_final_entity,
                                 one_line_rset, relation_possible, score_entity)
from cubicweb.view import EntityView
from cubicweb.web import action, formwidgets
from cubicweb.web.formfields import guess_field
from cubicweb.web.views import actions, management

from cubes.relationwidget.views import RelationFacetWidget
from cubes.skos import views as skos

from . import IndexView


class AuthenticatedIndexView(IndexView):
    __select__ = IndexView.__select__ & authenticated_user()
    template_name = 'index_authenticated'

    def build_context(self):
        context = super(AuthenticatedIndexView, self).build_context()
        for rql, key in [
                ('Any X,XMD,XU,XT ORDERBY XMD DESC WHERE X is SEDAArchiveTransfer, '
                 'X modification_date XMD, X created_by XU?, X title XT, '
                 'X owned_by U, U eid %(u)s', 'profiles'),
                ('Any X,XMD,XU,XUA ORDERBY XMD DESC WHERE X is SEDAArchiveUnit, '
                 'NOT X seda_archive_unit P, '
                 'X modification_date XMD, X created_by XU?, X user_annotation XUA, '
                 'X owned_by U, U eid %(u)s', 'units'),
                ('Any X,XMD,XU ORDERBY XMD DESC WHERE X is AuthorityRecord, '
                 'X modification_date XMD, X created_by XU?,'
                 'X owned_by U, U eid %(u)s', 'records'),
        ]:
            rset = self._cw.execute(rql, {'u': self._cw.user.eid})
            if rset:
                context['my_{}_html'.format(key)] = self._cw.view(
                    'detailed-paginated-list', rset=rset)
        return context


class DetailedPaginatedListView(skos.PaginatedListView):
    __regid__ = 'detailed-paginated-list'

    def call(self, **kwargs):
        super(DetailedPaginatedListView, self).call(subvid='detailed-item')


class DetailedItemView(EntityView):
    __regid__ = 'detailed-item'

    def entity_call(self, entity):
        self.w(tags.a(entity.dc_title(), href=entity.absolute_url()))
        descr = [self._cw._('modified on {}').format(entity.printable_value('modification_date'))]
        if entity.created_by:
            user = entity.created_by[0]
            descr.append(self._cw._('created by {}').format(user.name()))
        self.w(tags.span(', '.join(descr), klass='text-muted'))


class SherpaSecurityManagementView(management.SecurityManagementView):
    """Security view overriden to hide permissions definitions and using a
    RelationFacetWidget to edit owner.
    """
    __select__ = (management.SecurityManagementView.__select__ &
                  relation_possible('owned_by', action='add', strict=True))

    def entity_call(self, entity):
        w = self.w
        w(u'<h1><span class="etype">%s</span> <a href="%s">%s</a></h1>'
          % (entity.dc_type().capitalize(),
             xml_escape(entity.absolute_url()),
             xml_escape(entity.dc_title())))
        w('<h2>%s</h2>' % self._cw.__('Manage security'))
        msg = self._cw.__('ownerships have been changed')
        form = self._cw.vreg['forms'].select(
            'base', self._cw, entity=entity,
            form_renderer_id='base', submitmsg=msg,
            form_buttons=[formwidgets.SubmitButton()],
            domid='ownership%s' % entity.eid,
            __redirectvid='security',
            __redirectpath=entity.rest_path())
        field = guess_field(entity.e_schema,
                            self._cw.vreg.schema['owned_by'],
                            req=self._cw,
                            widget=RelationFacetWidget())
        field.help = None
        form.append_field(field)
        form.render(w=w, display_progress_div=False)


actions.ManagePermissionsAction.__select__ = (
    action.Action.__select__ & one_line_rset() & non_final_entity()
    & (is_instance('ConceptScheme', 'AuthorityRecord', 'SEDAArchiveTransfer')
       | (is_instance('SEDAArchiveUnit')
          & score_entity(lambda x: x.cw_adapt_to('IContained').container is None)))
    & relation_possible('owned_by', action='add', strict=True))


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__)
    vreg.unregister(management.SecurityManagementView)
