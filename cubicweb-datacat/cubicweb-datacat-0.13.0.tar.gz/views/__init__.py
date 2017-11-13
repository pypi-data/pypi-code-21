# copyright 2014-2015 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""cubicweb-datacat views/forms/actions/components for web ui"""

from functools import partial
from copy import deepcopy
import json
import re
import urlparse

from logilab.mtconverter import (
    xml_escape,
)

from cubicweb import (
    _,
    tags,
)
from cubicweb.predicates import (
    adaptable,
    has_related_entities,
    is_instance,
    match_user_groups,
    one_line_rset,
    score_entity,
)
from cubicweb.uilib import js
from cubicweb.utils import json_dumps
from cubicweb.web import (
    action,
    component,
    facet as cwfacet,
    formwidgets as fw,
    Redirect,
)
from cubicweb.web.views import (
    actions,
    ajaxcontroller,
    baseviews,
    ibreadcrumbs,
    idownloadable,
    json as jsonviews,
    navigation,
    uicfg,
)
from cubicweb.view import (
    AnyRsetView,
    EntityView,
)

from cubes.relationwidget import views as rwdg
from cubes.skos import rdfio
from cubes.skos.views import rdf as rdfviews
from cubes.datacat import opendefinition_licenses
from cubes.datacat.entities import license_rdf_uri


abaa = uicfg.actionbox_appearsin_addmenu
afs = uicfg.autoform_section
affk = uicfg.autoform_field_kwargs
pvdc = uicfg.primaryview_display_ctrl
pvs = uicfg.primaryview_section


uicfg.indexview_etype_section['TransformationSequence'] = 'subobject'
# already shown in "administration" section
uicfg.indexview_etype_section['SKOSSource'] = 'subobject'


def build_selectable_uicfg(rtag, select):
    """Return a copy of uicfg `rtag` with `select` set."""
    copy = deepcopy(rtag)
    copy.__module__ = __name__
    copy.__select__ = select
    return copy


def _autocomplete_widget(fname, wdgclass=fw.LazyRestrictedAutoCompletionWidget,
                         placeholder=None):
    if placeholder is None:
        placeholder = _("Start to type your choice: you'll be presented a list of "
                        "matching terms")
    return wdgclass(
        attrs={'placeholder': placeholder, 'size': 82},
        autocomplete_initfunc=fname,
        autocomplete_settings={'limit': 100, 'delay': 300},
    )


def search_in_scheme(req, scheme_uri):
    """Query ConceptScheme with `scheme_uri` for a Label matching `q` term
    found in request's form.
    """
    term = req.form['q']
    limit = req.form.get('limit', 50)
    lang = req.lang
    qs = ('DISTINCT Any X LIMIT {0} '
          'WHERE X in_scheme S, S cwuri %(scheme)s, L label_of X, L label LL,'
          '      L label ILIKE %(term)s'.format(limit))
    args = {'scheme': scheme_uri, 'term': u'%%%s%%' % term}
    return [{'value': concept.eid, 'label': concept.label(language_code=lang)}
            for concept in req.execute(qs, args).entities()]


class NoRedirectAddRelatedActions(actions.AddRelatedActions):
    """Override 'addrelated' action to avoid redirection to the parent entity."""

    __select__ = (actions.AddRelatedActions.__select__ &
                  is_instance('Agent', 'DataCatalog', 'Dataset', 'Distribution'))

    def redirect_params(self, *args, **kwargs):
        return {}


class WorkflowableEntityOutOfContextView(baseviews.OutOfContextView):
    """Out of context view showing workflow state"""

    __select__ = baseviews.OutOfContextView.__select__ & adaptable('IWorkflowable')

    def cell_call(self, row, col, **kwargs):
        self.w(u'<div style="margin-top: 1px;" class="clearfix">')
        super(WorkflowableEntityOutOfContextView, self).cell_call(row, col, **kwargs)
        entity = self.cw_rset.get_entity(row, col)
        iwf = entity.cw_adapt_to('IWorkflowable')
        self.w(tags.span(iwf.printable_state, klass='badge pull-right'))
        self.w(u'</div>')


#
# RDF views
#

class DatasetDCATRDFView(rdfviews.RDFPrimaryView):
    """RDF view for Dataset entities, outputting complete information about
    catalog, distributions and agents.

    This is mainly useful for clients who *do not follow URIs* to gather information about related
    resources and expect all information at one URL (eg. CKAN).
    """

    __regid__ = 'dcat.rdf.complete'
    __select__ = rdfviews.RDFPrimaryView.__select__ & is_instance('Dataset')
    # (rtype, role, <adapter regid>) of related entities to export along with
    # the dataset.
    follow_related = [
        ('in_catalog', 'subject', 'RDFPrimary'),
        ('of_dataset', 'object', 'RDFPrimary'),
        ('dataset_publisher', 'subject', 'RDFPrimary'),
        ('dataset_contact_point', 'subject', 'RDFContactPoint'),
        ('temporal_coverage', 'subject', 'RDFPrimary'),
        ('locate_datasets', 'object', 'RDFPrimary'),
    ]

    def entity_call(self, entity, graph=None):
        # Copied from parent class
        dump = graph is None
        if graph is None:
            graph = rdfio.default_graph()
        rdfgenerator = entity.cw_adapt_to(self.adapter)
        rdfgenerator.fill(graph)
        # Also output related entities
        for rtype, role, adapter in self.follow_related:
            for related in entity.related(rtype, role, entities=True):
                rdfgenerator = related.cw_adapt_to(adapter)
                rdfgenerator.fill(graph)
        # Copied from parent class
        if dump:
            self._dump(graph)


class DataCatalogDCATRDFView(rdfviews.RDFPrimaryView):
    """RDF view outputting complete information about catalog and children entities.

    This is mainly useful for clients who *do not follow URIs* to gather information about related
    resources and expect all information at one URL (eg. CKAN).
    """

    __regid__ = 'dcat.rdf.complete'
    __select__ = (rdfviews.RDFPrimaryView.__select__ &
                  has_related_entities('in_catalog', role='object'))

    def entity_call(self, entity, graph=None):
        # Copied from parent class
        dump = graph is None
        if graph is None:
            graph = rdfio.default_graph()
        for dataset in entity.related('in_catalog', role='object').entities():
            dataset.view(self.__regid__, graph=graph)
        # Copied from parent class
        if dump:
            self._dump(graph)


class DataCatalogCkanDCATRDFView(DataCatalogDCATRDFView):
    """Backward compatible view calling 'dcat.rdf.complete'."""
    __regid__ = 'dcat.rdf.ckan'


class DatasetCkanDCATRDFView(DatasetDCATRDFView):
    """Backward compatible view calling 'dcat.rdf.complete'."""
    __regid__ = 'dcat.rdf.ckan'


class RDFExportAction(action.Action):

    __regid__ = 'dcat.rdf-export'
    __select__ = one_line_rset() & is_instance('Dataset', 'DataCatalog')
    title = _('RDF export')

    def url(self):
        entity = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        return entity.absolute_url(vid='dcat.rdf.complete')


#
# JSON views
#


class CkanJsonLicenseView(jsonviews.JsonMixIn, EntityView):
    """JSON view outputting data about a license that CKAN can use as ``licenses_group_url``. """

    __regid__ = 'dcat.ckan.json.license'
    __select__ = (EntityView.__select__ & score_entity(lambda c: in_license_scheme(c)))

    def entity_call(self, entity, **kwargs):
        od_licenses = opendefinition_licenses()
        url2lic = {}
        title2lic = {}
        for lic_dict in od_licenses.values():
            title2lic[lic_dict['title'].lower()] = lic_dict
            if lic_dict['url']:
                urltuple = urlparse.urlsplit(lic_dict['url'])  # Remove {http://,https://} from URL
                url = urltuple.netloc + urltuple.path
                url2lic[url] = lic_dict
        # Build JSON license
        title = entity.label(language_code=u'en')
        url = license_rdf_uri(entity)
        urltuple = urlparse.urlsplit(url)
        url0 = urltuple.netloc + urltuple.path
        found = url2lic.get(url0, {})  # Find an Open Definition license with same URL
        if not found:
            for title_variant in (  # Find an Open Definition license with same title
                title,
                title.replace('License', 'Licence'),
                re.sub(r'v(\d)', lambda match: match.group(1), title),  # v1.0 -> 1.0
                re.sub(r'v(\d)', lambda match: match.group(1),
                       title.replace('License', 'Licence')),
            ):
                found = title2lic.get(title_variant.lower(), {})
                if found:
                    break
        license = {'title': title, 'url': found.get('url') or url}
        for key, default_value in [
            ('domain_content', False),
            ('domain_data', True),
            ('domain_software', False),
            ('family', u''),
            ('id', entity.absolute_url()),
            ('maintainer', u''),
            ('od_conformance', u'not reviewed'),
            ('osd_conformance', u'not reviewed'),
            ('status', u'active'),
        ]:
            license[key] = found.get(key, default_value)
        self.w(json_dumps(license, sort_keys=True))


class CkanJsonLicensesAction(action.Action):

    __regid__ = 'dcat.ckan.json.licenses'
    __select__ = (is_instance('ConceptScheme')
                  & score_entity(lambda cs: cs.scheme_relation and
                                 cs.scheme_relation[0].name == u'license_type'))
    title = _('JSON export for CKAN')

    def url(self):
        return self._cw.build_url(vid=self.__regid__,
                                  rql=self.cw_rset.printable_rql())


class CkanJsonLicensesView(jsonviews.JsonMixIn, AnyRsetView):
    """JSON view outputting data about a license that CKAN can use as ``licenses_group_url``. """

    __regid__ = 'dcat.ckan.json.licenses'
    __select__ = (AnyRsetView.__select__ &
                  score_entity(lambda cs: cs.scheme_relation and
                               cs.scheme_relation[0].name == u'license_type'))

    def call(self, **kwargs):
        licenses = []
        for scheme in self.cw_rset.entities():
            for concept in scheme.reverse_in_scheme:
                licenses.append(
                    json.loads(concept.view('dcat.ckan.json.license'))
                )
        self.w(json_dumps(licenses, sort_keys=True))


#
# HTML views
#

# DCAT-AP restrictions.
# Set some relations as "required" to conform to DCAT-AP recommandations
# despite our schema matches plain DCAT which is more permissive. Only DCAT-AP
# profile is supported through the UI at the moment.
affk.tag_attribute(('DataCatalog', 'title'), {'required': True})
affk.tag_attribute(('DataCatalog', 'description'), {'required': True})
affk.tag_attribute(('Dataset', 'title'), {'required': True})
affk.tag_attribute(('Dataset', 'description'), {'required': True})
affk.tag_subject_of(('DataCatalog', 'catalog_publisher', '*'),
                    {'required': True})


class NoPreviewIDownloadablePrimaryView(idownloadable.IDownloadablePrimaryView):
    """IDownloadablePrimaryView without data preview."""

    def render_data(self, *args):
        return False


class IDownloadableOutOfContextView(baseviews.OutOfContextView):
    """Out of context view for IDownloadable

    Adapted from cubicweb.web.views.idownloadable.IDownloadableOneLineView
    with content-type and a download icon.

    This is used in `file_distribution` relation contextual component in
    particular.
    """

    __select__ = (baseviews.OutOfContextView.__select__ &
                  adaptable('IDownloadable'))
    download_icon = 'glyphicon glyphicon-download-alt'

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        url = xml_escape(entity.absolute_url())
        adapter = entity.cw_adapt_to('IDownloadable')
        name = xml_escape(entity.dc_title())
        durl = xml_escape(adapter.download_url())
        dcontenttype = xml_escape(adapter.download_content_type())
        self.w(u'<a class="{2}" href="{0}" title="{1}"></a> '.format(
               durl, self._cw._('download'), self.download_icon))
        self.w(u'<a href="{0}">{1}</a> '.format(url, name))
        self.w(u'<span class="badge">{0}</span>'.format(dcontenttype))


# File
uicfg.indexview_etype_section['File'] = 'subobject'
pvs.tag_subject_of(('File', 'replaces', '*'), 'hidden')
pvs.tag_object_of(('*', 'replaces', 'File'), 'hidden')
afs.tag_object_of(('*', 'replaces', 'File'), 'main', 'hidden')
abaa.tag_object_of(('*', 'replaces', 'File'), True)

# afs.tag_subject_of(('File', 'resource_of', '*'), 'main', 'hidden')
afs.tag_object_of(('*', 'process_input_file', 'File'), 'main', 'hidden')

pvs.tag_subject_of(('File', 'file_distribution', '*'), 'hidden')


navigation.NextPrevNavigationComponent.context = 'navtop'


class FileIPrevNextAdapter(navigation.IPrevNextAdapter):
    """IPrevNext adapter for file replaced by or replacing another file.
    """

    __select__ = (has_related_entities('replaces', role='subject') |
                  has_related_entities('replaces', role='object'))

    def next_entity(self):
        successors = self.entity.reverse_replaces
        if successors:
            return successors[0]

    def previous_entity(self):
        predecessors = self.entity.replaces
        if predecessors:
            return predecessors[0]


class FileReplacedBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    """Define <New file version>/<Old file version> breadcrumb."""

    __select__ = (ibreadcrumbs.IBreadCrumbsAdapter.__select__ &
                  has_related_entities('replaces', role='object'))

    def parent_entity(self):
        return self.entity.reverse_replaces[0]


class DistributionFileBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    """Define Distribution / File breadcrumbs"""
    __select__ = (ibreadcrumbs.IBreadCrumbsAdapter.__select__ &
                  has_related_entities('file_distribution', role='subject') &
                  # Prevent select ambiguity ad File can be object of both
                  # `implemented_by` and `file_distribution` relations.
                  ~has_related_entities('implemented_by', role='object'))

    def parent_entity(self):
        return self.entity.file_distribution[0]


# Agent
abaa.tag_object_of(('*', 'catalog_publisher', 'Agent'), True)
afs.tag_object_of(('*', 'catalog_publisher', 'Agent'), 'main', 'hidden')
affk.set_field_kwargs('Agent', 'name', widget=fw.TextInput({'size': 82}))
affk.set_field_kwargs('Agent', 'email', widget=fw.TextInput({'size': 82}))
pvs.tag_subject_of(('Agent', 'publisher_type', 'Concept'), 'attributes')
afs.tag_subject_of(('Agent', 'publisher_type', 'Concept'), 'main', 'attributes')


# Concept

pvs.tag_object_of(('*', 'catalog_license', 'Concept'), 'hidden')


def scheme_relation_choices(form, field, **kwargs):
    """Choices function for CheckBox widget to select/unselect whether a scheme
    is used to qualify a license_type relationship.
    """
    choices = [(form._cw._('no specific usage'), u'')]
    for name in (u'license_type', u'dataset_type'):
        rtype_eid = form._cw.find('CWRType', name=name)[0][0]
        choices.append((form._cw._(name), unicode(rtype_eid)))
    return choices


def scheme_relation_value(form, field, **kwargs):
    """Return current value of scheme_relation."""
    edited = form.edited_entity
    if edited.scheme_relation:
        rtype = edited.scheme_relation[0]
        return (rtype.name, rtype.eid)
    return u''


def in_license_scheme(entity):
    """Return 1 if entity is a Concept in a scheme used to describe license
    type.
    """
    if not entity.cw_etype == 'Concept':
        return 0
    if not entity.has_eid():
        return 0
    scheme = entity.in_scheme[0]
    if (scheme.scheme_relation and
            scheme.scheme_relation[0].name == u'license_type'):
        return 1
    return 0


pvs.tag_subject_of(('Concept', 'license_type', 'Concept'), 'hidden')

license_concept_pvs = build_selectable_uicfg(pvs, score_entity(in_license_scheme))
license_concept_pvs.tag_subject_of(('Concept', 'license_type', 'Concept'), 'attributes')


afs.tag_subject_of(('Concept', 'license_type', 'Concept'), 'main', 'hidden')
afs.tag_object_of(('Concept', 'license_type', 'Concept'), 'main', 'hidden')
for rtype in ('publisher_type', 'language', 'dataset_frequency', 'dcat_theme',
              'license', 'media_type', 'distribution_format'):
    afs.tag_object_of(('*', rtype, 'Concept'), 'main', 'hidden')
afs.tag_subject_of(('Concept', 'license', '*'), 'main', 'hidden')

licence_concept_afs = build_selectable_uicfg(afs, score_entity(in_license_scheme))
licence_concept_afs.tag_subject_of(('Concept', 'license_type', 'Concept'), 'main', 'attributes')
afs.tag_object_of(('*', 'theme_taxonomy', 'ConceptScheme'), 'main', 'hidden')
afs.tag_subject_of(('ConceptScheme', 'scheme_relation', '*'), 'main', 'attributes')
affk.tag_subject_of(('ConceptScheme', 'scheme_relation', '*'),
                    {'label': _('usage'),
                     'help': _('usage of concepts in this scheme'),
                     'widget': fw.Radio,
                     'value': scheme_relation_value,
                     'fallback_on_none_attribute': True,
                     'sort': True,
                     'choices': scheme_relation_choices})


# DataCatalog
pvs.tag_attribute(('DataCatalog', 'title'), 'hidden')
pvs.tag_attribute(('DataCatalog', 'issued'), 'hidden')
afs.tag_attribute(('DataCatalog', 'issued'), 'main', 'hidden')
pvs.tag_attribute(('DataCatalog', 'modified'), 'hidden')
afs.tag_attribute(('DataCatalog', 'modified'), 'main', 'hidden')
pvs.tag_subject_of(('DataCatalog', 'catalog_publisher', '*'), 'hidden')
pvs.tag_subject_of(('DataCatalog', 'license', '*'), 'attributes')
pvdc.tag_subject_of(('DataCatalog', 'license', '*'), {'vid': 'incontext'})
afs.tag_subject_of(('DataCatalog', 'theme_taxonomy', '*'), 'main', 'attributes')
afs.tag_subject_of(('DataCatalog', 'catalog_publisher', '*'), 'main', 'attributes')
abaa.tag_object_of(('*', 'in_catalog', 'DataCatalog'), True)
abaa.tag_subject_of(('DataCatalog', 'theme_taxonomy', '*'), True)
afs.tag_object_of(('*', 'in_catalog', 'DataCatalog'), 'main', 'hidden')
pvdc.tag_attribute(('DataCatalog', 'homepage'), {'vid': 'urlattr'})
for attr in ('title', 'homepage'):
    affk.set_field_kwargs('DataCatalog', attr, widget=fw.TextInput({'size': 82}))
afs.tag_subject_of(('DataCatalog', 'license', 'Concept'), 'main', 'attributes')
pvs.tag_subject_of(('DataCatalog', 'language', '*'), 'attributes')
afs.tag_subject_of(('DataCatalog', 'language', '*'), 'main', 'attributes')
affk.tag_subject_of(('DataCatalog', 'language', '*'),
                    {'widget': rwdg.RelationFacetWidget(no_creation_form=True)})


class DataCatalogBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    """Define <Agent>/<DataCatalog> breadcrumb."""

    __select__ = (ibreadcrumbs.IBreadCrumbsAdapter.__select__ &
                  has_related_entities('catalog_publisher'))

    def parent_entity(self):
        return self.entity.catalog_publisher[0]


pvs.tag_subject_of(('*', 'spatial_coverage', '*'), 'attributes')
afs.tag_subject_of(('*', 'spatial_coverage', '*'), 'main', 'attributes')
affk.tag_subject_of(('*', 'spatial_coverage', '*'),
                    {'widget': rwdg.RelationFacetWidget(no_creation_form=True)})


# Dataset

def dataset_publisher_choices(form, field, **kwargs):
    """Return form field choices corresponding to all possible publishers for a dataset."""
    # Try to find out if this dataset is linked to a catalog
    linkedto = form.linked_to.get(('in_catalog', 'subject'))
    if linkedto:  # Adding dataset from a catalog view
        catalog = form._cw.entity_from_eid(linkedto[0])
        publishers = catalog.catalog_publisher
        publisher = publishers[0] if publishers else None
        if publisher is not None:
            return [(publisher.dc_title(), unicode(publisher.eid))]
    limit = kwargs.get('limit', 50)
    qs = 'DISTINCT Agent X LIMIT {limit}'.format(limit=limit)
    return [(entity.dc_title(), unicode(entity.eid)) for entity in form._cw.execute(qs).entities()]


pvs.tag_subject_of(('Dataset', 'in_catalog', '*'), 'hidden')
pvs.tag_subject_of(('Dataset', 'dataset_frequency', '*'), 'attributes')
pvs.tag_subject_of(('Dataset', 'dataset_contact_point', '*'), 'attributes')
pvs.tag_subject_of(('Dataset', 'dataset_publisher', '*'), 'attributes')
pvs.tag_subject_of(('Dataset', 'temporal_coverage', '*'), 'attributes')
pvdc.tag_attribute(('Dataset', 'landing_page'), {'vid': 'urlattr'})
afs.tag_subject_of(('Dataset', 'dataset_contact_point', '*'), 'main', 'attributes')
afs.tag_subject_of(('Dataset', 'dataset_publisher', '*'), 'main', 'attributes')
pvs.tag_subject_of(('Dataset', 'dataset_contributors', '*'), 'attributes')
afs.tag_subject_of(('Dataset', 'dataset_contributors', '*'), 'main', 'attributes')
afs.tag_subject_of(('Dataset', 'temporal_coverage', '*'), 'main', 'inlined')
abaa.tag_subject_of(('Dataset', 'temporal_coverage', '*'), False)
pvs.tag_attribute(('Dataset', 'title'), 'hidden')
pvs.tag_attribute(('Dataset', 'identifier'), 'hidden')
afs.tag_attribute(('Dataset', 'identifier'), 'main', 'hidden')
pvs.tag_attribute(('Dataset', 'issued'), 'hidden')
afs.tag_attribute(('Dataset', 'issued'), 'main', 'hidden')
pvs.tag_attribute(('Dataset', 'modified'), 'hidden')
afs.tag_attribute(('Dataset', 'modified'), 'main', 'hidden')
# Keep dcat_theme hidden from autoform since the RelationWidget will not work
# on creation as constraints on DataCatalog cannot be checked and we prefer
# the user to edit this *inline* from the primary view.
afs.tag_subject_of(('Dataset', 'dcat_theme', '*'), 'main', 'hidden')
pvs.tag_subject_of(('Dataset', 'dcat_theme', '*'), 'attributes')
affk.tag_subject_of(('Dataset', 'dcat_theme', '*'),
                    {'widget': rwdg.RelationFacetWidget(no_creation_form=True)})
pvs.tag_subject_of(('Dataset', 'dataset_type', '*'), 'attributes')
afs.tag_subject_of(('Dataset', 'dataset_type', '*'), 'main', 'attributes')
affk.tag_subject_of(('Dataset', 'dataset_type', '*'),
                    {'widget': rwdg.RelationFacetWidget(no_creation_form=True)})
afs.tag_subject_of(('Dataset', 'in_catalog', '*'), 'main', 'attributes')
afs.tag_object_of(('*', 'resource_feed_of', 'Dataset'), 'main', 'hidden')
afs.tag_object_of(('*', 'of_dataset', 'Dataset'), 'main', 'hidden')
for attr in ('identifier', 'title', 'keyword', 'landing_page',
             'provenance'):
    affk.set_field_kwargs('Dataset', attr, widget=fw.TextInput({'size': 82}))
afs.tag_subject_of(('Dataset', 'dataset_frequency', 'Concept'),
                   'main', 'attributes')
affk.tag_subject_of(('Dataset', 'dataset_publisher', '*'),
                    {'choices': dataset_publisher_choices})

pvs.tag_object_of(('*', 'locate_datasets', 'Dataset'), 'hidden')
afs.tag_object_of(('*', 'locate_datasets', 'Dataset'), 'main', 'attributes')
affk.tag_object_of(('*', 'locate_datasets', 'Dataset'),
                   {'widget': rwdg.RelationFacetWidget()})


class DatasetPublisherFacet(cwfacet.RelationFacet):
    __regid__ = 'datacat.dataset_publisher_facet'
    __select__ = cwfacet.RelationFacet.__select__ & is_instance('Dataset')
    rtype = 'dataset_publisher'
    role = 'subject'
    target_attr = 'name'


class DatasetInCatalogFacet(cwfacet.RelationFacet):
    __regid__ = 'datacat.dataset_in_catalog_facet'
    __select__ = cwfacet.RelationFacet.__select__ & is_instance('Dataset')
    rtype = 'in_catalog'
    role = 'subject'
    target_attr = 'title'


class DatasetIssuedFacet(cwfacet.DateRangeFacet):
    """Facet filtering datasets based on their publication date."""
    __regid__ = 'datacat.dataset_issued_facet'
    __select__ = cwfacet.DateRangeFacet.__select__ & is_instance('Dataset')
    rtype = 'issued'


class DatasetModifiedFacet(cwfacet.DateRangeFacet):
    """Facet filtering datasets based on their modification date."""
    __regid__ = 'datacat.dataset_modified_facet'
    __select__ = cwfacet.DateRangeFacet.__select__ & is_instance('Dataset')
    rtype = 'modified'


class DatasetCatalogBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    """Define DataCatalog / Dataset breadcrumbs"""
    __select__ = (ibreadcrumbs.IBreadCrumbsAdapter.__select__ &
                  has_related_entities('in_catalog', role='subject'))

    def parent_entity(self):
        return self.entity.in_catalog[0]


class DatasetHasDistributionFacet(cwfacet.HasRelationFacet):
    """Facet filtering datasets with a distribution."""
    __regid__ = 'datacat.has_distribution'
    __select__ = cwfacet.HasRelationFacet.__select__ & is_instance('Dataset')
    rtype, role = 'of_dataset', 'object'


class ConceptSchemeUsageFacet(cwfacet.RelationFacet):
    __regid__ = 'datacat.conceptschema_usage_facet'
    __select__ = cwfacet.RelationFacet.__select__ & is_instance('ConceptScheme')
    rtype = 'scheme_relation'
    role = 'subject'
    target_attr = 'name'
    title = _('usage')


# Entity types with a media_type relation

@ajaxcontroller.ajaxfunc(output_type='json')
def get_mediattypes(self):
    return search_in_scheme(
        self._cw, 'http://www.iana.org/assignments/media-types/media-types.xml')


affk.tag_subject_of(
    ('*', 'media_type', 'Concept'),
    {'widget': _autocomplete_widget(
        'get_mediattypes',
        placeholder=_('e.g. text/csv, image/gif, application/octet-stream, etc.'))
     },
)


# Distribution

class DistributionBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    """Define Dataset / Distribution breadcrumbs"""
    __select__ = (ibreadcrumbs.IBreadCrumbsAdapter.__select__ &
                  has_related_entities('of_dataset', role='subject'))

    def parent_entity(self):
        return self.entity.of_dataset[0]


pvs.tag_attribute(('Distribution', 'title'), 'hidden')
affk.set_field_kwargs('Distribution', 'title', widget=fw.TextInput({'size': 82}))
afs.tag_object_of(('*', 'file_distribution', 'Distribution'), 'main', 'inlined')
abaa.tag_object_of(('*', 'file_distribution', 'Distribution'), True)
afs.tag_attribute(('Distribution', 'byte_size'), 'main', 'hidden')
afs.tag_attribute(('Distribution', 'download_url'), 'main', 'hidden')
afs.tag_attribute(('Distribution', 'issued'), 'main', 'hidden')
afs.tag_attribute(('Distribution', 'modified'), 'main', 'hidden')
pvs.tag_subject_of(('Distribution', 'license', '*'), 'attributes')
pvdc.tag_subject_of(('Distribution', 'license', '*'), {'vid': 'incontext'})
pvs.tag_subject_of(('Distribution', 'media_type', '*'), 'attributes')
pvs.tag_subject_of(('Distribution', 'distribution_format', '*'), 'attributes')
afs.tag_subject_of(('Distribution', 'license', '*'), 'main', 'inlined')
affk.tag_subject_of(
    ('Distribution', 'distribution_format', 'Concept'),
    {'widget': _autocomplete_widget(
        'get_filetypes', placeholder=_('e.g. CSV, PNG, etc.'))}
)
afs.tag_subject_of(('Distribution', 'license', 'Concept'), 'main', 'attributes')


@ajaxcontroller.ajaxfunc(output_type='json')
def get_filetypes(self):
    return search_in_scheme(
        self._cw, 'http://publications.europa.eu/resource/authority/file-type')


pvs.tag_attribute(('Distribution', 'access_url'), 'hidden')
afs.tag_attribute(('Distribution', 'access_url'), 'main', 'hidden')
pvs.tag_attribute(('Distribution', 'download_url'), 'hidden')
afs.tag_attribute(('Distribution', 'download_url'), 'main', 'hidden')
pvs.tag_subject_of(('Distribution', 'of_dataset', '*'), 'hidden')
afs.tag_subject_of(('Distribution', 'of_dataset', '*'), 'main', 'hidden')
pvs.tag_subject_of(('Distribution', 'distribution_format', '*'), 'attributes')
afs.tag_subject_of(('Distribution', 'distribution_format', '*'), 'main', 'attributes')
pvs.tag_subject_of(('Distribution', 'media_type', '*'), 'attributes')
afs.tag_subject_of(('Distribution', 'media_type', '*'), 'main', 'attributes')
pvs.tag_attribute(('Distribution', 'issued'), 'hidden')
afs.tag_attribute(('Distribution', 'issued'), 'main', 'hidden')
pvs.tag_attribute(('Distribution', 'modified'), 'hidden')
afs.tag_attribute(('Distribution', 'modified'), 'main', 'hidden')
pvs.tag_attribute(('Distribution', 'byte_size'), 'hidden')
afs.tag_attribute(('Distribution', 'byte_size'), 'main', 'hidden')

# XXX does not work except in creation mode.
distr_afs = build_selectable_uicfg(afs, has_related_entities('file_distribution'))
distr_afs.tag_attribute(('File', 'title'), 'main', 'hidden')
distr_afs.tag_attribute(('File', 'description'), 'main', 'hidden')

# ResourceFeed
pvdc.tag_attribute(('ResourceFeed', 'url'), {'vid': 'urlattr'})
pvs.tag_attribute(('ResourceFeed', 'title'), 'hidden')
pvs.tag_subject_of(('ResourceFeed', 'resource_feed_of', '*'), 'hidden')
affk.set_field_kwargs('ResourceFeed', 'title', widget=fw.TextInput({'size': 82}))
affk.set_field_kwargs('ResourceFeed', 'url', widget=fw.TextInput({'size': 82}))
afs.tag_subject_of(('ResourceFeed', 'resource_feed_of', '*'), 'main', 'hidden')
pvs.tag_subject_of(('ResourceFeed', 'media_type', '*'), 'attributes')
afs.tag_subject_of(('ResourceFeed', 'media_type', '*'), 'main', 'attributes')
# No reledit for `media_type` relation since this cannot handle coupling with
# script form field.
pvdc.tag_subject_of(('ResourceFeed', 'media_type', '*'), {'vid': 'incontext'})
affk.set_fields_order('ResourceFeed',
                      ('title', 'url', 'media_type', 'validation_script',
                       'transformation_script'))
pvdc.tag_subject_of(('ResourceFeed', 'media_type', '*'), {'order': 2})
pvdc.tag_subject_of(('ResourceFeed', 'validation_script', '*'), {'order': 3})
pvdc.tag_subject_of(('ResourceFeed', 'transformation_script', '*'), {'order': 4})
pvs.tag_object_of(('*', 'process_for_resourcefeed', 'ResourceFeed'), 'hidden')
afs.tag_object_of(('*', 'process_for_resourcefeed', 'ResourceFeed'), 'main', 'hidden')
afs.tag_subject_of(('ResourceFeed', 'resource_feed_source', '*'),
                   'main', 'hidden')
abaa.tag_object_of(('*', 'process_for_resourcefeed', 'ResourceFeed'), False)


class ResourceFeedMediaTypeMasterWidget(fw.LazyRestrictedAutoCompletionWidget):
    """Custom widget that controls the content of "dependent" widgets."""
    needs_js = fw.LazyRestrictedAutoCompletionWidget.needs_js + ('cubes.datacat.js', )

    def render(self, form, field, renderer=None):
        master_domid = field.dom_id(form)
        dependent_info = dict(
            (etype, form.field_by_name(rtype, 'subject').dom_id(form))
            for etype, rtype in [('ValidationScript', 'validation_script'),
                                 ('TransformationScript', 'transformation_script')]
        )
        form._cw.add_onload(js.cw.cubes.datacat.initDependentFormField(
            master_domid, dependent_info))
        return super(ResourceFeedMediaTypeMasterWidget, self).render(form, field, renderer)


def script_choice(etype, form, field):
    """Vocabulary function grouping entities of type `etype` choices by
    media_type.
    """
    req = form._cw
    rset = req.execute('Any X,N,C,LL WHERE X is {0}, X name N, X media_type C,'
                       ' C preferred_label L, L label LL'.format(etype))
    vdict = {}
    for script_eid, script_name, mtype_eid, mtype in rset:
        vdict.setdefault((mtype_eid, mtype), []).append(
            (script_name, str(script_eid)))
    vocab = [(u'', '')]
    for (mtype_eid, mtype), values in vdict.iteritems():
        optgroup_id = '{0}_mediatype_{1}'.format(
            etype.lower(), mtype.replace('/', '-'))
        vocab.append((mtype, None, {'id': optgroup_id}))
        vocab.extend(values)
    return vocab


for etype, rtype in [('ValidationScript', 'validation_script'),
                     ('TransformationScript', 'transformation_script')]:
    afs.tag_subject_of(('ResourceFeed', rtype, '*'), 'main', 'attributes')
    affk.tag_subject_of(('ResourceFeed', rtype, '*'),
                        {'choices': partial(script_choice, etype),
                         'sort': False})


class CWSourceBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    """Define ResourceFeed / CWSource breadcrumbs"""
    __select__ = (ibreadcrumbs.IBreadCrumbsAdapter.__select__ &
                  has_related_entities('resource_feed_source', role='object'))

    def parent_entity(self):
        return self.entity.reverse_resource_feed_source[0]


class ResourceFeedBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    """Define Dataset / ResourceFeed breadcrumbs"""
    __select__ = (ibreadcrumbs.IBreadCrumbsAdapter.__select__ &
                  has_related_entities('resource_feed_of', role='subject'))

    def parent_entity(self):
        """The Dataset"""
        return self.entity.resource_feed_of[0]


class DataProcessInResourceFeedCtxComponent(component.EntityCtxComponent):
    """Display data processes in ResourceFeed primary view"""
    __regid__ = 'datacat.resourcefeed-dataprocess'
    __select__ = (component.EntityCtxComponent.__select__ &
                  is_instance('ResourceFeed') &
                  has_related_entities('process_for_resourcefeed',
                                       role='object'))
    title = _('Data processes')
    context = 'navcontentbottom'

    def render_body(self, w):
        rset = self._cw.execute(
            'Any P,CD,S,I,E,D ORDERBY CD DESC LIMIT 10 WHERE'
            ' P process_for_resourcefeed X,'
            ' P process_input_file I,'
            ' P in_state S,'
            ' D? process_depends_on P,'
            ' P creation_date CD,'
            ' P process_stderr E?,'
            ' X eid %(eid)s',
            {'eid': self.entity.eid})
        if rset:
            w(self._cw.view('table', rset=rset))
        rset = self._cw.execute(
            'Any P,CD,S,I,E,D ORDERBY CD DESC LIMIT 10 WHERE'
            ' P process_for_resourcefeed X,'
            ' P process_input_file I,'
            ' P in_state S,'
            ' P process_depends_on D?,'
            ' P creation_date CD,'
            ' P process_stderr E?,'
            ' X eid %(eid)s',
            {'eid': self.entity.eid})
        if rset:
            w(self._cw.view('table', rset=rset))


class ResourceFeedCleanProcessesAction(action.Action):
    __regid__ = 'datacat.clean-resourcefeed-process-logs'
    __select__ = (action.Action.__select__ & match_user_groups('managers')
                  & one_line_rset()
                  & has_related_entities('process_for_resourcefeed', role='object'))

    title = _('cleanup process logs')
    category = 'moreactions'

    def url(self):
        entity = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        return entity.absolute_url(vid=self.__regid__)


class ResourceFeedCleanProcessesView(EntityView):
    __regid__ = 'datacat.clean-resourcefeed-process-logs'
    __select__ = (EntityView.__select__ & match_user_groups('managers')
                  & one_line_rset()
                  & has_related_entities('process_for_resourcefeed', role='object'))

    def entity_call(self, entity):
        deleted = self._cw.call_service(self.__regid__, eid=entity.eid)
        msg = self._cw._('Number of log files is below specified limit')
        if deleted:
            if deleted == 1:
                msg = self._cw._('Most ancient process log file deleted')
            else:
                msg = self._cw._('%d most ancient process log files deleted'
                                 % len(deleted))
        raise Redirect(entity.absolute_url(__message=msg))


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__,
                      [NoPreviewIDownloadablePrimaryView])
    vreg.register_and_replace(NoPreviewIDownloadablePrimaryView,
                              idownloadable.IDownloadablePrimaryView)
