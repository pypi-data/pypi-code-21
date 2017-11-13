"""cubicweb-datacat unit tests for entities"""

import datetime

from cubicweb.devtools import (
    PostgresApptestConfiguration,
    testlib,
    startpgcluster,
    stoppgcluster,
)

from cubes.skos import rdfio

import utils


def setUpModule():
    startpgcluster(__file__)


def tearDownModule():
    stoppgcluster(__file__)


class RDFAdapterTC(testlib.CubicWebTC):
    """Test case for RDF data export."""

    configcls = PostgresApptestConfiguration

    def setup_database(self):
        with self.admin_access.repo_cnx() as cnx:
            lic_scheme = cnx.create_entity('ConceptScheme', cwuri=u'http://publications.europa.eu/'
                                           'resource/authority/licence')
            cnx.execute('SET CS scheme_relation RT WHERE CS eid %(cs)s, RT name %(rt)s',
                        {'cs': lic_scheme.eid, 'rt': 'license_type'})
            scheme = cnx.create_entity('ConceptScheme', cwuri=u'http://example.org/scheme')
            nat_concept = scheme.add_concept(u'National authority')
            attribution_concept = scheme.add_concept(u'Attribution')
            annual_concept = scheme.add_concept(u'Annual')
            csv_concept = scheme.add_concept(u'CSV')
            xls_concept = scheme.add_concept(u'Excel XLS')
            appxls_concept = scheme.add_concept(u'application/vnd.ms-excel')
            zip_concept = scheme.add_concept(u'ZIP')
            mediatypes_scheme = cnx.create_entity(
                'ConceptScheme',
                cwuri=u'http://www.iana.org/assignments/media-types/media-types.xml')
            appzip_concept = mediatypes_scheme.add_concept(u'application/zip')
            eng_concept = scheme.add_concept(u'English')
            edu_concept = scheme.add_concept(u'Education, culture and sport')
            publisher = cnx.create_entity('Agent', name=u'The Publisher',
                                          publisher_type=nat_concept,
                                          email=u'publisher@example.org')
            contact = cnx.create_entity('Agent', name=u'The Contact Point',
                                        email=u'contact@example.org')
            license = cnx.create_entity('Concept', in_scheme=lic_scheme,
                                        cwuri=u'http://creativecommons.org/licenses/by/3.0',
                                        license_type=attribution_concept)
            cnx.create_entity('Label', label_of=license, kind=u"preferred",
                              label=u'Creative Commons Attribution')
            cat = cnx.create_entity('DataCatalog', title=u'My Catalog',
                                    description=u'A nice catalog', catalog_publisher=publisher,
                                    homepage=u'http://cat.example.org', language=eng_concept,
                                    theme_taxonomy=scheme, license=license,
                                    issued=datetime.datetime(2016, 02, 01, 20, 40, 00),
                                    modified=datetime.datetime(2016, 02, 02, 18, 25, 00))
            ds = cnx.create_entity('Dataset', title=u'First Dataset', description=u'A nice datacat',
                                   in_catalog=cat, dataset_publisher=publisher,
                                   dataset_contact_point=contact, keyword=u'keyword',
                                   dataset_frequency=annual_concept, dcat_theme=edu_concept)
            dist1 = cnx.create_entity('Distribution', title=u'First Dataset (CSV)',
                                      description=u'First Dataset in CSV format', of_dataset=ds,
                                      license=license, distribution_format=csv_concept,
                                      access_url=u'http://www.example.org')
            dist2 = cnx.create_entity('Distribution', title=u'First Dataset (XLS)',
                                      description=u'First Dataset in XLS format', of_dataset=ds,
                                      license=license, distribution_format=xls_concept,
                                      media_type=appxls_concept)
            dist3 = cnx.create_entity('Distribution', title=u'First Dataset (ZIP)',
                                      description=u'First Dataset in ZIP format', of_dataset=ds,
                                      license=license, distribution_format=zip_concept)
            # Add a file to dist3 with a long 'data_name' (should be truncated
            # on export) and a data_format which should be bound to
            # distribution's media type.
            utils.create_file(
                cnx, b'zip zip zip', data_name=u'a' * 60 + '.zip',
                data_format=u'application/zip', file_distribution=dist3)
            cnx.commit()
            self.cat_eid = cat.eid
            self.ds_eid = ds.eid
            self.dist1_eid = dist1.eid
            self.dist2_eid = dist2.eid
            self.dist3_eid = dist3.eid
            self.publisher_eid = publisher.eid
            self.contact_eid = contact.eid
            self.license_eid = license.eid
            self.nat_concept_uri = nat_concept.cwuri
            self.attribution_concept_uri = attribution_concept.cwuri
            self.annual_concept_uri = annual_concept.cwuri
            self.csv_concept_uri = csv_concept.cwuri
            self.xls_concept_uri = xls_concept.cwuri
            self.appxls_concept_uri = appxls_concept.cwuri
            self.zip_concept_uri = zip_concept.cwuri
            self.appzip_concept_uri = appzip_concept.cwuri
            self.eng_concept_uri = eng_concept.cwuri
            self.theme_scheme_uri = scheme.cwuri
            self.edu_concept_uri = edu_concept.cwuri

    def test_rdf_export_catalog(self):
        """Check that we get expected RDF data when exporting a catalog."""
        with self.admin_access.repo_cnx() as cnx:
            cat = cnx.entity_from_eid(self.cat_eid)
            publisher = cnx.entity_from_eid(self.publisher_eid)
            cat_uri = rdfio.permanent_url(cat)
            rdfcat = cat.cw_adapt_to('RDFPrimary')
            graph = rdfio.default_graph()
            rdfcat.fill(graph)
            self._check_literal_property(graph,
                                         cat_uri, 'http://purl.org/dc/terms/title', u'My Catalog')
            self._check_uri_property(graph, cat_uri, 'http://purl.org/dc/terms/publisher',
                                     rdfio.permanent_url(publisher))
            self._check_uri_property(graph, cat_uri, 'http://xmlns.com/foaf/0.1/homepage',
                                     'http://cat.example.org')
            self._check_uri_property(graph, cat_uri, 'http://purl.org/dc/terms/language',
                                     self.eng_concept_uri)
            self._check_uri_property(graph, cat_uri, 'http://www.w3.org/ns/dcat#themeTaxonomy',
                                     self.theme_scheme_uri)
            self._check_literal_property(graph, rdfio.permanent_url(publisher),
                                         'http://xmlns.com/foaf/0.1/name',
                                         u'The Publisher')

    def test_rdf_export_dataset(self):
        """Check that we get expected RDF data when exporting a dataset."""
        with self.admin_access.repo_cnx() as cnx:
            ds = cnx.entity_from_eid(self.ds_eid)
            publisher = cnx.entity_from_eid(self.publisher_eid)
            contact = cnx.entity_from_eid(self.contact_eid)
            ds_uri = rdfio.permanent_url(ds)
            rdfds = ds.cw_adapt_to('RDFPrimary')
            graph = rdfio.default_graph()
            rdfds.fill(graph)
            self._check_literal_property(graph,
                                         ds_uri, 'http://purl.org/dc/terms/title', u'First Dataset')
            self._check_literal_property(graph,
                                         ds_uri, 'http://www.w3.org/ns/dcat#keyword',
                                         u'keyword')
            self._check_uri_property(graph, ds_uri, 'http://purl.org/dc/terms/publisher',
                                     rdfio.permanent_url(publisher))
            self._check_uri_property(graph, ds_uri, 'http://www.w3.org/ns/dcat#contactPoint',
                                     rdfio.permanent_url(contact))
            self._check_uri_property(graph, ds_uri, 'http://purl.org/dc/terms/accrualPeriodicity',
                                     self.annual_concept_uri)
            self._check_uri_property(graph, ds_uri, 'http://www.w3.org/ns/dcat#theme',
                                     self.edu_concept_uri)

    def test_rdf_export_distribution(self):
        """Check that we get expected RDF data when exporting a distribution."""
        with self.admin_access.repo_cnx() as cnx:
            for dist_eid, title, filetype, mediatype in [
                (self.dist1_eid, u'First Dataset (CSV)', self.csv_concept_uri, None),
                (self.dist2_eid, u'First Dataset (XLS)', self.xls_concept_uri,
                 self.appxls_concept_uri),
                (self.dist3_eid, u'First Dataset (ZIP)', self.zip_concept_uri,
                 self.appzip_concept_uri),
            ]:
                dist = cnx.entity_from_eid(dist_eid)
                license_uri = rdfio.permanent_url(cnx.entity_from_eid(self.license_eid))
                dist_uri = rdfio.permanent_url(dist)
                rdfdist = dist.cw_adapt_to('RDFPrimary')
                graph = rdfio.default_graph()
                rdfdist.fill(graph)
                self._check_literal_property(graph, dist_uri, 'http://purl.org/dc/terms/title',
                                             title)
                if title == u'First Dataset (CSV)':
                    self._check_uri_property(graph, dist_uri, 'http://purl.org/dc/terms/license',
                                             license_uri)
                    self._check_uri_property(graph, license_uri,
                                             'http://purl.org/dc/terms/type',
                                             self.attribution_concept_uri)
                    self._check_uri_property(graph, license_uri,
                                             'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
                                             'http://purl.org/dc/terms/LicenseDocument')
                    self._check_literal_property(graph, license_uri,
                                                 'http://purl.org/dc/terms/title',
                                                 u'Creative Commons Attribution')
                if filetype is not None:
                    self._check_uri_property(graph, dist_uri, 'http://purl.org/dc/terms/format',
                                             filetype)
                if mediatype is not None:
                    self._check_uri_property(graph, dist_uri, 'http://www.w3.org/ns/dcat#mediaType',
                                             mediatype)
                if title == u'First Dataset (ZIP)':
                    truncated_name = u'a' * 50 + '.zip'
                    access_url = 'http://testing.fr/cubicweb/distribution/{}/raw/{}'.format(
                        self.dist3_eid, truncated_name)
                    self._check_uri_property(graph, dist_uri, 'http://www.w3.org/ns/dcat#accessURL',
                                             access_url)
                if title == u'First Dataset (XLS)':
                    self._check_uri_property(graph, dist_uri, 'http://www.w3.org/ns/dcat#accessURL',
                                             dist_uri)

    def test_rdf_export_publisher(self):
        """Check that we get expected RDF data when exporting a publisher."""
        with self.admin_access.repo_cnx() as cnx:
            publisher = cnx.entity_from_eid(self.publisher_eid)
            publisher_uri = rdfio.permanent_url(publisher)
            rdfpub = publisher.cw_adapt_to('RDFPrimary')
            graph = rdfio.default_graph()
            rdfpub.fill(graph)
            self._check_literal_property(graph, publisher_uri, 'http://xmlns.com/foaf/0.1/name',
                                         u'The Publisher')
            self._check_literal_property(graph, publisher_uri, 'http://xmlns.com/foaf/0.1/mbox',
                                         u'mailto:publisher@example.org')
            self._check_uri_property(graph, publisher_uri, 'http://purl.org/dc/terms/type',
                                     self.nat_concept_uri)

    def test_rdf_export_contact_point(self):
        """Check that we get expected RDF data when exporting a contact point."""
        with self.admin_access.repo_cnx() as cnx:
            contact = cnx.entity_from_eid(self.contact_eid)
            contact_uri = rdfio.permanent_url(contact)
            rdfcontact = contact.cw_adapt_to('RDFContactPoint')
            graph = rdfio.default_graph()
            rdfcontact.fill(graph)
            self._check_literal_property(graph, contact_uri, 'http://www.w3.org/2006/vcard/ns#fn',
                                         u'The Contact Point')
            self._check_literal_property(graph, contact_uri,
                                         'http://www.w3.org/2006/vcard/ns#hasEmail',
                                         u'mailto:contact@example.org')

    def _check_literal_property(self, graph, subject_uri, rdf_property, expected_value):
        """Check that, in the given graph, `subject_uri` has the expected value for the
        `dcterms:title` property."""
        self.assertEqual(list(graph.objects(subject_uri, graph.uri(rdf_property))),
                         [expected_value])

    def _check_uri_property(self, graph, subject_uri, rdf_property, expected_uri):
        """Check that, in the given graph, `subject_uri` is related via `rdf_property` to a
        `foaf:Agent` with expected URI."""
        self.assertEqual(list(graph.objects(subject_uri, graph.uri(rdf_property))), [expected_uri])


if __name__ == '__main__':
    import unittest
    unittest.main()
