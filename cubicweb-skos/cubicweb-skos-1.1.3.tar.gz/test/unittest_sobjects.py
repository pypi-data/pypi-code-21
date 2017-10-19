# coding: utf-8
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

import logging
from contextlib import contextmanager

from cubicweb.devtools import testlib


@contextmanager
def silent_logging(logger=None):
    logger = logging.getLogger(logger)
    prev_level = logger.level
    logger.setLevel(logging.CRITICAL + 10)
    yield
    logger.setLevel(prev_level)


class DumpRelationsTC(testlib.CubicWebTC):
    def test(self):
        from cubes.skos.sobjects import dump_relations
        with self.admin_access.client_cnx() as cnx:
            scheme = cnx.create_entity('ConceptScheme', title=u'preexisting')
            concept = scheme.add_concept(u'something',
                                         cwuri=u'http://data.bnf.fr/ark:/12148/cb11934798x')
            cnx.commit()
            self.assertEqual(dump_relations(cnx, scheme.eid, 'ConceptScheme'),
                             [(concept.eid, 'in_scheme', None)])
            self.assertEqual(dump_relations(cnx, concept.eid, 'Concept'),
                             [(None, 'in_scheme', scheme.eid),
                              (concept.preferred_label[0].eid, 'label_of', None)])


class SKOSXMLImportTC(testlib.CubicWebTC):
    test_db_id = 'xmlparser'

    @classmethod
    def pre_setup_database(cls, cnx, config):
        url = u'file://%s' % cls.datapath('siaf_matieres_shortened.xml')
        cnx.create_entity('CWSource', name=u'mythesaurus', type=u'datafeed', parser=u'rdf.skos',
                          url=url)
        url = u'file://%s' % cls.datapath('bnf_rameau_0045_shortened.xml')
        cnx.create_entity('CWSource', name=u'rameau', type=u'datafeed', parser=u'rdf.skos',
                          url=url)
        scheme = cnx.create_entity('ConceptScheme', title=u'preexisting')
        scheme.add_concept(u'something', cwuri=u'http://data.bnf.fr/ark:/12148/cb11934798x')
        cnx.commit()

    def pull_source(self, source_name):
        dfsource = self.repo.sources_by_uri[source_name]
        assert dfsource.eid, dfsource
        # Disable raise_on_error as the "shortened" input files are not
        # complete.
        with self.repo.internal_cnx() as cnx:
            with silent_logging('cubicweb.sources'):
                dfsource.pull_data(cnx, force=True, raise_on_error=False)

    def check_siaf_shortened(self, source_name):
        with self.admin_access.client_cnx() as cnx:
            scheme = cnx.find('ConceptScheme', cwuri='http://data.culture.fr/'
                              'thesaurus/resource/ark:/67717/Matiere').one()
            self.assertEqual(scheme.title, u"Thésaurus-matières pour "
                             "l'indexation des archives locales")
            descr = u"Le Thésaurus pour la description et l'indexation des archives locales"
            self.assertEqual(scheme.description[:len(descr)], descr)
            self.assertEqual(scheme.description_format, u"text/plain")
            self.assertEqual(scheme.cwuri, u'http://data.culture.fr/'
                             'thesaurus/resource/ark:/67717/Matiere')
            self.assertEqual(scheme.cw_source[0].name, source_name)
            top_concepts = dict((c.cwuri, c) for c in scheme.top_concepts)
            # 11 original top concepts + 1 because of missing broader concept
            self.assertEqual(len(top_concepts), 12)
            concept = top_concepts['http://data.culture.fr/thesaurus/resource/ark:/67717/T1-503']
            self.assertEqual(concept.cw_source[0].name, source_name)
            self.assertEqual(len(concept.preferred_label), 1)
            self.assertEqual(len(concept.alternative_label), 0)
            self.assertEqual(len(concept.hidden_label), 0)
            narrow_concepts = dict((c.cwuri, c) for c in concept.narrower_concept)
            self.assertEqual(len(narrow_concepts), 2)
            label = concept.preferred_label[0]
            # XXX support skos-xl
            self.assertEqual(label.cwuri, u'http://data.culture.fr/thesaurus/resource/'
                             'ark:/67717/T1-503#preferred_label8c179857731ea1dbfc9d152ba4338eda')
            self.assertEqual(label.cw_source[0].name, source_name)
            self.assertEqual(label.label, u'communications')
            self.failIf(cnx.execute('Any L WHERE NOT EXISTS(L label_of X)'))
            # exact / close match
            concept = cnx.find('Concept', cwuri='http://data.culture.fr/thesaurus/resource/'
                               'ark:/67717/T1-246').one()
            self.assertEqual(len(concept.exact_match), 1)
            self.assertEqual(concept.exact_match[0].cw_etype, 'Concept')
            self.assertEqual(concept.exact_match[0].cwuri,
                             'http://data.bnf.fr/ark:/12148/cb11934798x')
            concept = cnx.find('Concept', cwuri='http://data.culture.fr/thesaurus/resource/'
                               'ark:/67717/T1-1317').one()
            self.assertEqual(len(concept.exact_match), 1)
            exturi = concept.exact_match[0]
            self.assertEqual(exturi.cw_etype, 'ExternalUri')
            self.assertEqual(exturi.cwuri, 'http://data.bnf.fr/ark:/12148/cb120423190')
            concept = cnx.find('Concept', cwuri='http://data.culture.fr/thesaurus/resource/'
                               'ark:/67717/T1-543').one()
            self.assertEqual(len(concept.close_match), 1)
            self.assertEqual(concept.close_match[0].cw_etype, 'ExternalUri')
            self.assertEqual(concept.close_match[0].uri,
                             'http://dbpedia.org/resource/Category:Economics')

            # full-text indexation
            rset = cnx.execute('Any U WHERE X cwuri U, X has_text %(q)s', {'q': 'communications'})
            self.assertEqual(rset.rows,
                             [['http://data.culture.fr/thesaurus/resource/ark:/67717/T1-503']])

            concept = cnx.find('Concept', cwuri='http://data.culture.fr/thesaurus/resource/'
                               'ark:/67717/T1-246').one()
            exturi.cw_set(inlined_match=concept)
            cnx.commit()

        self.pull_source('rameau')
        with self.admin_access.client_cnx() as cnx:
            concept = cnx.find('Concept', cwuri='http://data.culture.fr/thesaurus/resource/'
                               'ark:/67717/T1-1317').one()
            self.assertEqual(concept.label(), 'administration')
            self.assertEqual(len(concept.exact_match), 1)
            former_exturi = concept.exact_match[0]
            self.assertEqual(former_exturi.cw_etype, 'Concept')
            self.assertEqual(former_exturi.cwuri, 'http://data.bnf.fr/ark:/12148/cb120423190')
            self.assertEqual(former_exturi.inlined_match[0].cwuri,
                             'http://data.culture.fr/thesaurus/resource/ark:/67717/T1-246')

    def test_datafeed_source(self):
        # test creation upon initial pull
        self.pull_source('mythesaurus')
        self.check_siaf_shortened(u'mythesaurus')
        # test update upon subsequent pull
        self.pull_source('mythesaurus')

    def test_service(self):
        with self.admin_access.repo_cnx() as cnx:
            scheme_uris = cnx.call_service(
                'rdf.skos.import',
                stream=open(self.datapath('siaf_matieres_shortened.xml')),
                rdf_format='xml')[-1]
        self.assertEqual(scheme_uris,
                         ['http://data.culture.fr/thesaurus/resource/ark:/67717/Matiere'])
        self.check_siaf_shortened(u'system')

    def test_oddities(self):
        with self.admin_access.repo_cnx() as cnx:
            cnx.call_service('rdf.skos.import',
                             stream=open(self.datapath('oddities.xml')),
                             rdf_format='xml')
            scheme = cnx.execute('ConceptScheme X WHERE '
                                 'X cwuri "http://data.culture.fr/thesaurus/Matiere"').one()
            self.assertEqual(scheme.dc_title(), scheme.cwuri)
            concept = scheme.reverse_in_scheme[0]
            self.assertEqual(concept.label(), u'communications')
            self.assertEqual(len(concept.in_scheme), 2)
            concept = cnx.execute('Concept X WHERE '
                                  'X cwuri "http://logilab.fr/thesaurus/test/c3"').one()
            self.assertEqual(len(concept.broader_concept), 2)


class LCSVImportTC(testlib.CubicWebTC):

    def setup_database(self):
        with self.admin_access.repo_cnx() as cnx:
            scheme = cnx.create_entity('ConceptScheme', cwuri=u'http://example/lcsv')
            cnx.commit()
        self.scheme_uri = scheme.cwuri

    def test_import_lcsv(self):
        with self.admin_access.repo_cnx() as cnx:
            cnx.call_service('lcsv.skos.import', scheme_uri=self.scheme_uri,
                             stream=open(self.datapath('lcsv_example_shortened.csv')),
                             delimiter='\t', encoding='utf-8', language_code=u'es')
            self._check_imported_lcsv(cnx, 'es')

    def test_import_lcsv_without_language_code(self):
        with self.admin_access.repo_cnx() as cnx:
            cnx.call_service('lcsv.skos.import', scheme_uri=self.scheme_uri,
                             stream=open(self.datapath('lcsv_example_shortened.csv')),
                             delimiter='\t', encoding='utf-8')
            self._check_imported_lcsv(cnx, None)

    def _check_imported_lcsv(self, cnx, label_lang):
        scheme = cnx.find('ConceptScheme', cwuri=u'http://example/lcsv').one()
        self.assertEqual(len(scheme.top_concepts), 2)
        concepts = cnx.find('Concept')
        self.assertEqual(len(concepts), 5)
        concept1 = cnx.find(
            'Concept', definition=u"Définition de l'organisation politique de l'organisme,").one()
        label = concept1.preferred_label[0]
        self.assertEqual(label.label, "Vie politique")
        self.assertEqual(len(concept1.preferred_label), 1)
        self.assertEqual(len(concept1.narrower_concept), 2)
        self.assertEqual(concept1.cwuri, 'http://testing.fr/cubicweb/%s' % concept1.eid)
        concept2 = cnx.find('Concept',
                            definition=u"Création volontaire ou en application de la loi").one()
        self.assertEqual(concept2.broader_concept[0], concept1)
        self.assertEqual(concept2.cwuri, 'http://testing.fr/cubicweb/%s' % concept2.eid)
        label = cnx.find('Label', label=u"Vie politique").one()
        self.assertEqual(label.language_code, label_lang)
        self.assertEqual(label.cwuri, 'http://testing.fr/cubicweb/%s' % label.eid)


if __name__ == '__main__':
    from unittest import main
    main()
