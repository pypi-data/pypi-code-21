# copyright 2015-2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""cubicweb-skos views"""

from copy import copy
from functools import partial

from logilab.common.decorators import cachedproperty
from rql.utils import uquote

from cubicweb import ValidationError, tags, _
from cubicweb.utils import make_uid, UStringIO
from cubicweb.predicates import (is_instance, has_related_entities, one_line_rset,
                                 score_entity, match_edited_type,
                                 match_form_params, match_user_groups,
                                 ExpectedValuePredicate)
from cubicweb.view import View, AnyRsetView, EntityView
from cubicweb.web import Redirect
from cubicweb.web import (action, component, formfields as ff, formwidgets as fw,
                          facet)
from cubicweb.web.views import (actions, autoform, editcontroller, formrenderers, uicfg,
                                ibreadcrumbs, forms, tabs, cwsources, treeview, baseviews)

from cubes.skos import CW_VERSION, to_unicode, lcsv
from cubes.skos.entities import CSVIndentationError, CSVDecodeError


# uicfg tweaks #################################################################

# configure index page
uicfg.indexview_etype_section['Label'] = 'hidden'

pvs = uicfg.primaryview_section
# configure primary view for ConceptScheme
pvs.tag_attribute(('ConceptScheme', 'title'), 'hidden')
pvs.tag_attribute(('ConceptScheme', 'cwuri'), 'attributes')

pvs.tag_object_of(('Concept', 'in_scheme', 'ConceptScheme'), 'hidden')
# configure primary view for Concept
pvs.tag_attribute(('Concept', 'cwuri'), 'attributes')
for label_type in ('preferred', 'alternative', 'hidden'):
    pvs.tag_subject_of(('*', '%s_label' % label_type, '*'), 'hidden')
pvs.tag_object_of(('*', 'label_of', '*'), 'hidden')
pvs.tag_subject_of(('Concept', 'in_scheme', '*'), 'hidden')
pvs.tag_subject_of(('Concept', 'broader_concept', 'Concept'), 'hidden')
pvs.tag_object_of(('Concept', 'broader_concept', 'Concept'), 'hidden')
pvs.tag_subject_of(('Concept', 'narrower_concept', 'Concept'), 'hidden')
pvs.tag_object_of(('Concept', 'narrower_concept', 'Concept'), 'hidden')

pvs.tag_subject_of(('SKOSSource', 'through_cw_source', '*'), 'hidden')

afs = uicfg.autoform_section
affk = uicfg.autoform_field_kwargs
# configure creation/edit for ConceptScheme
afs.tag_object_of(('*', 'in_scheme', '*'), 'main', 'hidden')
affk.set_field_kwargs('ConceptScheme', 'title', widget=fw.TextInput({'size': 80}))
# configure creation/edit for Concept
afs.tag_subject_of(('*', 'in_scheme', '*'), 'main', 'hidden')
afs.tag_subject_of(('Concept', 'broader_concept', 'Concept'), 'main', 'relations')
afs.tag_object_of(('Concept', 'broader_concept', 'Concept'), 'main', 'hidden')
afs.tag_subject_of(('Concept', 'narrower_concept', 'Concept'), 'main', 'hidden')
afs.tag_object_of(('Concept', 'narrower_concept', 'Concept'), 'main', 'hidden')
for label_type in ('preferred', 'alternative', 'hidden'):
    afs.tag_subject_of(('*', '%s_label' % label_type, '*'), 'main', 'hidden')
afs.tag_object_of(('*', 'label_of', '*'), 'main', 'inlined')
afs.tag_subject_of(('*', 'label_of', '*'), 'inlined', 'hidden')
affk.set_field_kwargs('Label', 'label', widget=fw.TextInput({'size': 80}))

# clickable cwuri in primary views
pvdc = uicfg.primaryview_display_ctrl
pvdc.tag_attribute(('*', 'cwuri'), {'vid': 'urlattr'})

# close_match is not symmetric and should only be viewable from the subject
pvs.tag_object_of(('*', 'close_match', 'Concept'), 'hidden')
afs.tag_object_of(('*', 'close_match', 'Concept'), 'main', 'hidden')


class AddConceptToConceptAction(action.LinkToEntityAction):
    __abstract__ = True
    __select__ = action.LinkToEntityAction.__select__ & is_instance('Concept')
    target_etype = 'Concept'

    def url(self):
        baseurl = super(AddConceptToConceptAction, self).url()
        entity = self.cw_rset.get_entity(0, 0)
        linkto = 'in_scheme:%s:subject' % (entity.scheme.eid)
        return '%s&__linkto=%s' % (baseurl, self._cw.url_quote(linkto))


class AddNarrowerConceptAction(AddConceptToConceptAction):
    __regid__ = 'skos.add_broader_concept'
    title = _('add Concept broader_concept Concept object')
    rtype = 'broader_concept'
    role = 'object'


class AddRelatedConceptAction(AddConceptToConceptAction):
    __regid__ = 'skos.add_related_concept'
    title = _('add Concept related_concept Concept subject')
    rtype = 'related_concept'
    role = 'subject'


# base views ###################################################################

class PaginatedListView(baseviews.ListView):
    __regid__ = 'paginated-list'

    @cachedproperty
    def domid(self):
        return self._cw.form.get('divid') or 'rs%s' % make_uid(id(self.cw_rset))

    def page_navigation_url(self, navcomp, _path, params):
        params['divid'] = self.domid
        params['vid'] = self.__regid__
        return navcomp.ajax_page_url(**params)

    def call(self, **kwargs):
        self.w(u'<div id="{0}">'.format(self.domid))
        nav_html = UStringIO()
        self.paginate(w=nav_html.write)
        self.w(nav_html.getvalue())
        super(PaginatedListView, self).call(**kwargs)
        self.w(nav_html.getvalue())
        self.w(u'</div>')


class ConceptSchemePrimaryView(tabs.TabbedPrimaryView):
    __select__ = is_instance('ConceptScheme')
    tabs = ['main_tab', _('skos_top_concepts_tab')]


class ConceptSchemeConceptsTab(tabs.TabsMixin, EntityView):
    """display a SKOS concept scheme tree"""
    __regid__ = 'skos_top_concepts_tab'  # don't use '.' in tab's regid
    __select__ = is_instance('ConceptScheme')

    def entity_call(self, entity):
        rschema = self._cw.vreg.schema.rschema('in_scheme')
        if rschema.has_perm(self._cw, 'add', toeid=entity.eid):
            self.w(tags.a(self._cw._('import concepts'),
                          href=entity.absolute_url(vid='skos.scheme.import'),
                          klass='btn btn-success pull-right'))
            self.w(tags.div(klass='clearfix'))
        rset = entity.top_concepts_rset
        if not rset:
            return
        if len(rset) < self._cw.property_value('navigation.page-size'):
            treeid = 'skos_tree_%s' % entity.eid
            self._cw.view('treeview', rset=rset, treeid=treeid, initial_thru_ajax=True, w=self.w)
        else:
            self._cw.view('paginated-list', rset=rset, w=self.w)


class ConceptPrimaryView(tabs.TabbedPrimaryView):
    __select__ = is_instance('Concept')
    tabs = ['main_tab', _('skos_sub_concepts_tab')]


class ConceptConceptsTab(tabs.TabsMixin, EntityView):
    """display a SKOS concept tree"""
    __regid__ = 'skos_sub_concepts_tab'  # don't use '.' in tab's regid
    __select__ = (is_instance('Concept') &
                  has_related_entities('narrower_concept'))

    def entity_call(self, entity):
        rset = entity.related('narrower_concept')
        treeid = 'skos_tree_%s' % entity.eid
        self._cw.view('treeview', rset=rset, treeid=treeid, initial_thru_ajax=True, w=self.w)


class ConceptLabelsComponent(component.EntityCtxComponent):
    """display concept labels in a table"""
    __regid__ = 'skos.concept.labels'
    __select__ = component.EntityCtxComponent.__select__ & is_instance('Concept')
    title = _('Labels')
    context = 'navcontentbottom'
    order = 2

    def render_body(self, w):
        rql = ('Any LL,LLC,LK ORDERBY LLC WHERE L label_of X, X eid %(x)s, '
               'L language_code LLC, L label LL, L kind LK')
        rset = self._cw.execute(rql, {'x': self.entity.eid})
        self._cw.view('table', rset=rset, w=w)


class ConceptMultiSchemeComponent(component.EntityCtxComponent):
    """display a SKOS concept's schemes if there are more than one"""
    __regid__ = 'skos.concept.parent-schemes'
    __select__ = (component.EntityCtxComponent.__select__ &
                  is_instance('Concept') &
                  score_entity(lambda x: len(x.in_scheme) > 1))
    title = _('ConceptScheme_plural')
    context = 'navcontentbottom'
    order = 1

    def render_body(self, w):
        w(self._cw._('This concept belongs to several schemes:'))
        self._cw.view('list', rset=self.entity.related('in_scheme'))


class TranslateView(AnyRsetView):
    __regid__ = 'translate'

    def cell_call(self, row, col, props=None, format='text/html'):
        self.w(self._cw._(self.cw_rset.rows[row][col]))


class ConceptIBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    __select__ = is_instance('Concept')

    def parent_entity(self):
        return self.entity.parent_concept or self.entity.scheme


# tree view ####################################################################

class ConceptTreeViewItemView(treeview.TreeViewItemView):
    """`treeitem` view for Concept with branch state closed by default"""
    __select__ = treeview.TreeViewItemView.__select__ & is_instance('Concept')

    def open_state(self, *args):
        return False


# facets #######################################################################

class InSchemeFacet(facet.RelationAttributeFacet):
    __regid__ = 'skos.facet.in_scheme'
    __select__ = facet.RelationAttributeFacet.__select__ & is_instance('Concept')
    rtype = 'in_scheme'
    role = 'subject'
    target_attr = 'title'


# ConceptScheme edition ########################################################

class ConceptSchemeAutoform(autoform.AutomaticEntityForm):
    """Autoform for ConceptScheme (creation only) with additional fields to
    import concepts from a file.
    """
    __select__ = (autoform.AutomaticEntityForm.__select__ & is_instance('ConceptScheme')
                  & score_entity(lambda x: not x.has_eid()))

    def __init__(self, *args, **kwargs):
        super(ConceptSchemeAutoform, self).__init__(*args, **kwargs)
        self.fieldsets_in_order = [None, _('inline csv import')]
        for field in ImportSchemeConceptsForm._fields_:
            field = copy(field)
            field.required = False
            field.fieldset = 'inline csv import'
            self.append_field(field)


class params_in_form(ExpectedValuePredicate):
    """Return 1 if expected values match with non-empty form parameters."""

    def __call__(self, cls, req, **kwargs):
        for param in self.expected:
            if not req.form.get(param):
                return 0
        return 1


class ConceptSchemeEditController(editcontroller.EditController):
    """Custom edit controller for ConceptScheme entity to handle import of
    concepts from file provided in edition form.
    """
    __select__ = (editcontroller.EditController.__select__ &
                  match_edited_type('ConceptScheme') &
                  match_form_params('stream', 'format', 'encoding', 'language_code', 'delimiter') &
                  params_in_form('stream'))

    def edit_entity(self, formparams, multiple=False):
        """Use created entity and import concepts from specified file."""
        eid = super(ConceptSchemeEditController, self).edit_entity(formparams, multiple=multiple)
        form = self._cw.form
        entity = self._cw.entity_from_eid(eid)
        _, fobj = form['stream']
        delimiter = CSV_DELIMITERS[form['delimiter']]
        _handle_concepts_import(self._cw, entity, form['format'],
                                stream=fobj, encoding=form['encoding'],
                                language_code=form['language_code'],
                                delimiter=delimiter)
        return eid


# simple file import ###########################################################

class ImportSchemeConceptsMixIn(object):
    __regid__ = 'skos.scheme.import'
    __select__ = (is_instance('ConceptScheme')
                  & match_user_groups('managers')
                  & one_line_rset())


class ImportSchemeConceptsForm(ImportSchemeConceptsMixIn, forms.EntityFieldsForm):
    """ask for a file to import"""
    filefield = ff.FileField(name='stream', label=_('file'), required=True)
    formatfield = ff.StringField(name='format', label=_('file format'),
                                 required=True, internationalizable=True,
                                 choices=[(_('simple'), u'simple'),
                                          (_(u'LCSV'), u'lcsv')], sort=False)
    encoding = ff.StringField(name='encoding', label=_('file encoding'),
                              internationalizable=True,
                              choices=[(_('utf-8'), u'utf-8'),
                                       (_('latin 1'), u'latin1')], sort=False)
    language = ff.StringField(name='language_code',
                              label=_('language of concepts in the file'),
                              internationalizable=True,
                              choices=[(_('french'), u'fr'),
                                       (_('english'), u'en')], sort=False)
    delimiter = ff.StringField(name='delimiter', label=_('hierarchical delimiter'),
                               internationalizable=True,
                               choices=[(_('tabulation'), 'tab'),
                                        (_(';'), ';'),
                                        (_(','), ','),
                                        (_('space'), 'space')], sort=False)
    form_buttons = [fw.SubmitButton(label=_('to_import'))]

    @property
    def action(self):
        return self.edited_entity.absolute_url(vid=self.__regid__)


CSV_DELIMITERS = {'tab': '\t', 'space': ' ', ',': ',', ';': ';'}


class ImportSchemeConceptsView(ImportSchemeConceptsMixIn, EntityView):

    def entity_call(self, entity):
        self.w('<h1>%s</h1>' % self._cw._('Import concepts from file'))
        form = self._cw.vreg['forms'].select(self.__regid__, self._cw, entity=entity)
        if form.posting:
            posted = form.process_posted()
            if 'stream' not in posted:  # https://www.cubicweb.org/ticket/5245936
                raise ValidationError(None, {'stream': self._cw.__("required field")})
            kwargs = {field.name: posted[field.name] for field in form._fields_}
            kwargs['delimiter'] = CSV_DELIMITERS[kwargs['delimiter']]
            try:
                _handle_concepts_import(self._cw, entity, kwargs.pop('format'), **kwargs)
            except:
                # for unclear reason we have to pop stream from form data, else
                # it's stored in session's data while it's not pickleable,
                # leading to silent error in set_cookie with pyramid.
                self._cw.form.pop('stream')
                raise
            raise Redirect(entity.absolute_url(__message=self._cw._('Import completed')))
        else:
            form.render(w=self.w)


def _handle_concepts_import(req, entity, fileformat, **kwargs):
    """Entry point of import of concepts to be related to concept scheme
    `entity` based of specified file format.
    """
    assert fileformat in ('simple', 'lcsv'), fileformat
    if fileformat == 'simple':
        _simple_import(req, entity, **kwargs)
    else:
        _lcsv_import(req, entity, **kwargs)


def _simple_import(req, entity, **kwargs):
    """Trigger import of concepts to be related to concept scheme `entity`
    using a the 'simple' text format.
    """
    try:
        entity.add_concepts_from_file(**kwargs)
    except CSVIndentationError as exc:
        raise ValidationError(entity.eid,
                              {None: req._("Indentation error line %s") % exc.line})
    except CSVDecodeError as exc:
        raise ValidationError(entity.eid,
                              {None: req._("Encoding error line %s") % exc.line})


def _lcsv_import(req, entity, **kwargs):
    """Trigger import of concepts to be related to concept scheme `entity`
    using the LCSV text format.
    """
    try:
        req.cnx.call_service('lcsv.skos.import', scheme_uri=entity.cwuri, **kwargs)
    except lcsv.InvalidLCSVFile as exc:
        if exc.column:
            msg = req._(to_unicode(exc)) % exc.column
        else:
            msg = req._(to_unicode(exc))
        raise ValidationError(entity.eid, {None: msg})


# SKOS import ##################################################################

class ImportConceptSchemeAction(action.Action):
    __regid__ = 'rdf.skos.import'
    __select__ = match_user_groups('managers')
    title = _('import concept scheme from SKOS')
    category = 'manage'

    def url(self):
        return self._cw.build_url(vid=self.__regid__)


class SKOSImportForm(forms.FieldsForm):
    """ask for a file to import"""
    __regid__ = 'rdf.skos.import'
    __select__ = match_user_groups('managers')
    filefield = ff.FileField(name='file', label=_('SKOS file'), required=True)
    formatfield = ff.StringField(name='format', label=_('RDF format'),
                                 internationalizable=True,
                                 choices=[(_('per extension'), ''),
                                          (_('xml'), u'xml'),
                                          (_('ntriples'), u'nt'),
                                          (_('n3'), u'n3')],
                                 sort=False)
    form_buttons = [fw.SubmitButton(label=_('to_import'))]

    @property
    def action(self):
        return self._cw.build_url(vid=self.__regid__)


class SKOSImportResultView(View):
    __regid__ = 'rdf.skos.import'
    __select__ = match_user_groups('managers')

    def call(self):
        self.w('<h1>%s</h1>' % self._cw._('Import a SKOS file'))
        form = self._cw.vreg['forms'].select(self.__regid__, self._cw)
        if form.posting:
            posted = form.process_posted()
            if 'file' not in posted:  # https://www.cubicweb.org/ticket/5245936
                raise ValidationError(None, {'file': self._cw.__("required field")})
            stream = posted['file']
            rdf_format = posted['format']
            try:
                logs, scheme_uris = self._cw.cnx.call_service('rdf.skos.import', stream=stream,
                                                              rdf_format=rdf_format)
            except Exception as exc:
                logs = None
                msg = self._cw._('SKOS import failed: ') + to_unicode(exc)
                self.exception('error while importing %s', stream.filename)
            else:
                if scheme_uris:
                    schemes = self._cw.execute('Any X WHERE X is ConceptScheme, X cwuri IN (%s)'
                                               % ','.join(uquote(uri) for uri in scheme_uris))
                    msg = self._cw._('SKOS import completed: %s') % self._cw.view('csv', schemes)
                else:
                    msg = self._cw._('SKOS import completed but no scheme was found')
            self.w(u'<div class="message">%s</div>' % msg)
            if logs:
                self._cw.view('cw.log.table',
                              pyvalue=cwsources.log_to_table(self._cw, u''.join(logs)),
                              default_level='Info', w=self.w)

        else:
            form.render(w=self.w)


# SKOSSource #######################################################################################

class SiteConfigurationAction(actions.ManagersAction):
    __regid__ = 'skossource'
    title = _('SKOS sources')
    order = 10
    category = 'manage'


class SKOSSourcePrimaryView(tabs.TabbedPrimaryView):
    __select__ = is_instance('SKOSSource')
    tabs = [_('skos.source-main'), _('skos.source-imports')]
    default_tab = 'skos.source-main'


class SKOSSourceMainTab(tabs.PrimaryTab):
    __regid__ = 'skos.source-main'
    __select__ = is_instance('SKOSSource')


class SKOSSourceImportsTab(EntityView):
    __regid__ = 'skos.source-imports'
    __select__ = is_instance('SKOSSource')

    def entity_call(self, entity):
        if self._cw.user.is_in_group('managers'):
            self.w(tags.a(self._cw._('synchronize'), klass='btn btn-success pull-right',
                          href=entity.absolute_url(vid='skos.source-sync')))
            self.w(tags.div(klass='clearfix'))
        source = entity.through_cw_source[0]
        rset = source.related('cw_import_of', role='object')
        if rset:
            self._cw.view('cw.imports-table', rset=rset, w=self.w)


class SKOSSourceConceptComponent(component.EntityCtxComponent):
    """Display schemes related to the source"""
    __regid__ = 'skos.source.schemes'
    __select__ = component.EntityCtxComponent.__select__ & is_instance('SKOSSource')
    title = _('ConceptScheme_plural')
    context = 'navcontentbottom'
    order = 2

    def render_body(self, w):
        rset = self._cw.execute('Any X, XT WHERE X is ConceptScheme, X title XT, '
                                'X cw_source CWS, S through_cw_source CWS, S eid %(s)s',
                                {'s': self.entity.eid})
        if rset:
            self._cw.view('list', rset=rset, w=w)
        else:
            w(self._cw._('This source has no associated scheme. This may be because it has not '
                         'yet been synchronized. You may ask for synchronization using the button '
                         'in the "imports" tab. <b>If there is a lot of concepts to import, you '
                         'should probably rather ask the site administrator to import it for you.'
                         '</b>'))


class SKOSSourceSyncView(EntityView):
    __regid__ = 'skos.source-sync'
    __select__ = (match_user_groups('managers')
                  & one_line_rset() & is_instance('SKOSSource'))

    title = _('synchronize')

    def entity_call(self, entity):
        source = entity.through_cw_source[0]
        import_log_eid = self._cw.call_service('source-sync', source_eid=source.eid)
        import_log = self._cw.entity_from_eid(import_log_eid)
        msg = self._cw._('Synchronization has been requested, refresh this page in a few '
                         'minutes.')
        url = import_log.absolute_url(__message=msg)
        raise Redirect(url)


class CWDataImportIBreadCrumbsAdapter(cwsources.CWDataImportIBreadCrumbsAdapter):
    """Custom breadcrumbs adapter for CWDataImport so that if cubicweb's source is underlying to a
    SKOSSource, imports appear as under the later.
    """
    __select__ = (cwsources.CWDataImportIBreadCrumbsAdapter.__select__
                  & score_entity(lambda x: x.cwsource.reverse_through_cw_source))

    def parent_entity(self):
        return self.entity.cwsource.reverse_through_cw_source[0]


class SKOSSourceFormRenderer(formrenderers.FormRenderer):
    __select__ = is_instance('SKOSSource')

    def render(self, w, form, values):
        w('<div class="help-block">%s</div>' % (self._cw._(
            'This form allows to import SKOS RDF published on the Internet using a <b>source</b>. '
            'Sources may be synchronized when desired.')))
        w('<div class="help-block">%s</div>' % (self._cw._(
            'Please specify <b>an arbitrary short name</b> for the data source and '
            '<b>one or more URL from which RDF data may be retrieved</b>.')))
        super(SKOSSourceFormRenderer, self).render(w, form, values)


# https://www.cubicweb.org/ticket/5474286 ##########################################################

if CW_VERSION < (3, 22):

    class CWSourceSyncAction(action.Action):
        __regid__ = 'cw.source-sync'
        __select__ = (action.Action.__select__ & match_user_groups('managers')
                      & one_line_rset() & is_instance('CWSource')
                      & score_entity(lambda x: x.name != 'system'))
        title = _('synchronize')
        category = 'mainactions'
        order = 20

        def url(self):
            entity = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
            return entity.absolute_url(vid=self.__regid__)

if CW_VERSION < (3, 23):
    # asynchronous source synchronization from the UI (https://www.cubicweb.org/ticket/10468967) ###

    from cubicweb.server import Service  # noqa

    class SourceSynchronizationService(Service):
        """Force synchronization of a datafeed source. Actual synchronization is done
        asynchronously, this will simply create and return the entity which will hold the import
        log.
        """
        __regid__ = 'source-sync'
        __select__ = Service.__select__ & match_user_groups('managers')

        def call(self, source_eid):
            source = self._cw.entity_from_eid(source_eid)
            import_log = self._cw.create_entity('CWDataImport', cw_import_of=source)
            self._cw.commit()  # commit the import log creation before starting the synchronize task

            def _synchronize_source(repo, source_eid, import_log_eid):
                with repo.internal_cnx() as cnx:
                    source = repo.sources_by_eid[source_eid]
                    source.pull_data(cnx, force=True, import_log_eid=import_log_eid)

            sync = partial(_synchronize_source, self._cw.repo, source_eid, import_log.eid)
            self._cw.repo.threaded_task(sync)
            return import_log.eid

    class CWSourceSyncView(EntityView):
        __regid__ = 'cw.source-sync'
        __select__ = (match_user_groups('managers')
                      & one_line_rset() & is_instance('CWSource')
                      & score_entity(lambda x: x.name != 'system'))

        title = _('synchronize')

        def entity_call(self, entity):
            import_log_eid = self._cw.call_service('source-sync', source_eid=entity.eid)
            msg = self._cw._('Synchronization has been requested, refresh this page in a few '
                             'minutes.')
            import_log = self._cw.entity_from_eid(import_log_eid)
            url = import_log.absolute_url(__message=msg)
            raise Redirect(url)


def registration_callback(vreg):
    if CW_VERSION == (3, 22):
        from cubicweb.sobjects import services
        vreg.register_all(globals().values(), __name__,
                          (CWSourceSyncView, SourceSynchronizationService))
        vreg.register_and_replace(CWSourceSyncView,
                                  cwsources.CWSourceSyncView)
        vreg.register_and_replace(SourceSynchronizationService,
                                  services.SourceSynchronizationService)
    else:
        vreg.register_all(globals().values(), __name__)
