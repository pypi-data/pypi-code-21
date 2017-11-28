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
# You should have received a copy of the GNU General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

from jinja2 import Environment, PackageLoader, select_autoescape

from cubicweb.view import View
from cubicweb.web.views import urlrewrite, startup, uicfg


_REWRITE_RULES = []
_JINJA_ENV = Environment(loader=PackageLoader('cubicweb_sherpa.views'),
                         autoescape=select_autoescape(enabled_extensions=('html',)))


def jinja_render(template_name, **ctx):
    """Return a string containing result of rendering of Jinja2's `template_name` with
    `ctx` as context.
    """
    template = _JINJA_ENV.get_template(template_name + '.jinja2.html')
    return template.render(**ctx)


class JinjaStaticView(View):
    """Abstract base class to render static pages from a jinja template."""
    __abstract__ = True
    template_name = None
    title = None

    def call(self, **kw):
        self.w(jinja_render(self.template_name, **self.build_context()))

    def build_context(self):
        return {
            'title': self._cw._(self.title),
            'build_url': self._cw.build_url,
            'data_url': self._cw.datadir_url,
        }


def jinja_static_view(template_name, title=None, regid=None, path=None):
    """Generate a sub-class of :class:`JinjaStaticView` parametrized with its `template_name` and
    `title`.

    `__regid__` is built by prepending 'sherpa.' to `template_name` or may be explicitly specified
    using `regid`.

    A path to access to view is automatically generated and will match `template_name` unless
    explicitly specified using `path` argument.
    """
    class_name = template_name.capitalize() + 'View'
    if regid is None:
        regid = 'sherpa.' + template_name

    if path is None:
        path = '/' + template_name
    _REWRITE_RULES.append((path, {'vid': regid}))

    return type(class_name, (JinjaStaticView,), {'__regid__': regid,
                                                 'template_name': template_name,
                                                 'title': title})


IndexView = jinja_static_view('index', 'view_index', regid='index', path='/')
ProjectView = jinja_static_view('project', u'Sherpa un générateur de profils')
UtilisationView = jinja_static_view('utilisation', u'Pour commencer')
SedaView = jinja_static_view('seda', u'Le SEDA')
Seda2SchemaView = jinja_static_view('schema_seda', u'Schéma du SEDA 2')
AProposView = jinja_static_view('apropos', u'À propos')
ContactView = jinja_static_view('contact', 'Contact')
ArchiveUnitView = jinja_static_view('archive_unit', u"Unités d'archive")
ARecordView = jinja_static_view('authority_record', u"Notices d'autorité")


# add our rewrite rules, has to be done once the list if filled because of metaclass magic
class SherpaReqRewriter(urlrewrite.SimpleReqRewriter):
    ignore_baseclass_rules = True
    global _REWRITE_RULES
    rules = tuple(_REWRITE_RULES)
    del _REWRITE_RULES


uicfg.autoform_section.tag_subject_of(('CWUser', 'primary_email', '*'), 'main', 'hidden')


def authority_record_kind_vocabulary(form, field):
    """Vocabulary function for AuthorityRecord.kind skipping "unknown" value."""
    rset = form._cw.execute('Any X, XN WHERE X name XN, X is AgentKind, '
                            'X name != "unknown-agent-kind"')
    return [(entity.dc_title(), str(entity.eid)) for entity in rset.entities()]


uicfg.autoform_field_kwargs.tag_attribute(('AuthorityRecord', 'agent_kind'),
                                          {'choices': authority_record_kind_vocabulary})


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, (IndexView,))
    vreg.register_and_replace(IndexView, startup.IndexView)

    from cubicweb.web.views import actions, bookmark, cwuser
    vreg.unregister(actions.SelectAction)
    vreg.unregister(actions.CancelSelectAction)
    vreg.unregister(actions.ViewAction)
    vreg.unregister(actions.MultipleEditAction)
    vreg.unregister(actions.CopyAction)
    vreg.unregister(actions.AddNewAction)
    vreg.unregister(actions.AddRelatedActions)
    vreg.unregister(actions.ViewSameCWEType)
    vreg.unregister(actions.UserPreferencesAction)
    vreg.unregister(actions.ManageAction)
    vreg.unregister(actions.PoweredByAction)
    vreg.unregister(bookmark.BookmarksBox)
    vreg.unregister(cwuser.UserPreferencesEntityAction)
