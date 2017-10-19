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

from functools import wraps
from StringIO import StringIO

from logilab.common.testlib import require_module

from cubicweb.devtools import testlib

from cubes.skos.entities import CSVIndentationError, CSVDecodeError
from cubes.skos.rdfio import (TYPE_PREDICATE_URI, RDFLibRDFGraph, LibRDFRDFGraph,
                              permanent_url, unicode_with_language as ul)


def get_narrower_concepts(concept):
    """Get a dictionnary matching the name of the concept to the dictionnary of its narrower
    concepts (recursive)
    """
    narrower_concepts = {}
    for concept in concept.narrower_concept:
        narrower_concepts[concept.dc_title()] = get_narrower_concepts(concept)
    return narrower_concepts


def build_result_dict(scheme):
    """Create a hierarchy with the concept names in a dictionary"""
    concepts = scheme.top_concepts
    result = {}
    for concept in concepts:
        result[concept.dc_title()] = get_narrower_concepts(concept)
    return result


class ConceptSchemeTC(testlib.CubicWebTC):

    def test_top_concepts(self):
        with self.admin_access.client_cnx() as cnx:
            scheme = cnx.create_entity('ConceptScheme', title=u'some classification')
            c1 = cnx.create_entity('Concept', in_scheme=scheme)
            cnx.create_entity('Label', label=u'hip', language_code=u'fr',
                              kind=u'preferred', label_of=c1)
            c2 = cnx.create_entity('Concept', in_scheme=scheme, broader_concept=c1)
            cnx.create_entity('Label', label=u'hop', language_code=u'fr',
                              kind=u'preferred', label_of=c2)
            cnx.commit()
            self.assertEqual(set(x.eid for x in scheme.top_concepts),
                             set((c1.eid,)))

    def test_add_concepts_from_file_interdoc(self):
        with self.admin_access.client_cnx() as cnx:
            scheme = cnx.create_entity('ConceptScheme', title=u'interdoc')
            cnx.commit()
        csv_file = self.datapath('thesaurus_interdoc_7_hierageneTab_shortened.csv')
        with self.admin_access.web_request() as req:
            scheme = req.entity_from_eid(scheme.eid)
            with open(csv_file) as sourcefile:
                scheme.add_concepts_from_file(sourcefile, u'utf-8', u'fr', u',')
            result = build_result_dict(scheme)
        expected = {
            u'ADMINISTRATION': {
                u'ACTION PUBLIQUE': {
                    u'ACTE ADMINISTRATIF': {
                        u'ACTE CREATEUR DE DROITS': {},
                        u'ACTE UNILATERAL': {
                            u'VISA': {},
                        },
                        u'CONTRAT PUBLIC': {
                            u'CONTRAT ADMINISTRATIF': {
                                u'CLAUSE EXORBITANTE': {},
                                u'COTRAITANCE': {
                                    u'GROUPEMENT D\'ENTREPRISES': {
                                        u'GROUPEMENT CONJOINT': {},
                                        u'GROUPEMENT SOLIDAIRE': {},
                                    },
                                },
                                u'EQUILIBRE FINANCIER': {
                                    u'FAIT DU PRINCE': {}
                                },
                                u'VENTE EN L\'ETAT FUTUR D\'ACHEVEMENT': {},
                            },
                            u'CONVENTION D\'EXPLOITATION': {},
                            u'PARTENARIAT PUBLIC-PRIVE': {
                                u'SOCIETE LOCALE DE PARTENARIAT': {},
                            },
                        },
                    },
                },
            },
            u'AMENAGEMENT': {
                u'AMENAGEMENT DU TERRITOIRE': {
                    u'AMENAGEMENT DE LA MONTAGNE': {
                        u'PROTECTION DE LA MONTAGNE': {
                            u'RTM': {},
                        },
                        u'UTN': {},
                        u'ZONE MONTAGNE': {},
                    },
                    u'AMENAGEMENT DU LITTORAL': {
                        u'BANDE LITTORALE DES 100 METRES': {},
                    },
                },
            },
        }
        self.assertEqual(result, expected)

    def test_add_concepts_from_file_ok(self):
        with self.admin_access.client_cnx() as cnx:
            scheme = cnx.create_entity('ConceptScheme', title=u'rapport')
            cnx.commit()
        csv_file = self.datapath('hierarchical_csv_example_shortened.csv')
        with self.admin_access.web_request() as req:
            scheme = req.entity_from_eid(scheme.eid)
            with open(csv_file) as sourcefile:
                scheme.add_concepts_from_file(sourcefile, u'utf-8', u'fr', u'\t')
            result = build_result_dict(scheme)
        expected = {
            u'APPELLATION DES LOIS ET DES RAPPORTS': {
                u'LOIS RAPPORTS JURISPRUDENCE': {
                    u'APPELLATION DE DECISIONS DE JURISPRUDENCE': {
                        u'ARRET BERKANI': {}, u'ARRET TERNON': {},
                    },
                    u'APPELLATION DES RAPPORTS': {
                        u'RAPPORT ARTHUIS': {}, u'LOLF': {}, u'LOV': {}},
                }
            },
            u'LISTE DES MOTS OUTILS': {
                u'CHAPITRE MOTS OUTILS': {
                    u'MOTS OUTILS': {
                        u'ABATTEMENT': {}, u'ACCORD': {},
                    }
                }
            }
        }
        self.assertEqual(result, expected)

    def test_add_concepts_from_file_sep_inside_concept(self):
        with self.admin_access.client_cnx() as cnx:
            scheme = cnx.create_entity('ConceptScheme', title=u'rapport')
            cnx.commit()
        rapport = StringIO('toto\n\tti\tti\n\ttata')
        with self.admin_access.web_request() as req:
            scheme = req.entity_from_eid(scheme.eid)
            scheme.add_concepts_from_file(rapport, u'utf-8', u'fr', u'\t')
            result = build_result_dict(scheme)
        expected = {u'toto': {u'ti\tti': {},
                              u'tata': {}}}
        self.assertEqual(result, expected)

    def test_add_concepts_from_file_decode_error(self):
        with self.admin_access.client_cnx() as cnx:
            scheme = cnx.create_entity('ConceptScheme', title=u'rapport')
            cnx.commit()
        with open(self.datapath('bad_encoding.csv')) as fobj:
            with self.admin_access.web_request() as req:
                scheme = req.entity_from_eid(scheme.eid)
                with self.assertRaises(CSVDecodeError) as cm:
                    scheme.add_concepts_from_file(fobj, u'utf-8', u'fr', u',')
                self.assertEqual(cm.exception.line, 3)
                # Now with the good encoding.
                fobj.seek(0)
                scheme.add_concepts_from_file(fobj, u'latin1', u'fr', u',')
                result = build_result_dict(scheme)
        expected = {u'voici mes concepts en latin1': {u'celui-ci est bon': {},
                                                      u'celui-là n\'est pas bon': {}}}
        self.assertEqual(result, expected)

    def test_add_concepts_from_file_wrong_indentation(self):
        with self.admin_access.client_cnx() as cnx:
            scheme = cnx.create_entity('ConceptScheme', title=u'rapport')
            cnx.commit()
        rapport = StringIO('toto\n\ttiti\n\t\t\ttata')
        with self.admin_access.web_request() as req:
            scheme = req.entity_from_eid(scheme.eid)
            with self.assertRaises(CSVIndentationError) as cm:
                scheme.add_concepts_from_file(rapport, u'utf-8', u'fr', u'\t')
            self.assertEqual(cm.exception.line, 3)

    def test_add_concepts_from_file_multiple_deindentation(self):
        with self.admin_access.client_cnx() as cnx:
            scheme = cnx.create_entity('ConceptScheme', title=u'rapport')
            cnx.commit()
        rapport = StringIO('toto\n\ttiti\n\t\ttata\ntutu')
        with self.admin_access.web_request() as req:
            scheme = req.entity_from_eid(scheme.eid)
            scheme.add_concepts_from_file(rapport, u'utf-8', u'fr', u'\t')
            result = build_result_dict(scheme)
        expected = {u'toto': {u'titi': {u'tata': {}}},
                    u'tutu': {}}
        self.assertEqual(result, expected)

    def test_add_concepts_from_file_sep_comma(self):
        with self.admin_access.client_cnx() as cnx:
            scheme = cnx.create_entity('ConceptScheme', title=u'rapport')
            cnx.commit()
        rapport = StringIO('toto\n,titi\n,,tata\n,,  tati  \n tutu \n,tuti\n,,titu\n,toti\n')
        with self.admin_access.web_request() as req:
            scheme = req.entity_from_eid(scheme.eid)
            scheme.add_concepts_from_file(rapport, u'utf-8', u'fr', u',')
            result = build_result_dict(scheme)
        expected = {u'toto': {u'titi': {u'tata': {}, u'tati': {}}},
                    u'tutu': {u'tuti': {u'titu': {}}, u'toti': {}}}
        self.assertEqual(result, expected)

    def test_add_concepts_from_file_sep_space(self):
        with self.admin_access.client_cnx() as cnx:
            scheme = cnx.create_entity('ConceptScheme', title=u'rapport')
            cnx.commit()
        rapport = StringIO('toto\n titi   iti\n  tata\n  tati  \ntutu \n tuti\n  titu\n toti\n')
        with self.admin_access.web_request() as req:
            scheme = req.entity_from_eid(scheme.eid)
            scheme.add_concepts_from_file(rapport, u'utf-8', u'fr', u' ')
            result = build_result_dict(scheme)
        expected = {u'toto': {u'titi   iti': {u'tata': {}, u'tati': {}}},
                    u'tutu': {u'tuti': {u'titu': {}}, u'toti': {}}}
        self.assertEqual(result, expected)


class ConceptTC(testlib.CubicWebTC):

    def setup_database(self):
        with self.admin_access.client_cnx() as cnx:
            scheme = cnx.create_entity('ConceptScheme', title=u'some classification')
            c1 = cnx.create_entity('Concept', in_scheme=scheme)
            cnx.create_entity('Label', label=u'hîp', language_code=u'fr-CA',
                              kind=u'preferred', label_of=c1)
            cnx.create_entity('Label', label=u'hip', language_code=u'en',
                              kind=u'preferred', label_of=c1)
            cnx.create_entity('Label', label=u'hop', language_code=u'fr',
                              kind=u'alternative', label_of=c1)
            cnx.commit()
        self.c1_eid = c1.eid

    def test_dc_title(self):
        with self.admin_access.client_cnx() as cnx:
            c1 = cnx.entity_from_eid(self.c1_eid)
            self.assertEqual(c1.dc_title(), u'hip')
            cnx.lang = 'fr'
            self.assertEqual(c1.dc_title(), u'hîp')

    def test_labels(self):
        with self.admin_access.client_cnx() as cnx:
            c1 = cnx.entity_from_eid(self.c1_eid)
            self.assertEqual(c1.labels,
                             {u'en': u'hip', u'fr-CA': u'hîp', u'fr': u'hîp'})

    def test_label_language_preferred(self):
        """The preferred label matching user's language is selected."""
        with self.admin_access.repo_cnx() as cnx:
            concept = cnx.find('Concept').one()
            # Should be the preferred English label.
            self.assertEqual(concept.label(), u'hip')

    def test_label_language_nopreferred_in_language(self):
        """No label in user's language, a random one is selected."""
        with self.admin_access.repo_cnx() as cnx:
            concept = cnx.find('Concept').one()
            cnx.execute('SET L language_code "oups" WHERE L language_code "en"')
            cnx.commit()
            concept.cw_clear_all_caches()
            self.assertIn(concept.label(),
                          [x.label for x in concept.reverse_label_of])

    def test_label_language_ambiguous_short_form(self):
        """The requested language's short form in ambiguous."""
        with self.admin_access.repo_cnx() as cnx:
            concept = cnx.find('Concept').one()
            cnx.create_entity('Label', label=u'in Ghotuo',
                              language_code=u'aaa', kind=u'preferred',
                              label_of=concept)
            cnx.create_entity('Label', label=u'in Alumu-Tesu',
                              language_code=u'aab', kind=u'preferred',
                              label_of=concept)
            cnx.create_entity('Label', label=u'in Ari',
                              language_code=u'aac', kind=u'preferred',
                              label_of=concept)
            cnx.commit()
            self.assertEqual(concept.label(language_code=u'aaa'),
                             u'in Ghotuo')
            self.assertEqual(concept.label(language_code=u'aab'),
                             u'in Alumu-Tesu')
            self.assertEqual(concept.label(language_code=u'aac'),
                             u'in Ari')


SKOS_SCHEME = 'http://www.w3.org/2004/02/skos/core#ConceptScheme'
SKOS_CONCEPT = 'http://www.w3.org/2004/02/skos/core#Concept'
SKOS_INSCHEME = 'http://www.w3.org/2004/02/skos/core#inScheme'
SKOS_LABEL = 'http://www.w3.org/2004/02/skos/core#prefLabel'
SKOS_DEFINITION = 'http://www.w3.org/2004/02/skos/core#definition'
DC_TITLE = 'http://purl.org/dc/elements/1.1/title'


def require_lib(lib):
    """Decorate a test method with require_module(lib) and bind it respective
    graph generator instance.
    """
    graphcls = {'rdflib': RDFLibRDFGraph,
                'RDF': LibRDFRDFGraph}[lib]

    def decorator(testfunc):
        @wraps(testfunc)
        def wrapper(self):
            return testfunc(self, graphcls())
        return require_module(lib)(wrapper)

    return decorator


class RDFAdaptersTC(testlib.CubicWebTC):

    def setup_database(self):
        with self.admin_access.client_cnx() as cnx:
            scheme = cnx.create_entity('ConceptScheme', title=u'some classification')
            c1 = cnx.create_entity('Concept', in_scheme=scheme,
                                   definition=u'def1')
            cnx.create_entity('Label', label=u'hip', language_code=u'fr',
                              kind=u'preferred', label_of=c1)
            c2 = cnx.create_entity('Concept', in_scheme=scheme, broader_concept=c1)
            cnx.create_entity('Label', label=u'hop', language_code=u'fr',
                              kind=u'preferred', label_of=c2)
            cnx.commit()
            self.assertEqual(set(x.eid for x in scheme.top_concepts),
                             set((c1.eid,)))

    def _test_concept_list_repr(self, graph):
        with self.admin_access.client_cnx() as cnx:
            scheme = cnx.execute('ConceptScheme X').one()
            concept = cnx.find('Concept', definition=u'def1').one()
            rdfgenerator = concept.cw_adapt_to('RDFList')
            rdfgenerator.fill(graph)
            expected = [
                (permanent_url(concept), TYPE_PREDICATE_URI, SKOS_CONCEPT),
                (permanent_url(concept), SKOS_DEFINITION, u'def1'),
                (permanent_url(concept), SKOS_INSCHEME, permanent_url(scheme)),
            ]
        self.assertCountEqual(set(graph.triples()), expected)

    test_rdflib_concept_list_repr = require_lib('rdflib')(_test_concept_list_repr)
    test_librdf_concept_list_repr = require_lib('RDF')(_test_concept_list_repr)

    def _test_scheme_list_repr(self, graph):
        with self.admin_access.client_cnx() as cnx:
            scheme = cnx.execute('ConceptScheme X').one()
            rdfgenerator = scheme.cw_adapt_to('RDFList')
            rdfgenerator.fill(graph)
        expected = [(permanent_url(scheme), TYPE_PREDICATE_URI, SKOS_SCHEME),
                    (permanent_url(scheme), DC_TITLE, u'some classification')]
        self.assertCountEqual(graph.triples(), expected)

    test_rdflib_scheme_list_repr = require_lib('rdflib')(_test_scheme_list_repr)
    test_librdf_scheme_list_repr = require_lib('RDF')(_test_scheme_list_repr)

    def _test_scheme_primary_repr(self, graph):
        with self.admin_access.client_cnx() as cnx:
            scheme = cnx.execute('ConceptScheme X').one()
            c1 = scheme.top_concepts[0]
            c2 = c1.narrower_concept[0]
            scheme_uri = permanent_url(scheme)
            c1_uri = permanent_url(c1)
            c2_uri = permanent_url(c2)
            rdfgenerator = scheme.cw_adapt_to('RDFPrimary')
            rdfgenerator.fill(graph)
        expected = [
            (scheme_uri, TYPE_PREDICATE_URI, SKOS_SCHEME),
            (scheme_uri, DC_TITLE, u'some classification'),
            (c1_uri, TYPE_PREDICATE_URI, SKOS_CONCEPT),
            (c1_uri, SKOS_INSCHEME, scheme_uri),
            (c1_uri, SKOS_LABEL, ul('hip', 'fr')),
            (c1_uri, SKOS_DEFINITION, u'def1'),
            (c1_uri, u'http://www.w3.org/2004/02/skos/core#narrower', c2_uri),
            (c2_uri, TYPE_PREDICATE_URI, SKOS_CONCEPT),
            (c2_uri, SKOS_INSCHEME, scheme_uri),
            (c2_uri, SKOS_LABEL, ul('hop', 'fr')),
            (c2_uri, u'http://www.w3.org/2004/02/skos/core#broader', c1_uri),
        ]
        self.assertCountEqual(graph.triples(), expected)

    test_rdflib_scheme_primary_repr = require_lib('rdflib')(_test_scheme_primary_repr)
    test_librdf_scheme_primary_repr = require_lib('RDF')(_test_scheme_primary_repr)

    def _test_concept_primary_repr(self, graph):
        with self.admin_access.client_cnx() as cnx:
            scheme = cnx.execute('ConceptScheme X').one()
            c1 = cnx.find('Concept', definition=u'def1').one()
            c2 = c1.narrower_concept[0]
            c1_uri, c2_uri = permanent_url(c1), permanent_url(c2)
            rdfgenerator = c1.cw_adapt_to('RDFPrimary')
            rdfgenerator.fill(graph)
        expected = [
            (c1_uri, TYPE_PREDICATE_URI, SKOS_CONCEPT),
            (c1_uri, SKOS_INSCHEME, permanent_url(scheme)),
            (c1_uri, SKOS_DEFINITION, u'def1'),
            (c1_uri, SKOS_LABEL, ul('hip', 'fr')),
            (c1_uri, u'http://www.w3.org/2004/02/skos/core#narrower', c2_uri),
            (c2_uri, u'http://www.w3.org/2004/02/skos/core#broader', c1_uri),
        ]
        self.assertCountEqual(set(graph.triples()), expected)

    test_rdflib_concept_primary_repr = require_lib('rdflib')(_test_concept_primary_repr)
    test_librdf_concept_primary_repr = require_lib('RDF')(_test_concept_primary_repr)

    def test_warm_relation_cache(self):
        with self.admin_access.client_cnx() as cnx:
            scheme = cnx.execute('ConceptScheme X').one()
            rdfgenerator = scheme.cw_adapt_to('RDFPrimary')
            rdfgenerator.warm_caches()
            c1 = cnx.execute('Concept X WHERE X preferred_label L, L label "hip"').one()
            c2 = cnx.execute('Concept X WHERE X preferred_label L, L label "hop"').one()
            scheme._cw.execute = lambda rql, args=None: 1 / 0  # ensure no RQL query is done
            self.assertCountEqual(scheme.cw_attr_cache,
                                  ['cwuri', 'creation_date', 'modification_date',
                                   'title', 'description', 'description_format'])
            self.assertEqual(len(scheme.reverse_in_scheme), 2)
            self.assertEqual(c1.scheme.eid, scheme.eid)
            self.assertIn('cwuri', c1.cw_attr_cache)
            self.assertIn('definition', c1.cw_attr_cache)
            self.assertIn('example', c1.cw_attr_cache)
            self.assertEqual(c1.labels, {u'fr': u'hip'})
            for rtype in ('exact_match', 'close_match'):
                self.assertIn(rtype + '_subject', c1._cw_related_cache)
                self.assertNotIn(rtype + '_object', c1._cw_related_cache)
            self.assertEqual(len(c1.broader_concept), 0)
            self.assertEqual(len(c1.reverse_broader_concept), 1)
            self.assertEqual(len(c1.related_concept), 0)
            self.assertEqual(c1.reverse_broader_concept, (c2,))
            self.assertEqual(len(c2.broader_concept), 1)
            self.assertEqual(len(c2.reverse_broader_concept), 0)
            self.assertEqual(c2.broader_concept, (c1,))


if __name__ == '__main__':
    from unittest import main
    main()
