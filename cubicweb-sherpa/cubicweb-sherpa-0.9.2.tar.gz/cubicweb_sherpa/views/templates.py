# -*- coding: utf-8
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
"""sherpa views/templates"""

from cubicweb import NotAnEntity
from cubicweb.utils import UStringIO
from cubicweb.web.views import basetemplates

from . import jinja_render


# Bootstrap configuration.
basetemplates.TheMainTemplate.twbs_container_cls = 'container-fluid'


def render_component(comp):
    stream = UStringIO()
    w = stream.write
    comp.render(w)
    return stream.getvalue()


def _compute_active_path(rset):
    if not rset:
        return None
    try:
        entity = rset.get_entity(0, 0)
    except NotAnEntity:
        return None
    ibreadcrumbs = entity.cw_adapt_to('IBreadCrumbs')
    # recurs = set([-1]) to avoid some view specific calculation
    root = ibreadcrumbs.breadcrumbs(recurs=set([-1]))[0]
    if isinstance(root, tuple):
        if root[0].endswith('sedalib'):
            return 'sedalib'
    elif root.cw_etype in ('ConceptScheme', 'SEDAArchiveTransfer', 'AuthorityRecord'):
        return root.cw_etype.lower()
    return None


class NavigationLink(object):
    def __init__(self, url, label, active):
        self.url = url
        self.label = label
        self.active = active


class SherpaMainTemplate(basetemplates.TheMainTemplate):

    def call(self, view):
        self.set_request_content_type()
        self.write_doctype()
        self.template_header(self.content_type, view=view)
        context = self.template_context(view)
        self.w(jinja_render('maintemplate', **context))

    def template_context(self, view):
        """Return the main-template's context."""
        # boxes
        boxes = [render_component(box) for box in self.get_components(view, context='left')]
        # header
        header_components = [render_component(comp)
                             for comp in self.get_components(view, context='header-right')]
        # application message
        msgcomp = self._cw.vreg['components'].select_or_none(
            'applmessages', self._cw, rset=self.cw_rset)
        application_message = msgcomp.render() if msgcomp else u''
        # navigation links
        navigation_links = []
        active_path = _compute_active_path(self.cw_rset)
        for path, label in [
                ('sedaarchivetransfer', u'Profils SEDA'),
                ('sedalib', u"Unités d'archive"),
                ('authorityrecord', u"Notices d'autorité"),
                ('conceptscheme', u'Vocabulaires'),
        ]:
            active = path == active_path
            link = NavigationLink(self._cw.build_url(path), label, active=active)
            navigation_links.append(link)
        # contextual components
        contextual_components = self._cw.view('contentheader', rset=self.cw_rset, view=view)

        ctx = self.base_context()
        url = self._cw.build_url
        ctx.update({
            'title': view.page_title(),
            'page_content': view.render(),
            'navigation_links': navigation_links,
            'application_message': application_message,
            'contextual_components': contextual_components,
            'header_components': header_components,
            'boxes': boxes,
            'footer': {
                'resources': [
                    {'url': url('schema_seda'),
                     'label': u'Schéma du SEDA 2.0'},
                    {'url': self._cw.data_url('dictionnaire_SEDA2_final.pdf'),
                     'label': 'Dictionnaire des balises'},
                    {'url': url('documentation_fonctionnelle'),
                     'label': 'Documentation fonctionnelle'},
                    {'url': 'https://www.cubicweb.org/project/cubicweb-sherpa',
                     'label': 'Documentation technique'},
                ],
            },
        })
        ctx.update(getattr(view, 'template_context', lambda: {})())

        return ctx

    def base_context(self):
        """Return a basic context using standard cubicweb information."""
        req = self._cw
        return {
            'page_id': 'contentmain',
            '_': req._,
            'user': req.user.login,
            'build_url': req.build_url,
            'data_url': req.datadir_url,
            'current_url': req.relative_path(),
        }


def registration_callback(vreg):
    vreg.register_and_replace(SherpaMainTemplate, basetemplates.TheMainTemplate)
