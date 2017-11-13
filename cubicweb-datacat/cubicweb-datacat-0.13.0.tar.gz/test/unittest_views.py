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

"""cubicweb-datacat tests for views"""

from datetime import datetime
import json
from tempfile import NamedTemporaryFile

from mock import patch
from pytz import utc
from rdflib.compare import (
    graph_diff,
    to_isomorphic,
)

from cubicweb import Binary
from cubicweb.devtools import (
    PostgresApptestConfiguration,
    testlib,
    startpgcluster,
    stoppgcluster,
)

from cubes.skos import rdfio
from cubes.datacat.views import dataset_publisher_choices


def setUpModule():
    startpgcluster(__file__)


def tearDownModule():
    stoppgcluster(__file__)


class PublisherChoicesFunctionTC(testlib.CubicWebTC):
    """Test case for cubicweb-datacat dataset publisher choices function."""

    configcls = PostgresApptestConfiguration

    def setup_database(self):
        with self.admin_access.repo_cnx() as cnx:
            pub1 = cnx.create_entity('Agent', name=u'Publisher 1')
            pub2 = cnx.create_entity('Agent', name=u'Publisher 2')
            cat = cnx.create_entity('DataCatalog', title=u'My Catalog',
                                    description=u'A nice catalog', catalog_publisher=pub1)
            cnx.commit()
        self.cat_eid = cat.eid
        self.pub1_eid = pub1.eid
        self.pub2_eid = pub2.eid

    def test_choices_add_dataset_from_catalog(self):
        """Check that publisher list is correct when dataset is created from a catalog."""
        with self.admin_access.web_request() as req:
            req.form['__linkto'] = 'in_catalog:{0}:subject'.format(self.cat_eid)
            dset_class = self.vreg['etypes'].etype_class('Dataset')(req)
            add_form = self.vreg['forms'].select('edition', req, entity=dset_class)
            publisher_field = add_form.field_by_name('dataset_publisher', 'subject')
            self.assertEqual(dataset_publisher_choices(add_form, publisher_field),
                             [(u'Publisher 1', unicode(self.pub1_eid))])

    def test_choices_add_dataset_no_catalog(self):
        """Check that publisher list is correct when dataset is created standalone."""
        with self.admin_access.web_request() as req:
            dset_class = self.vreg['etypes'].etype_class('Dataset')(req)
            add_form = self.vreg['forms'].select('edition', req, entity=dset_class)
            publisher_field = add_form.field_by_name('dataset_publisher', 'subject')
            self.assertEqual(dataset_publisher_choices(add_form, publisher_field),
                             [(u'Publisher 1', unicode(self.pub1_eid)),
                              (u'Publisher 2', unicode(self.pub2_eid))])


def sorted_triples(graph):
    return '\n'.join(sorted(graph.serialize(format='nt').splitlines()))


def conceptscheme(cnx, uri, **kwargs):
    return cnx.create_entity('ConceptScheme', cwuri=uri, **kwargs)


class RDFAdapterTC(testlib.CubicWebTC):
    """Test case for RDF data export."""

    configcls = PostgresApptestConfiguration

    def setup_database(self):
        # patch now() so that computed datetime attributes always return the same datetime
        # See https://docs.python.org/3/library/unittest.mock-examples.html#partial-mocking
        with patch('cubes.datacat.hooks.datetime') as mock_dt:
            mock_dt.now.return_value = datetime(2016, 02, 02, 15, 25, 0, tzinfo=utc)
            mock_dt.side_effect = datetime
            # Now set up entities
            with self.admin_access.repo_cnx() as cnx:
                spatial_scheme = conceptscheme(
                    cnx, u'http://publications.europa.eu/resource/authority/country')
                lic_scheme = conceptscheme(
                    cnx, u'http://publications.europa.eu/resource/authority/licence')
                cnx.execute('SET CS scheme_relation RT WHERE CS eid %(cs)s, RT name %(rt)s',
                            {'cs': lic_scheme.eid, 'rt': 'license_type'})
                scheme = conceptscheme(cnx, u'http://example.org/scheme',
                                       title=u'Concept Scheme')
                nat_concept = scheme.add_concept(u'National authority',
                                                 cwuri=u'http://example.org/national_authority')
                attribution_concept = scheme.add_concept(u'Attribution',
                                                         cwuri=u'http://example.org/attribution')
                annual_concept = scheme.add_concept(u'Annual', cwuri=u'http://example.org/annual')
                csv_concept = scheme.add_concept(u'CSV', cwuri=u'http://example.org/csv')
                xls_concept = scheme.add_concept(u'Excel XLS', cwuri=u'http://example.org/xls')
                appxls_concept = scheme.add_concept(u'application/vnd.ms-excel',
                                                    cwuri=u'http://example.org/application_xls')
                zip_concept = scheme.add_concept(u'ZIP', cwuri=u'http://example.org/zip')
                appzip_concept = scheme.add_concept(u'application/zip',
                                                    cwuri=u'http://example.org/application_zip')
                eng_concept = scheme.add_concept(u'English', cwuri=u'http://example.org/english')
                edu_concept = scheme.add_concept(u'Education, culture and sport',
                                                 cwuri=u'http://example.org/education')
                publisher = cnx.create_entity('Agent', name=u'The Publisher',
                                              publisher_type=nat_concept,
                                              email=u'publisher@example.org',
                                              cwuri=u'http://example.org/publisher')
                contact = cnx.create_entity('Agent', name=u'The Contact Point',
                                            email=u'contact@example.org',
                                            cwuri=u'http://example.org/contact')
                license = cnx.create_entity('Concept', in_scheme=lic_scheme,
                                            license_type=attribution_concept,
                                            cwuri=u'http://example.org/license')
                cnx.create_entity('Label', label_of=license, kind=u"preferred",
                                  label=u'Other (attribution)')
                toulouse = spatial_scheme.add_concept(
                    u'Toulouse', cwuri=u'http://example.org/toulouse')
                parcducanal = spatial_scheme.add_concept(
                    u'Parc tech du canal', cwuri=u'http://example.org/parc-du-canal')
                floor1 = spatial_scheme.add_concept(
                    u'floor 1', cwuri=u'http://example.org/floor1')
                cat = cnx.create_entity('DataCatalog', title=u'My Catalog',
                                        description=u'A nice catalog', catalog_publisher=publisher,
                                        homepage=u'http://cat.example.org', language=eng_concept,
                                        theme_taxonomy=scheme, license=license,
                                        issued=datetime(2016, 02, 01, 20, 40, 0, tzinfo=utc),
                                        modified=datetime(2016, 02, 02, 18, 25, 0, tzinfo=utc),
                                        spatial_coverage=[toulouse, parcducanal],
                                        cwuri=u'http://example.org/catalog')
                dset_type = scheme.add_concept(u'blah', cwuri=u'http://example.org/blah')
                ds = cnx.create_entity('Dataset', title=u'First Dataset', description=u'A dataset',
                                       identifier=u'dataset-1',
                                       landing_page=u'http://www.example.org/dataset-1',
                                       in_catalog=cat, dataset_publisher=publisher,
                                       dataset_contact_point=contact, keyword=u'keyword',
                                       dataset_frequency=annual_concept, dcat_theme=edu_concept,
                                       spatial_coverage=floor1,
                                       dataset_type=dset_type,
                                       cwuri=u'http://example.org/dataset')
                cnx.create_entity(
                    'Location', name=u'somewhere',
                    cwuri=u'http://example.org/location/somewhere',
                    geometry=(u'GEOMETRYCOLLECTION (POINT (2 46))', 4326),
                    locate_datasets=ds)
                cnx.create_entity('PeriodOfTime',
                                  cwuri=u'http://example.org/2012-2013',
                                  start=datetime(2012, 1, 1, tzinfo=utc),
                                  end=datetime(2013, 2, 1, tzinfo=utc),
                                  reverse_temporal_coverage=ds)
                csv_dist = cnx.create_entity(
                    'Distribution', title=u'First Dataset (CSV)',
                    description=u'First Dataset in CSV format',
                    of_dataset=ds, license=license,
                    distribution_format=csv_concept,
                    cwuri=u'http://example.org/dataset/csv')

                with cnx.security_enabled(write=False):
                    # by-pass security on data_sha1hex
                    cnx.create_entity('File', data=Binary(b'a,b,c'),
                                      data_name=u'csv',
                                      data_sha1hex=u'chat1',
                                      file_distribution=csv_dist)

                cnx.create_entity('Distribution', title=u'First Dataset (XLS)',
                                  description=u'First Dataset in XLS format',
                                  of_dataset=ds, license=license,
                                  distribution_format=xls_concept,
                                  media_type=appxls_concept,
                                  access_url=u'http://www.example.org',
                                  cwuri=u'http://example.org/dataset/xls')
                cnx.create_entity('Distribution', title=u'First Dataset (ZIP)',
                                  description=u'First Dataset in ZIP format',
                                  of_dataset=ds,
                                  distribution_format=zip_concept,
                                  media_type=appzip_concept,
                                  documentation=u'http://d.a.ta',
                                  access_url=u'http://www.example.org',
                                  cwuri=u'http://example.org/dataset/zip')
                cnx.commit()
                self.cat_eid = cat.eid

    @patch('cubes.datacat.entities.DownloadableDistribution.download_url',
           return_value=u'http://example.org/abc/download')  # predictable Distribution's access_url
    @patch('cubes.skos.rdfio.permanent_url',  # predicable URIs (no eid)
           side_effect=lambda entity: entity.cwuri)
    @patch('cubes.skos.rdfio.RDFGraphGenerator.same_as_uris')
    def _check_rdf_view(self, action_regid, expected_fname, mock_same_as_uris,
                        mock_permanent_url, mock_download_url):
        # Because we mock either cwuri or absolute_url, RDFGraphGenerator will add `sameAS` triples
        # on exported entities. We don't want this
        mock_same_as_uris.return_value = []
        with self.admin_access.client_cnx() as cnx:
            cat = cnx.entity_from_eid(self.cat_eid)
            with NamedTemporaryFile() as f:
                f.write(cat.view(action_regid))
                f.seek(0)
                graph = rdfio.default_graph()
                graph.load('file://' + f.name, rdf_format='xml')
            expected_graph = rdfio.default_graph()
            expected_graph.load('file://' + self.datapath(expected_fname), rdf_format='xml')
            iso1 = to_isomorphic(graph._graph)
            iso2 = to_isomorphic(expected_graph._graph)
            in_both, in_first, in_second = graph_diff(iso1, iso2)
            self.assertEqual(iso1, iso2, u'RDF graphs are not the same:\n'
                             '* Only in actual:\n{0}\n\n'
                             '* Only in expected:\n{1}'.format(
                                 sorted_triples(in_first), sorted_triples(in_second)))
        mock_download_url.assert_called_once_with()

    def test_complete_rdf_view(self):
        """Check that 'RDF export' action produce valid DCAT RDF data."""
        self._check_rdf_view('dcat.rdf.complete', 'valid_export.xml')

    def test_ckan_rdf_view(self):
        """Check bwcompat ckan views."""
        self._check_rdf_view('dcat.rdf.ckan', 'valid_export.xml')


class CkanJsonLicenseExportTC(testlib.CubicWebTC):
    """Test case for JSON license export to be used with CKAN."""

    configcls = PostgresApptestConfiguration

    def setup_database(self):
        with self.admin_access.repo_cnx() as cnx:
            lic_scheme = conceptscheme(
                cnx, u'http://publications.europa.eu/resource/authority/licence')
            cnx.execute('SET CS scheme_relation RT WHERE CS eid %(cs)s, RT name %(rt)s',
                        {'cs': lic_scheme.eid, 'rt': 'license_type'})
            cnx.commit()

    def test_ckan_json_license_export_match_by_uri(self):
        """Check that a license concept scheme is exported correctly for CKAN (license found by its
        URI in OpenDefinition)."""
        with self.admin_access.repo_cnx() as cnx:
            lic_scheme = cnx.execute('ConceptScheme CS WHERE CS scheme_relation RT, '
                                     'RT name "license_type"').one()
            cc_by_40_uri = cnx.create_entity('ExternalUri',
                                             uri=u'http://creativecommons.org/licenses/by/4.0/')
            cc_by_40 = cnx.create_entity('Concept', in_scheme=lic_scheme,
                                         exact_match=cc_by_40_uri)
            cnx.create_entity('Label', label_of=cc_by_40,
                              label=u'Creative Commons Attribution 4.0 International',
                              kind=u"preferred", language_code=u'en')
            cnx.commit()
        with self.admin_access.web_request() as req:
            lic_scheme = req.entity_from_eid(lic_scheme.eid)
            rset = req.execute('Any X WHERE X eid %(x)s',
                               {'x': lic_scheme.eid})
            export = json.loads(req.view('dcat.ckan.json.licenses', rset=rset))
            self.assertEqual(len(export), 1)
            self.assertEqual(export[0], {  # Values from file data/od-licenses.json
                "domain_content": True,
                "domain_data": True,
                "domain_software": False,
                "family": "",
                "id": "CC-BY-4.0",
                "maintainer": "Creative Commons",
                "od_conformance": "approved",
                "osd_conformance": "not reviewed",
                "status": "active",
                "title": "Creative Commons Attribution 4.0 International",
                "url": "https://creativecommons.org/licenses/by/4.0/",
            })

    def test_ckan_json_license_export_match_by_title(self):
        """Check that a license concept scheme is exported correctly for CKAN (license found by its
        title in OpenDefinition)."""
        with self.admin_access.repo_cnx() as cnx:
            lic_scheme = cnx.execute('ConceptScheme CS WHERE CS scheme_relation RT, '
                                     'RT name "license_type"').one()
            pddl = cnx.create_entity('Concept', in_scheme=lic_scheme,
                                     cwuri=u'http://example.org/licenses/pddl/1.0/')
            cnx.create_entity('Label', label_of=pddl,
                              label=u'Open Data Commons Public Domain Dedication and License v1.0',
                              kind=u"preferred", language_code=u'en')
            cnx.commit()
        with self.admin_access.web_request() as req:
            rset = req.execute('Any X WHERE X eid %(x)s',
                               {'x': lic_scheme.eid})
            export = json.loads(req.view('dcat.ckan.json.licenses', rset=rset))
            self.assertEqual(len(export), 1)
            self.assertEqual(export[0], {  # Values from file data/od-licenses.json
                "domain_content": False,
                "domain_data": True,
                "domain_software": False,
                "family": "",
                "id": "ODC-PDDL-1.0",
                "maintainer": "",
                "od_conformance": "approved",
                "osd_conformance": "not reviewed",
                "status": "active",
                "title": "Open Data Commons Public Domain Dedication and License v1.0",
                "url": "http://www.opendefinition.org/licenses/odc-pddl",
            })

    def test_ckan_json_license_export_no_match(self):
        """Check that a license concept scheme is exported correctly for CKAN (license not found in
        OpenDefinition)."""
        with self.admin_access.repo_cnx() as cnx:
            lic_scheme = cnx.execute('ConceptScheme CS WHERE CS scheme_relation RT, '
                                     'RT name "license_type"').one()
            other_at = cnx.create_entity('Concept', in_scheme=lic_scheme)
            cnx.create_entity('Label', label_of=other_at, label=u'Licence Ouverte / Open Licence',
                              kind=u"preferred", language_code=u'en')
            cnx.commit()
        with self.admin_access.web_request() as req:
            licence = req.entity_from_eid(other_at.eid)
            rset = req.execute('Any X WHERE X eid %(x)s',
                               {'x': lic_scheme.eid})
            export = json.loads(req.view('dcat.ckan.json.licenses', rset=rset))
            self.assertEqual(len(export), 1)
            self.assertEqual(export[0], {
                "domain_content": False,
                "domain_data": True,
                "domain_software": False,
                "family": "",
                "maintainer": "",
                "od_conformance": "not reviewed",
                "osd_conformance": "not reviewed",
                "status": "active",
                "title": "Licence Ouverte / Open Licence",
                "id": licence.absolute_url(),
                "url": rdfio.permanent_url(licence),
            })

    def test_ckan_json_license_export_multiple_schemes(self):
        """Check several concept schemes can be exported with the view."""
        with self.admin_access.repo_cnx() as cnx:
            scheme1 = cnx.create_entity(
                'ConceptScheme', title=u'test scheme')
            cnx.execute('SET X scheme_relation RT'
                        ' WHERE RT name "license_type",'
                        ' X title "test"')
            scheme1.add_concept(u'foo')
            scheme2 = cnx.create_entity(
                'ConceptScheme', title=u'test 2')
            scheme2.add_concept(u'bar')
            cnx.execute('SET X scheme_relation RT'
                        ' WHERE RT name "license_type",'
                        ' X title LIKE "test%"')
            cnx.commit()
        with self.admin_access.web_request() as req:
            rset = req.execute(
                'Any CS WHERE CS is ConceptScheme, CS title LIKE "test%"')
            export = json.loads(req.view('dcat.ckan.json.licenses', rset=rset))
            self.assertCountEqual([x['title'] for x in export],
                                  [u'foo', u'bar'])


if __name__ == '__main__':
    import unittest
    unittest.main()
