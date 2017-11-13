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

"""cubicweb-datacat entity's classes"""

from os import path

import rdflib

from cubicweb.predicates import (
    has_related_entities,
    is_instance,
)
from cubicweb.entities import (
    adapters,
    AnyEntity,
)

from cubes.datacat import (
    register_catalog_rdf_mapping,
    register_contact_point_rdf_mapping,
    register_dataset_rdf_mapping,
    register_distribution_rdf_mapping,
    register_periodoftime_rdf_mapping,
    register_publisher_rdf_mapping,
)
from cubes.file.entities import FileIDownloadableAdapter
from cubes.skos.entities import AbstractRDFAdapter
from cubes.skos import rdfio


class Agent(AnyEntity):
    __regid__ = 'Agent'

    def dc_title(self):
        """Return a dc_title built from name and email"""
        title = self.name
        if self.email:
            title += ' <%s>' % self.email
        return title


class Dataset(AnyEntity):
    __regid__ = 'Dataset'

    def dc_title(self):
        """dc_title is either the title or the identifier"""
        return self.title or self.identifier

    @property
    def contact_point(self):
        """Contact point of this Dataset"""
        if self.dataset_contact_point:
            return self.dataset_contact_point[0]


class PeriodOfTime(AnyEntity):
    __regid__ = 'PeriodOfTime'

    def dc_title(self):
        return u'{} - {}'.format(
            self.printable_value('start'), self.printable_value('end'))


class Distribution(AnyEntity):
    __regid__ = 'Distribution'

    def dc_title(self):
        if self.title:
            return self.title
        elif self.reverse_file_distribution:
            return self.reverse_file_distribution[0].dc_title()
        else:
            return u'{0} #{1}'.format(self.cw_etype, self.eid)


class DownloadableDistributionFile(FileIDownloadableAdapter):

    __select__ = (FileIDownloadableAdapter.__select__
                  & has_related_entities('file_distribution', role='subject'))

    def download_file_name(self):
        name, ext = path.splitext(self.entity.data_name)
        return name[:50] + ext


class DownloadableDistribution(adapters.IDownloadableAdapter):
    """IDownloadable adapter for Distribution entities related to a File."""

    __select__ = (adapters.IDownloadableAdapter.__select__ &
                  has_related_entities('file_distribution', role='object'))

    @property
    def downloadable_file(self):
        """The IDownloadable adapted distribution file."""
        dfile = self.entity.reverse_file_distribution[0]
        return dfile.cw_adapt_to('IDownloadable')

    def download_url(self, **kwargs):
        name = self._cw.url_quote(self.download_file_name())
        path = '%s/raw/%s' % (self.entity.rest_path(), name)
        return self._cw.build_url(path, **kwargs)

    def download_content_type(self):
        return self.downloadable_file.download_content_type()

    def download_encoding(self):
        return self.downloadable_file.download_encoding()

    def download_file_name(self):
        return self.downloadable_file.download_file_name()

    def download_data(self):
        return self.downloadable_file.download_data()


class ResourceFeed(AnyEntity):
    __regid__ = 'ResourceFeed'

    @property
    def dataset(self):
        """The Dataset using this ResourceFeed."""
        return self.resource_feed_of[0]

    @property
    def data_format(self):
        return self.media_type[0].label()


class TransformationScript(AnyEntity):
    __regid__ = 'TransformationScript'

    @property
    def output_format(self):
        if self.output_media_type:
            return self.output_media_type[0].label()

    @property
    def transformation_sequence(self):
        return self.reverse_step_script[0].in_sequence[0]


#
# Adapters
#

# Export to RDF

def license_rdf_uri(license):
    """Return the URI to be used as license RDF identifier."""
    exact_matches = license.exact_match
    if exact_matches and exact_matches[0].cw_etype == 'ExternalUri':
        return exact_matches[0].uri
    else:
        return rdfio.permanent_url(license)


def fill_graph_with(entity, graph, adapterid):
    """Fill a `graph` using `entity` adaped as `adapterid`."""
    filler = entity.cw_adapt_to(adapterid)
    assert filler, '{0} not adaptable as {1}'.format(entity, adapterid)
    filler.fill(graph)


def add_literal_to_graph(subject_s_uri, property_s_uri, value, graph):
    """Add the following triple to RDF graph: ``(subject_s_uri, property_s_uri, value).``"""
    if value is not None:
        graph.add(graph.uri(subject_s_uri), graph.uri(property_s_uri), value)


def add_uri_to_graph(subject_s_uri, property_s_uri, object_s_uri, graph):
    """Add the following triple to RDF graph: ``(subject_s_uri, property_s_uri, object_s_uri)``."""
    graph.add(graph.uri(subject_s_uri), graph.uri(property_s_uri), graph.uri(object_s_uri))


def add_license_to_graph(license, subject_uri, graph, reg):
    """Add license information to RDF graph for `subject_uri`."""
    reg.register_prefix('rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
    license_uri = license_rdf_uri(license)
    add_uri_to_graph(subject_uri, reg.normalize_uri('dcterms:license'), license_uri, graph)
    add_uri_to_graph(license_uri, reg.normalize_uri('rdf:type'),
                     reg.normalize_uri('dcterms:LicenseDocument'), graph)
    add_literal_to_graph(license_uri, reg.normalize_uri('dcterms:title'),
                         license.label(language_code=license._cw.lang), graph)
    if license.license_type:
        concept = license.license_type[0]
        add_concept_to_graph(concept, license_uri, 'dcterms:type', graph, reg)


def add_checksum_to_graph(checksum_value, subject_uri, graph, reg):
    """Add a spdx:Checksum related to `subject_uri` through spdx:checksum.

    spdx:algorithm is fixed to checksumAlgorithm_sha1 as this is currently the
    only supported value per DCAT-AP.
    """
    reg.register_prefix('spdx', 'http://spdx.org/rdf/terms#')
    # Set a predictable but unique identifier for spdx:Checksum blank node.
    checksum = rdflib.BNode('/'.join([subject_uri, checksum_value]))
    add_uri_to_graph(subject_uri, reg.normalize_uri('spdx:checksum'),
                     checksum, graph)
    add_uri_to_graph(checksum, reg.normalize_uri('rdf:type'),
                     reg.normalize_uri('spdx:Checksum'), graph)
    add_literal_to_graph(checksum, reg.normalize_uri('spdx:checksumValue'),
                         checksum_value, graph)
    add_uri_to_graph(checksum, reg.normalize_uri('spdx:algorithm'),
                     reg.normalize_uri('spdx:checksumAlgorithm_sha1'),
                     graph)


def graph_add_concept_as(graph, reg, concept, subject_uri, rdf_property, as_type):
    """Add `concept` as an rdf:type `as_type` to graph related to
    `subject_uri` through `rdf_property`.
    """
    reg.register_prefix('rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
    object_uri = concept.cwuri
    add_uri_to_graph(subject_uri, reg.normalize_uri(rdf_property), object_uri,
                     graph)
    add_uri_to_graph(object_uri, reg.normalize_uri('rdf:type'),
                     reg.normalize_uri(as_type), graph)
    add_literal_to_graph(object_uri, reg.normalize_uri('rdf:value'),
                         concept.label(), graph)


def add_concept_scheme_to_graph(concept_scheme, graph, reg):
    """Add concept scheme to RDF graph related to `subject_uri` with 'relation_uri'."""
    reg.register_prefix('rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
    reg.register_prefix('skos', 'http://www.w3.org/2004/02/skos/core#')
    reg.register_prefix('dcterms', 'http://purl.org/dc/terms/')
    scheme_uri = concept_scheme.cwuri
    add_uri_to_graph(scheme_uri, reg.normalize_uri('rdf:type'),
                     reg.normalize_uri('skos:ConceptScheme'), graph)
    add_literal_to_graph(scheme_uri, reg.normalize_uri('dcterms:title'), concept_scheme.title,
                         graph)


def add_concept_to_graph(concept, subject_uri, relation_uri, graph, reg):
    """Add concept to RDF graph related to `subject_uri` with 'relation_uri'."""
    reg.register_prefix('rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
    reg.register_prefix('skos', 'http://www.w3.org/2004/02/skos/core#')
    concept_uri = concept.cwuri
    add_uri_to_graph(subject_uri, reg.normalize_uri(relation_uri), concept_uri, graph)
    add_uri_to_graph(concept_uri, reg.normalize_uri('rdf:type'), reg.normalize_uri('skos:Concept'),
                     graph)
    add_uri_to_graph(concept_uri, reg.normalize_uri('skos:inScheme'), concept.in_scheme[0].cwuri,
                     graph)
    for label in concept.preferred_label:
        add_literal_to_graph(concept_uri, reg.normalize_uri('skos:prefLabel'),
                             rdfio.unicode_with_language(label.label, label.language_code), graph)


def add_concept_literal_to_graph(concept, subject_uri, relation_uri, graph, reg):
    """Add concept's label to RDF graph related to `subject_uri` with 'relation_uri'."""
    reg.register_prefix('rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
    reg.register_prefix('skos', 'http://www.w3.org/2004/02/skos/core#')
    label = concept.label(language_code=concept._cw.lang)
    add_literal_to_graph(subject_uri, reg.normalize_uri(relation_uri), label, graph)


class DataCatalogRDFAdapter(AbstractRDFAdapter):
    """Adapt DataCatalog entities to RDF using DCAT vocabulary."""
    __regid__ = 'RDFPrimary'
    __select__ = AbstractRDFAdapter.__select__ & is_instance('DataCatalog')

    register_rdf_mapping = staticmethod(register_catalog_rdf_mapping)

    def fill(self, graph):
        super(DataCatalogRDFAdapter, self).fill(graph)
        reg = self.registry
        reg.register_prefix('foaf', 'http://xmlns.com/foaf/0.1/')
        catalog_uri = rdfio.permanent_url(self.entity)
        for agent in self.entity.catalog_publisher:
            fill_graph_with(agent, graph, self.__regid__)
        # Export license.
        for license in self.entity.license:
            add_license_to_graph(license, catalog_uri, graph, reg)
        # Export homepage attribute as an RDF resource
        if self.entity.homepage:
            add_uri_to_graph(catalog_uri, reg.normalize_uri('foaf:homepage'), self.entity.homepage,
                             graph)
        # Export languages
        for language in self.entity.language:
            fill_graph_with(language, graph, self.__regid__)
            graph_add_concept_as(graph, reg, language, catalog_uri,
                                 'dcterms:language', 'dcterms:LinguisticSystem')
        # Export concept scheme
        for scheme in self.entity.theme_taxonomy:
            add_concept_scheme_to_graph(scheme, graph, reg)
            add_uri_to_graph(catalog_uri, reg.normalize_uri('dcat:themeTaxonomy'), scheme.cwuri,
                             graph)
        # Export locations
        for location in self.entity.spatial_coverage:
            fill_graph_with(location, graph, self.__regid__)
            graph_add_concept_as(graph, reg, location, catalog_uri,
                                 'dcterms:spatial', 'dcterms:Location')


class DatasetRDFAdapter(AbstractRDFAdapter):
    """Adapt Dataset entities to RDF using DCAT vocabulary."""
    __regid__ = 'RDFPrimary'
    __select__ = AbstractRDFAdapter.__select__ & is_instance('Dataset')

    register_rdf_mapping = staticmethod(register_dataset_rdf_mapping)

    def fill(self, graph):
        super(DatasetRDFAdapter, self).fill(graph)
        reg = self.registry
        dataset_uri = rdfio.permanent_url(self.entity)
        # Export comma-separated keyword attribute as multiple RDF resources
        if self.entity.keyword:
            for keyword in self.entity.keyword.split(u','):
                add_literal_to_graph(dataset_uri, reg.normalize_uri('dcat:keyword'),
                                     keyword.strip(), graph)
        # dct:accrualPeriodicity.
        reg.register_prefix('rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
        for concept in self.entity.dataset_frequency:
            frequency_uri = concept.cwuri
            add_uri_to_graph(dataset_uri, reg.normalize_uri('dcterms:accrualPeriodicity'),
                             frequency_uri, graph)
            add_uri_to_graph(frequency_uri, reg.normalize_uri('rdf:type'),
                             reg.normalize_uri('dcterms:Frequency'), graph)
            add_literal_to_graph(frequency_uri, reg.normalize_uri('rdf:value'), concept.label(),
                                 graph)
        # dct:type
        if self.entity.dataset_type:
            dtype = self.entity.dataset_type[0]
            add_concept_to_graph(dtype, dataset_uri, 'dcterms:type', graph, reg)
        # dcat:theme
        for concept in self.entity.dcat_theme:
            add_concept_to_graph(concept, dataset_uri, 'dcat:theme', graph, reg)
        # dct:spatial
        for location in self.entity.spatial_coverage:
            fill_graph_with(location, graph, self.__regid__)
            graph_add_concept_as(graph, reg, location, dataset_uri,
                                 'dcterms:spatial', 'dcterms:Location')


class DistributionRDFAdapter(AbstractRDFAdapter):
    """Adapt Distribution entities to RDF using DCAT vocabulary."""
    __regid__ = 'RDFPrimary'
    __select__ = AbstractRDFAdapter.__select__ & is_instance('Distribution')

    register_rdf_mapping = staticmethod(register_distribution_rdf_mapping)

    def fill(self, graph):
        super(DistributionRDFAdapter, self).fill(graph)
        reg = self.registry
        distribution_uri = rdfio.permanent_url(self.entity)
        # Export access_url and download_url attributes as an RDF resource
        access_url = self.entity.access_url
        if access_url is None:
            downloadable = self.entity.cw_adapt_to('IDownloadable')
            if downloadable:
                # Distribution has a File related.
                access_url = downloadable.download_url()
            else:
                # Fall back to Distribution's URI.
                access_url = rdfio.permanent_url(self.entity)
        add_uri_to_graph(distribution_uri, reg.normalize_uri('dcat:accessURL'),
                         access_url, graph)
        if self.entity.download_url:
            add_uri_to_graph(distribution_uri, reg.normalize_uri('dcat:downloadURL'),
                             self.entity.download_url, graph)
        # Export license from either the distribution directly or from the
        # catalog if distribution has no license.
        license = None
        if self.entity.license:
            license = self.entity.license[0]
        elif self.entity.catalog_license:
            license = self.entity.catalog_license[0]
        if license is not None:
            add_license_to_graph(license, distribution_uri, graph, reg)
        # Export distribution_format relation if available
        for filetype in self.entity.distribution_format:
            fill_graph_with(filetype, graph, self.__regid__)
            graph_add_concept_as(
                graph, reg, filetype, distribution_uri,
                'dcterms:format', 'dcterms:MediaTypeOrExtent')
        # Export media_type if available
        for mediatype in self.entity.media_type:
            fill_graph_with(mediatype, graph, self.__regid__)
            graph_add_concept_as(
                graph, reg, mediatype, distribution_uri,
                'dcat:mediaType', 'dcterms:MediaTypeOrExtent')
        # Documentation
        if self.entity.documentation:
            reg.register_prefix('foaf', 'http://xmlns.com/foaf/0.1/')
            add_uri_to_graph(distribution_uri, reg.normalize_uri('foaf:page'),
                             self.entity.documentation, graph)
        # Export file's metadata.
        if self.entity.reverse_file_distribution:
            distfile = self.entity.reverse_file_distribution[0]
            sha1hex = distfile.data_sha1hex
            if sha1hex is not None:
                add_checksum_to_graph(sha1hex, distribution_uri, graph, reg)


class PeriodOfTimeRDFAdapter(AbstractRDFAdapter):
    """Adapt PeriodOfTime entities to RDF using DCAT vocabulary."""
    __regid__ = 'RDFPrimary'
    __select__ = AbstractRDFAdapter.__select__ & is_instance('PeriodOfTime')
    register_rdf_mapping = staticmethod(register_periodoftime_rdf_mapping)


class AgentRDFAdapter(AbstractRDFAdapter):
    """Adapt Agent entities to foaf:Agent RDF using FOAF vocabulary."""
    __abstract__ = True

    register_rdf_mapping = staticmethod(register_publisher_rdf_mapping)

    def fill(self, graph):
        super(AgentRDFAdapter, self).fill(graph)
        self.fill_email(graph)

    def fill_email(self, graph):
        raise NotImplementedError()


class PublisherRDFAdapter(AgentRDFAdapter):
    """Adapt publisher Agent entities to foaf:Agent RDF using FOAF vocabulary.
    """
    __regid__ = 'RDFPrimary'
    __select__ = (AgentRDFAdapter.__select__ &
                  (has_related_entities('dataset_publisher', 'object') |
                   has_related_entities('catalog_publisher', 'object')))

    register_rdf_mapping = staticmethod(register_publisher_rdf_mapping)

    def fill(self, graph):
        super(PublisherRDFAdapter, self).fill(graph)
        self.fill_publisher_type(graph)

    def fill_publisher_type(self, graph):
        """Export publisher_type relation and delegate to Concept adapter to
        fill object side of the relation.
        """
        if self.entity.publisher_type:
            concept = self.entity.publisher_type[0]
            add_concept_to_graph(concept, rdfio.permanent_url(self.entity),
                                 'dcterms:type', graph, self.registry)

    def fill_email(self, graph):
        """Export email attribute as a owl:Thing RDF resource"""
        reg = self.registry
        reg.register_prefix('foaf', 'http://xmlns.com/foaf/0.1/')
        if self.entity.email:
            add_uri_to_graph(rdfio.permanent_url(self.entity),
                             reg.normalize_uri('foaf:mbox'),
                             u'mailto:{0}'.format(self.entity.email), graph)


class ContactPointRDFAdapter(AgentRDFAdapter):
    """Adapt Agent entities to vcard:Kind RDF using vCard vocabulary."""
    __regid__ = 'RDFContactPoint'
    __select__ = (AgentRDFAdapter.__select__ &
                  has_related_entities('dataset_contact_point', 'object'))

    register_rdf_mapping = staticmethod(register_contact_point_rdf_mapping)

    def fill_email(self, graph):
        reg = self.registry
        # Export email attribute as a owl:Thing RDF resource
        reg.register_prefix('vcard', 'http://www.w3.org/2006/vcard/ns#')
        if self.entity.email:
            add_uri_to_graph(rdfio.permanent_url(self.entity),
                             reg.normalize_uri('vcard:hasEmail'),
                             u'mailto:{0}'.format(self.entity.email), graph)
