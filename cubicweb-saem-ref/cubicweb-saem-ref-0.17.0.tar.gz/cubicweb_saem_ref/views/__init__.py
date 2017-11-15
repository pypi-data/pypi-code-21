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
"""cubicweb-saem-ref views/forms/actions/components for web ui"""

from functools import wraps

from logilab.common.decorators import monkeypatch
from logilab.mtconverter import xml_escape
from logilab.common.registry import yes

from cubicweb import _
from cubicweb import NoSelectableObject, neg_role, tags
from cubicweb.utils import json_dumps, js_href
from cubicweb.uilib import domid, js
from cubicweb.view import EntityView
from cubicweb.predicates import (has_permission, is_instance, multi_lines_rset, match_kwargs,
                                 partial_has_related_entities)
from cubicweb.web import component, formwidgets as fw
from cubicweb.web.views import basecomponents, uicfg, urlrewrite, tabs, primary

from cubes.squareui.views.basetemplates import basetemplates
from cubicweb_seda.views import dropdown_button, has_rel_perm, widgets as sedawidgets

from .. import cwuri_url


pvs = uicfg.primaryview_section
afs = uicfg.autoform_section
abaa = uicfg.actionbox_appearsin_addmenu
affk = uicfg.autoform_field_kwargs

pvs.tag_subject_of(('*', 'ark_naa', '*'), 'attributes')
afs.tag_subject_of(('*', 'ark_naa', '*'), 'main', 'attributes')
afs.tag_subject_of(('*', 'custom_workflow', '*'), 'main', 'hidden')
afs.tag_subject_of(('*', 'primary_email', '*'), 'main', 'hidden')

abaa.tag_object_of(('*', 'for_user', '*'), False)  # do not expose CWProperties mecanism
abaa.tag_subject_of(('*', 'use_email', '*'), False)
abaa.tag_subject_of(('*', 'phone_number', '*'), False)

affk.set_field_kwargs('*', 'ark', widget=fw.TextInput({'size': 80}), required=False)


def external_link(text, href):
    """Return an HTML link with an icon indicating that the URL is external.
    """
    icon = tags.span(klass="glyphicon glyphicon-share-alt")
    return tags.a(u' '.join([text, icon]), href=href, escapecontent=False)


def add_etype_link(req, etype, text=u'', klass='icon-plus-circled pull-right',
                   **urlparams):
    """Return an HTML link to add an entity of type 'etype'."""
    vreg = req.vreg
    eschema = vreg.schema.eschema(etype)
    if eschema.has_perm(req, 'add'):
        url = vreg['etypes'].etype_class(etype).cw_create_url(req, **urlparams)
        return tags.a(text, href=url, klass=klass,
                      title=req.__('New %s' % etype))
    return u''


def import_etype_link(req, etype, url):
    """Return an HTML link to the view that may be used to import an entity of type `etype`.
    """
    eschema = req.vreg.schema.eschema(etype)
    if eschema.has_perm(req, 'add'):
        return tags.a(u'', href=url, klass='icon-upload pull-right',
                      title=req.__('Import %s' % etype))
    return u''


def add_relations_button(req, entity, msg, *relations_info, **extraurlparams):
    """Return an HTML dropdown button to add relations with `entity` as object"""
    links = [relation_link(req, entity, relation_info, **extraurlparams)
             for relation_info in relations_info]
    links = [l for l in links if l]
    if links:
        # No links if user cannot add any relation.
        return dropdown_button(req._(msg), links)


def relation_link(req, entity, relation_info, **extraurlparams):
    """Return a HTML link to add a `rtype` relation to `entity`"""
    rtype, role, target_etype, label = relation_info
    rschema = req.vreg.schema[rtype]
    targets = rschema.targets(role=role)
    if target_etype is not None:
        for target in targets:
            etype = target.type
            if etype == target_etype:
                break
        else:
            raise AssertionError('{0} not found in targets of {1}'.format(
                target_etype, rschema))
    else:
        assert len(targets) == 1, \
            'expecting a single {0} for relation {1}'.format(role, rschema)
        etype = targets[0].type
    if not has_rel_perm('add', entity, rtype, role, target_etype=etype):
        return u''
    linkto = '{rtype}:{eid}:{role}'.format(rtype=rtype, eid=entity.eid, role=neg_role(role))
    urlparams = {'__linkto': linkto,
                 '__redirectpath': entity.rest_path()}
    urlparams.update(extraurlparams)
    if label is None:
        label = etype
    return add_etype_link(req, etype, text=req._(label).lower(),
                          klass='', **urlparams)


def editlinks(icon_info):
    """Decorator for `entity_call` to add "edit" links."""
    def decorator(entity_call):
        @wraps(entity_call)
        def wrapper(self, entity, **kwargs):
            editurlparams = {
                '__redirectpath': kwargs.pop('__redirectpath',
                                             entity.rest_path()),
            }
            if 'tabid' in kwargs:
                editurlparams['__redirectparams'] = 'tab=' + kwargs.pop('tabid')
            html_icons = entity.view('saem.edit-link',
                                     icon_info=icon_info,
                                     editurlparams=editurlparams)
            if html_icons:
                self.w(tags.div(html_icons, klass='pull-right'))
            return entity_call(self, entity, **kwargs)
        return wrapper
    return decorator


class ExternalLinkView(EntityView):
    """Render an entity as an external link according to `rtype` keyword
    argument or automatically if it is an ExternalUri.
    """

    __regid__ = 'saem.external_link'
    __select__ = EntityView.__select__ & (
        is_instance('ExternalUri') | match_kwargs('rtype'))

    def entity_call(self, entity, rtype=None):
        if rtype is None:
            rtype = 'uri'  # ExternalUri
        href = text = getattr(entity, rtype)
        self.w(external_link(text, href))


def configure_relation_widget(req, div, search_url, title, multiple, validate):
    """Build a javascript link to invoke a relation widget

    Widget will be linked to div `div`, with a title `title`. It will display selectable entities
    matching url `search_url`. bool `multiple` indicates whether several entities can be selected or
    just one, `validate` identifies the javascript callback that must be used to validate the
    selection.
    """
    req.add_js('cubes.saem_ref.js')
    return sedawidgets.configure_relation_widget(req, div, search_url, title, multiple, validate)


class AddEntityComponent(component.CtxComponent):
    """Component with 'add' link to be displayed in 'same etype' views usually 'SameETypeListView'.
    """
    __regid__ = 'saem.add_entity'
    __select__ = (component.CtxComponent.__select__ & multi_lines_rset() & has_permission('add') &
                  is_instance('AuthorityRecord', 'ConceptScheme',
                              'SEDAArchiveTransfer', 'SEDAArchiveUnit'))
    context = 'navtop'
    extra_kwargs = {'SEDAArchiveUnit': {'unit_type': 'unit_content'}}

    def render_body(self, w):
        etype = self.cw_rset.description[0][0]
        w(add_etype_link(self._cw, etype, **self.extra_kwargs.get(etype, {})))


class ImportEntityComponent(component.CtxComponent):
    """Component with 'import' link to be displayed in 'same etype' views usually
    'SameETypeListView'.

    Concret class should fill the `import_vid` class attribute and add a proper `is_instance`
    selector.
    """
    __abstract__ = True
    __regid__ = 'saem.import_entity'
    __select__ = component.CtxComponent.__select__ & multi_lines_rset() & has_permission('add')
    import_url = None  # URL of the view that may be used to import data
    context = 'navtop'

    def render_body(self, w):
        etype = self.cw_rset.description[0][0]
        w(import_etype_link(self._cw, etype, self.import_url))


# Bootstrap configuration.
basetemplates.TheMainTemplate.twbs_container_cls = 'container'


# Wrap breadcrumbs items within a "container" div.
@monkeypatch(basetemplates.HTMLPageHeader)
def breadcrumbs(self, view):
    components = self.get_components(view, context='header-center')
    if components:
        self.w(u'<nav role="navigation" class="cw-breadcrumb">')
        for comp in components:
            self.w(u'<div class="%s">' % basetemplates.TheMainTemplate.twbs_container_cls)
            comp.render(w=self.w)
            self.w(u'</div>')
        self.w(u'</nav>')


# Display header-right components in a specific div, not using 'nav' bootstrap style and handle an
# 'active' class in the nav component (main-navigation)
@monkeypatch(basetemplates.HTMLPageHeader)
def main_header(self, view):
    w = self.w
    w(u'<nav class="navbar navbar-default" role="banner">')
    w(u'<div class="container">')
    w(u'<div class="pull-right dropdown">')
    components = self.get_components(view, context='header-right')
    for comp in components:
        comp.render(w=w)
    w(u'</div>')
    self.display_navbar_header(w, view)
    w(u'<div id="tools-group" class="collapse navbar-collapse">')
    components = self.get_components(view, context='main-navigation')
    if components:
        w(u'<ul class="nav navbar-nav navbar-left">')
        for comp in components:
            if getattr(comp, 'active', False):
                w(u'<li class="active">')
            else:
                w(u'<li>')
            comp.render(w=w)
            w(u'</li>')
        w(u'</ul>')
    w(u'</div></div></nav>')


class MainNavigationMenuComponent(basecomponents.HeaderComponent):
    __abstract__ = True
    __select__ = yes()
    context = 'main-navigation'
    path = label = None

    @property
    def active(self):
        return self._cw.relative_path().lower() == self.path

    def render(self, w, **kwargs):
        self._cw.add_css('cubes.saem_ref.css')
        w(tags.a(self._cw._(self.label), href=self._cw.build_url(self.path)))


def main_navigation_menu():
    """Yield navigation component instance to fill the navigation menu"""
    for order, (path, label) in enumerate([
        ('Organization', _('Organization_plural_short')),
        ('AuthorityRecord', 'AuthorityRecord_plural'),
        ('ConceptScheme', _('Vocabularies')),
        ('SEDAArchiveTransfer', 'SEDAArchiveTransfer_plural'),
        ('sedalib', _('SEDA components')),
    ]):
        yield type(path + 'NavMenuEntryComponent', (MainNavigationMenuComponent,), {
            '__regid__': 'saem.navmenu_' + path.lower(),
            'path': path.lower(),
            'label': label,
            'order': order,
        })


class SAEMHTMLPageFooter(basetemplates.HTMLPageFooter):
    def footer_content(self):
        self.w(u'''<p>
  <a href="http://www.gironde.fr" target="_blank"><img src="{logo_cd33}" /></a>
  <a href="http://www.bordeaux-metropole.fr" target="_blank"><img src="{logo_metro}" /></a>
  <a href="http://www.bordeaux.fr" target="_blank"><img src="{logo_mairie}" /></a>
</p>'''.format(logo_cd33=self._cw.data_url('cd33.jpg'),
               logo_metro=self._cw.data_url('bx_metro.jpg'),
               logo_mairie=self._cw.data_url('mairie_bx.jpg')))


class RelatedEntitiesListView(EntityView):
    """Abstract entity view for displaying an related entities in a list.

    This view should be called with a ``subvid`` parameter indicating the ``regid`` of the view
    to be used for each related entity.
    """

    __abstract__ = True
    __select__ = EntityView.__select__ & partial_has_related_entities()
    rtype = None
    role = 'object'
    subvid = 'saem.listitem'
    target_etype = None
    subvid_kwargs = None

    @property
    def title(self):
        return self.rtype + '_object' if self.role == 'object' else self.rtype

    def entity_call(self, entity, **kwargs):
        kwargs.update(self.subvid_kwargs or {})
        kwargs['__redirectpath'] = entity.rest_path()
        if self.target_etype is not None:
            targettypes = (self.target_etype, )
        else:
            targettypes = None
        rset = entity.related(self.rtype, role=self.role,
                              targettypes=targettypes)
        if self.title:
            self.w(tags.h2(self._cw._(self.title)))
        if len(rset) == 1:
            self._cw.view(self.subvid, rset=rset, w=self.w, **kwargs)
        else:
            # assign divid to self for reuse in page_navigation_url below
            self.divid = u'{}{}'.format(domid(self.__regid__), entity.eid)
            self.w(u'<div id="{}">'.format(self.divid))
            self.do_paginate(rset=rset)
            self._cw.view('list', rset=rset, w=self.w, subvid=self.subvid, **kwargs)
            self.w(u'</div>')

    def page_navigation_url(self, navcomp, _path, params):
        divid = params['divid'] = self.divid
        # we don't want vid from _cw.form which target the parent tab
        params['vid'] = self.__regid__
        # generate rql instead of using cw_rset.printable_rql since it's usually an ambiguous query
        # using ARK identifier
        params['rql'] = 'Any X WHERE X eid {}'.format(self.cw_rset.one().eid)
        return js_href("$(%s).loadxhtml(AJAX_PREFIX_URL, %s, 'get', 'swap')" % (
            json_dumps('#' + divid), js.ajaxFuncArgs('view', params)))


class RelationInfo(tuple):

    def __new__(cls, rtype, role, targets=None, label=None):
        return tuple.__new__(cls, (rtype, role, targets, label))


class SubviewsTabView(tabs.TabsMixin, EntityView):
    """Abstract tab view rendering views listed in `subvids` attribute."""
    __abstract__ = True
    subvids = ()  # List sub vids to be displayed in this tab.
    relations_info = ()

    def entity_call(self, entity):
        if self.relations_info:
            relations_info = [RelationInfo(*rinfo) for rinfo in self.relations_info]
            urlparams = {'__redirectparams': 'tab=' + self.__regid__}
            button = add_relations_button(self._cw, entity, _('add'),
                                          *relations_info, **urlparams)
            if button is not None:
                # No button if user cannot add any relation.
                self.w(button)
                self.w(tags.div(klass='clearfix'))
        for vid in self.subvids:
            try:
                entity.view(vid, w=self.w, tabid=self.__regid__)
            except NoSelectableObject:
                # no data to display, skip view
                continue


class EditLinkView(EntityView):
    """Render entity as a link to the edition view"""
    __regid__ = 'saem.edit-link'

    def entity_call(self, entity, icon_info=True, editurlparams=None):
        editurlparams = editurlparams or {}
        links = []
        if icon_info:
            links.append(('icon-info', self._cw._('view'), entity.absolute_url()))
        if entity.cw_has_perm('update'):
            links.append(('icon-pencil', self._cw._('edit'),
                          entity.absolute_url(vid='edition', **editurlparams)))
        if entity.cw_has_perm('delete'):
            links.append(('icon-trash', self._cw._('delete'),
                          entity.absolute_url(vid='deleteconf', **editurlparams)))
        for csscls, label, href in links:
            self.w(u'<span title="{label}">{link}</span>'.format(
                label=label, link=tags.a(klass=csscls, href=href)))


urlrewrite.SchemaBasedRewriter.rules.append(
    (urlrewrite.rgx('/ark:/(.+)'),
     urlrewrite.build_rset(rql=r'Any X WHERE X ark %(text)s', rgxgroups=[('text', 1)]))
)


class SAEMRefRewriter(urlrewrite.SimpleReqRewriter):
    """URL rewriter for SAEM-Ref"""
    rules = [
        ('/oai', dict(vid='oai')),
        ('/ark', dict(vid='saem.ws.ark')),
        ('/archival-units', dict(vid='saem.ws.archival-units')),
        ('/sedalib', dict(rql='Any X WHERE X is SEDAArchiveUnit, '
                              'NOT X seda_archive_unit P',
                          vid='saem.sedalib')),
    ]


@monkeypatch(tabs.TabsMixin)
def active_tab(self, default):
    return self._cw.form.get('tab', domid(default))


class URLAttributeView(primary.URLAttributeView):
    """Overriden from cubicweb to handle case where ark is directly used in cwuri, and so absolute
    url should be generated from it.
    """
    def entity_call(self, entity, rtype, **kwargs):
        if rtype == 'cwuri':
            url = xml_escape(cwuri_url(entity))
        else:
            url = entity.printable_value(rtype)
        if url:
            self.w(u'<a href="%s">%s</a>' % (url, url))


def registration_callback(vreg):
    from cubicweb.web.views import actions, cwuser, tableview, undohistory
    vreg.register_all(globals().values(), __name__, (URLAttributeView, SAEMHTMLPageFooter,))
    vreg.register_and_replace(URLAttributeView, primary.URLAttributeView)
    vreg.register_and_replace(SAEMHTMLPageFooter, basetemplates.HTMLPageFooter)
    vreg.unregister(tableview.TableView)
    vreg.unregister(undohistory.UndoHistoryView)
    vreg.unregister(basecomponents.ApplicationName)
    # unregister some undesired actions
    vreg.unregister(actions.SelectAction)
    vreg.unregister(actions.CancelSelectAction)
    vreg.unregister(actions.ViewAction)
    vreg.unregister(actions.MultipleEditAction)
    vreg.unregister(actions.CopyAction)
    vreg.unregister(actions.AddNewAction)
    vreg.unregister(actions.ViewSameCWEType)
    vreg.unregister(actions.UserPreferencesAction)
    vreg.unregister(actions.ManageAction)
    vreg.unregister(actions.PoweredByAction)
    vreg.unregister(cwuser.UserPreferencesEntityAction)
    # global actions
    vreg.unregister(actions.SiteConfigurationAction)
    # facets
    from cubicweb_seda.views.facets import SimplifiedProfileFacet
    vreg.unregister(SimplifiedProfileFacet)

    for menu_entry in main_navigation_menu():
        vreg.register(menu_entry)
