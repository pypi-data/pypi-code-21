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
"""cubicweb-saem-ref startup views"""

from contextlib import contextmanager

from cubicweb import tags
from cubicweb.web.views import baseviews, startup, uicfg

from . import add_etype_link, import_etype_link


for etype in ('AgentKind', 'ArchivalRole', 'AgentPlace',
              'AssociationRelation', 'ChronologicalRelation', 'HierarchicalRelation',
              'EACResourceRelation', 'Activity', 'SEDADate'):
    uicfg.indexview_etype_section[etype] = 'subobject'


def view_link(req, *args, **kwargs):
    """Return an HTML link with a "view" icon."""
    return tags.a(u'', href=req.build_url(*args, **kwargs),
                  klass='icon-eye pull-right',
                  title=req._('View'))


@contextmanager
def index_box(w, title_html, panel_class='panel-info'):
    w(u'<div class="{}">'.format('col-md-4' if panel_class == 'panel-info' else ''))
    w(u' <div class="panel {}">'.format(panel_class))
    w(u'  <div class="panel-heading panel-title">{0}</div>'.format(title_html))
    yield
    w(u' </div>')
    w(u'</div>')


class ListGroupView(baseviews.ListView):
    """Same a 'list' view but with a 'list-group' CSS class (for list items in
    particular).
    """
    __regid__ = 'listgroup'

    def call(self, title=None, subvid=None, listid=None, **kwargs):
        return super(ListGroupView, self).call(
            klass='list-group', title=title, subvid=subvid, listid=listid, **kwargs)

    def cell_call(self, row, col=0, vid=None, klass=None, **kwargs):
        self.w(u'<li class="list-group-item">')
        self.wview(self.item_vid, self.cw_rset, row=row, col=col, vid=vid, **kwargs)
        self._view_modification_date(row, col)
        self.w(u'</li>\n')

    def _view_modification_date(self, row, col):
        _ = self._cw._
        entity = self.cw_rset.get_entity(row, col)
        self.w(u'<div class="text-muted">')
        self.w(u'<span>%s</span> ' % _('latest update on'))
        self.w(u'<span class="value">%s</span> '
               % self._cw.format_date(entity.modification_date))
        self.w(u'</div>')


class SAEMRefIndexView(startup.IndexView):
    """Index view for SAEM-Ref"""
    etype_rql = {
        'AuthorityRecord': (
            'Any X,XN,XA,MD ORDERBY MD DESC LIMIT 5 WHERE X is AuthorityRecord, '
            'X modification_date MD, X ark XA, '
            'NE name_entry_for X, NE form_variant "authorized", NE parts XN'),
        'ConceptScheme': (
            'Any X,XT,XA,XD,XDF,MD ORDERBY MD DESC LIMIT 5 WHERE X is ConceptScheme, '
            'X modification_date MD, X title XT, X ark XA, '
            'X description XD, X description_format XDF'),
        'SEDAArchiveTransfer': (
            'Any X,XT,XA,XD,MD ORDERBY MD DESC LIMIT 5 WHERE X is SEDAArchiveTransfer, '
            'X modification_date MD, X title XT, X ark XA, '
            'X user_annotation XD'),
        'Organization': (
            'Any X,XN,XA,MD ORDERBY MD DESC LIMIT 5 WHERE X is Organization, '
            'X modification_date MD, X name XN, X ark XA'),
    }

    def _render_modified_rset(self, rset):
        if rset:
            self.w(tags.div(self._cw._('recently modified entities'),
                            klass='panel-body text-mutted'))
            self._cw.view('listgroup', rset=rset, w=self.w)
        else:
            self.w(tags.div(self._cw._('no entity'),
                            klass='panel-body text-mutted'))

    def render_box(self, etype, import_url=None):
        req = self._cw
        title_html = u'<b>{0}</b>'.format(req.__(etype + '_plural'))
        # `view`, `add`, `import` buttons inserted in reversed order because of 'pull-right'
        if import_url:
            title_html += import_etype_link(req, etype, import_url)
        title_html += add_etype_link(req, etype)
        rset = req.execute(self.etype_rql[etype])
        if rset:
            title_html += view_link(req, etype)
        with index_box(self.w, title_html):
            self._render_modified_rset(rset)

    def render_seda_lib_box(self):
        req = self._cw
        title_html = u'<b>{0}</b>'.format(req._('SEDA components'))
        title_html += add_etype_link(req, 'SEDAArchiveUnit', unit_type='unit_content')
        rset = req.execute(
            'Any X,MD ORDERBY MD DESC LIMIT 5 '
            'WHERE X is SEDAArchiveUnit, X modification_date MD, '
            'NOT X seda_archive_unit P')
        if rset:
            title_html += view_link(req, 'sedalib')
        with index_box(self.w, title_html):
            self._render_modified_rset(rset)

    def entities(self):
        self.w(u'<div class="row">')
        for etype, import_url in [
            ('Organization', None),
            ('AuthorityRecord', self._cw.build_url('view', vid='eac.import')),
            ('ConceptScheme', self._cw.build_url('add/skossource')),
            ('SEDAArchiveTransfer', None),
        ]:
            self.render_box(etype, import_url)
        self.render_seda_lib_box()
        self.w(u'</div>')


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__,
                      butclasses=(SAEMRefIndexView, ))
    vreg.register_and_replace(SAEMRefIndexView, startup.IndexView)
