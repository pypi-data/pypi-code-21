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

import os
from tempfile import NamedTemporaryFile

from logilab.common.testlib import TestCase, require_module

from cubicweb.devtools import testlib

from cubes.skos import rdfio
from cubes.skos.rdfio import unicode_with_language as ul


def skos(name):
    return 'http://www.w3.org/2004/02/skos/core#' + name


class UnicodeWithLanguageTC(TestCase):

    def test_comparison_ul_ul(self):
        a = ul('toto', 'fr')
        b = ul('toto', 'fr')
        self.assertEqual(a, b)

        b = ul('toto', 'en')
        self.assertNotEqual(a, b)

        b = ul('titi', 'fr')
        self.assertNotEqual(a, b)

    def test_comparison_ul_and_other(self):
        a = ul('toto', 'fr')
        b = u'toto'
        self.assertNotEqual(a, b)


class GuessRDFFormatTC(TestCase):

    def test_base(self):
        self.assertEqual(rdfio.guess_rdf_format('file.xml'), 'xml')
        self.assertEqual(rdfio.guess_rdf_format('file.rdf'), 'xml')
        self.assertEqual(rdfio.guess_rdf_format('file.n3'), 'n3')

    def test_url(self):
        self.assertEqual(rdfio.guess_rdf_format('http://url.com/rdf/file.xml'), 'xml')
        self.assertEqual(rdfio.guess_rdf_format('http://url.com/rdf/file.rdf'), 'xml')
        self.assertEqual(rdfio.guess_rdf_format('http://url.com/rdf/file.n3'), 'n3')

    def test_error(self):
        self.assertRaises(ValueError, rdfio.guess_rdf_format, 'file.unknown')
        self.assertRaises(ValueError, rdfio.guess_rdf_format, 'http://url.com/rdf/file')
        self.assertRaises(ValueError, rdfio.guess_rdf_format, 'http://url.com/file/rdf')


class RDFRegistryTC(TestCase):

    def setUp(self):
        self.xy = rdfio.RDFRegistry()
        self.xy.register_prefix('dc', 'http://purl.org/dc/elements/1.1/')
        self.xy.register_prefix('foaf', 'http://xmlns.com/foaf/0.1/')
        self.xy.register_prefix('skos', 'http://www.w3.org/2004/02/skos/core#')

    def test_register_prefix(self):
        xy = self.xy
        self.assertEqual(xy.prefixes['dc'], 'http://purl.org/dc/elements/1.1/')
        # re-registering the same prefix is fine
        xy.register_prefix('dc', 'http://purl.org/dc/elements/1.1/')
        # though re-registering an existing prefix to a different url isn't
        self.assertRaises(rdfio.RDFRegistryError,
                          xy.register_prefix, 'dc', 'http://purl.org/dc/elements/1.2/')
        # unless we explicitly tell it's ok
        xy.register_prefix('dc', 'http://purl.org/dc/elements/1.2/', overwrite=True)
        self.assertEqual(xy.prefixes['dc'], 'http://purl.org/dc/elements/1.2/')

    def test_register_etype_equivalence(self):
        xy = self.xy
        xy.register_etype_equivalence('CWUser', 'foaf:Person')
        self.assertEqual(xy.etype2rdf['CWUser'], 'http://xmlns.com/foaf/0.1/Person')
        # re-registering the same equivalence is fine
        xy.register_etype_equivalence('CWUser', 'foaf:Person')
        # though re-registering a different isn't
        self.assertRaises(rdfio.RDFRegistryError,
                          xy.register_etype_equivalence, 'CWUser', 'foaf:Personne')
        # unless we explicitly tell it's ok
        xy.register_etype_equivalence('CWUser', 'foaf:Personne', overwrite=True)
        self.assertEqual(xy.etype2rdf['CWUser'], 'http://xmlns.com/foaf/0.1/Personne')
        xy.register_etype_equivalence('User', 'foaf:Person', overwrite=True)

    def test_register_attribute_equivalence(self):
        xy = self.xy
        xy.register_etype_equivalence('CWUser', 'foaf:Person')
        xy.register_attribute_equivalence('CWUser', 'login', 'dc:title')
        self.assertEqual(xy.attr2rdf[('CWUser', 'login')], 'http://purl.org/dc/elements/1.1/title')
        # re-registering the same equivalence is fine
        xy.register_attribute_equivalence('CWUser', 'login', 'dc:title')
        # though re-registering a different isn't
        self.assertRaises(rdfio.RDFRegistryError,
                          xy.register_attribute_equivalence, 'CWUser', 'login', 'dc:description')
        # unless we explicitly tell it's ok
        xy.register_attribute_equivalence('CWUser', 'login', 'dc:description', overwrite=True)
        self.assertEqual(xy.attr2rdf[('CWUser', 'login')],
                         'http://purl.org/dc/elements/1.1/description')

    def test_register_relation_equivalence(self):
        xy = self.xy
        xy.register_etype_equivalence('ConceptScheme', 'skos:ConceptScheme')
        xy.register_etype_equivalence('Concept', 'skos:Concept')
        xy.register_relation_equivalence('Concept', 'in_scheme', 'ConceptScheme', 'skos:inScheme')
        xy.register_relation_equivalence('Concept', 'broader_concept', 'Concept', 'skos:broader')
        self.assertEqual(xy.rel2rdf[('Concept', 'in_scheme', 'ConceptScheme')],
                         set([('http://www.w3.org/2004/02/skos/core#inScheme', False)]))
        xy.register_relation_equivalence('Concept', 'in_scheme', 'ConceptScheme', 'skos:inScheme')
        xy.register_relation_equivalence('Concept', 'in_scheme', 'ConceptScheme', 'skos:inSchema')
        self.assertEqual(xy.rel2rdf[('Concept', 'in_scheme', 'ConceptScheme')],
                         set([('http://www.w3.org/2004/02/skos/core#inScheme', False),
                              ('http://www.w3.org/2004/02/skos/core#inSchema', False)]))
        xy.register_relation_equivalence('Concept', 'broader_concept', 'Concept', 'skos:broader')
        xy.register_relation_equivalence('Concept', 'broader_concept', 'Concept', 'skos:narrower',
                                         reverse=True)
        self.assertEqual(xy.rel2rdf[('Concept', 'broader_concept', 'Concept')],
                         set([('http://www.w3.org/2004/02/skos/core#broader', False),
                              ('http://www.w3.org/2004/02/skos/core#narrower', True)]))

    def test_predicates_for_subject_etype(self):
        xy = self.xy
        xy.register_etype_equivalence('ConceptScheme', 'skos:ConceptScheme')
        xy.register_etype_equivalence('Concept', 'skos:Concept')
        xy.register_attribute_equivalence('ConceptScheme', 'title', 'dc:title')
        xy.register_relation_equivalence('Concept', 'in_scheme', 'ConceptScheme', 'skos:inScheme')
        xy.register_relation_equivalence('Concept', 'broader_concept', 'Concept', 'skos:narrower',
                                         reverse=True)
        self.assertEqual(sorted(xy.predicates_for_subject_etype('ConceptScheme')),
                         [('title', 'http://purl.org/dc/elements/1.1/title', False)])
        self.assertEqual(sorted(xy.predicates_for_subject_etype('Concept')),
                         [('broader_concept', 'http://www.w3.org/2004/02/skos/core#narrower', True),
                          ('in_scheme', 'http://www.w3.org/2004/02/skos/core#inScheme', False)])

    def test_register_prefix_unknown(self):
        xy = self.xy
        with self.assertRaises(rdfio.RDFRegistryError) as cm:
            xy.register_etype_equivalence('CWUser', 'foafx:Person')
        self.assertEqual(str(cm.exception), 'prefix foafx not found')
        with self.assertRaises(rdfio.RDFRegistryError) as cm:
            xy.register_attribute_equivalence('ConceptScheme', 'title', 'foafx:title')
        self.assertEqual(str(cm.exception), 'prefix foafx not found')
        with self.assertRaises(rdfio.RDFRegistryError) as cm:
            xy.register_etype_equivalence('ConceptScheme', 'foafx:ConceptScheme')
        self.assertEqual(str(cm.exception), 'prefix foafx not found')


def dcf(string):
    return u'http://data.culture.fr/thesaurus/resource/ark:/67717/' + string


def ext_entities_to_dict(ext_entities):
    """Turn a sequence of external entities into a 2-level dict with entity
    type and extid as keys.
    """
    entities_dict = {}
    for extentity in ext_entities:
        entities_dict.setdefault(extentity.etype, {})[extentity.extid] = extentity.values
    return entities_dict


class RDFGraphTCMixIn(object):

    def setUp(self, uris=None):
        """Create a sample RDF graph and add some triples to it.

        Also load triples from the given URIs.
        """
        graph = self.graph = self.build_graph()
        self.bob = graph.uri("http://example.org/people/Bob")
        self.knows = graph.uri("http://foaf.com/knows")
        self.alice = graph.uri("http://example.org/people/Alice")
        self.firstname = graph.uri("http://foaf.com/firstname")
        self.age = graph.uri("http://foaf.com/age")
        self.desc = graph.uri("http://dc.com/description")
        graph.add(self.bob, self.knows, self.alice)
        graph.add(self.bob, self.firstname, "bob")
        graph.add(self.bob, self.age, 45)
        graph.add(self.bob, self.desc, ul("man", "en"))
        graph.add(self.alice, self.firstname, "alice")
        graph.add(self.alice, self.age, 25)
        uris = uris or []
        for uri in uris:
            graph.load(uri)

    def build_graph(self):
        raise NotImplementedError

    _triples = set([  # Only miss (Alice, knows, BNode)
        ('http://example.org/people/Alice', 'http://foaf.com/age', 25),
        ('http://example.org/people/Alice', 'http://foaf.com/firstname', u'alice'),
        ('http://example.org/people/Bob', 'http://foaf.com/firstname', u'bob'),
        ('http://example.org/people/Bob', 'http://foaf.com/age', 45),
        ('http://example.org/people/Bob', 'http://dc.com/description', ul('man', 'en')),
        ('http://example.org/people/Bob', 'http://foaf.com/knows',
         'http://example.org/people/Alice'),
    ])

    def test_add(self):
        graph = self.graph
        result = list(graph.objects(self.bob, self.knows))
        self.assertEqual(result, ["http://example.org/people/Alice"])
        result = list(graph.objects(self.bob, self.age))
        self.assertEqual(result, [45])
        result = list(graph.objects(self.bob, self.desc))
        self.assertEqual(result, [ul("man", "en")])
        result = list(graph.objects(self.alice, self.firstname))
        self.assertEqual(result, ["alice"])

    def test_triples(self):
        triples = set(self.graph.triples())
        self.assertTrue(self._triples.issubset(triples))

    def test_load_dump_roundtrip(self):
        # XXX other formats fail, but sounds due to the underlying lib
        for rdf_format in ('xml',):  # 'n3', 'nt'):
            self.set_description('testing roundtrip for the %s format' % rdf_format)
            self.assertRoundTrip(rdf_format)

    def assertRoundTrip(self, rdf_format='xml'):
        with NamedTemporaryFile(delete=False) as fobj:
            try:
                self.graph.dump(fobj, rdf_format=rdf_format)
                fobj.close()
                graph = self.build_graph()
                graph.load('file://' + fobj.name, rdf_format=rdf_format)
            finally:
                os.unlink(fobj.name)
        self.assertTrue(self._triples.issubset(set(graph.triples())))


class RDFLibRDFGraphTC(RDFGraphTCMixIn, TestCase):
    build_graph = rdfio.RDFLibRDFGraph

    @require_module('rdflib')
    def setUp(self):
        super(RDFLibRDFGraphTC, self).setUp(uris=[self.datapath('bnode.n3')])


class LibRDFRDFGraphTC(RDFGraphTCMixIn, TestCase):
    build_graph = rdfio.LibRDFRDFGraph

    @require_module('RDF')
    def setUp(self):
        super(LibRDFRDFGraphTC, self).setUp(uris=[self.datapath('bnode.n3')])


def skos_rdf_registry():
    xy = rdfio.RDFRegistry()
    xy.register_prefix('dc', 'http://purl.org/dc/elements/1.1/')
    xy.register_prefix('skos', 'http://www.w3.org/2004/02/skos/core#')
    xy.register_etype_equivalence('ConceptScheme', 'skos:ConceptScheme')
    xy.register_etype_equivalence('Concept', 'skos:Concept')
    xy.register_attribute_equivalence('ConceptScheme', 'title', 'dc:title')
    xy.register_relation_equivalence('Concept', 'in_scheme', 'ConceptScheme', 'skos:inScheme')
    xy.register_relation_equivalence('Concept', 'broader_concept', 'Concept', 'skos:broader')
    xy.register_relation_equivalence('Concept', 'broader_concept', 'Concept', 'skos:narrower',
                                     reverse=True)
    xy.register_relation_equivalence('Concept', 'narrower_concept', 'Concept', 'skos:narrower')
    xy.register_relation_equivalence('Concept', 'narrower_concept', 'Concept', 'skos:broader',
                                     reverse=True)
    xy.register_relation_equivalence('Concept', 'related_concept', 'Concept', 'skos:related')
    xy.register_relation_equivalence('Concept', 'preferred_label', 'Label', 'skos:prefLabel')
    return xy


class RDFGraphToEntitiesTC(TestCase):

    @require_module('rdflib')
    def test_rdflib(self):
        self._test(rdfio.RDFLibRDFGraph())

    @require_module('RDF')
    def test_librdf(self):
        self._test(rdfio.LibRDFRDFGraph())

    def _test(self, graph):
        xy = skos_rdf_registry()
        xy.register_relation_equivalence('Concept', 'alternative_label', 'Label', 'skos:altLabel')
        graph.load(self.datapath('siaf_matieres_shortened.xml'))

        etypes = ('ConceptScheme', 'Concept')  # , 'Label')
        ext_entities = rdfio.rdf_graph_to_entities(xy, graph, etypes)
        e = ext_entities_to_dict(ext_entities)
        self.assertEqual(e['ConceptScheme'][dcf('Matiere')],
                         {'title': set([u"Thésaurus-matières pour l'indexation "
                                        "des archives locales"])})
        self.assertEqual(e['Concept'][dcf('T1-1073')],
                         {'broader_concept': set([dcf('T1-3')]),
                          'in_scheme': set([dcf('Matiere')]),
                          'related_concept': set([dcf('T1-760')]),
                          'alternative_label': set([ul(u'académie', 'fr-fr'),
                                                    ul(u"société d'agriculture", 'fr-fr')]),
                          'preferred_label': set([ul(u'société savante', 'fr-fr')]),
                          })


class AddEntitiesToRDFGraphTC(testlib.CubicWebTC):

    @require_module('rdflib')
    def test_rdflib(self):
        self._test(rdfio.RDFLibRDFGraph())

    @require_module('RDF')
    def test_librdf(self):
        self._test(rdfio.LibRDFRDFGraph())

    def _test(self, graph):
        xy = skos_rdf_registry()
        xy.register_attribute_equivalence(
            'ConceptScheme', lambda x: x.dc_description(), 'dc:description')
        with self.admin_access.client_cnx() as cnx:
            scheme = cnx.create_entity('ConceptScheme', title=u'some classification',
                                       description=u'skos soks!')
            c1 = cnx.create_entity('Concept', in_scheme=scheme)
            l1 = cnx.create_entity('Label', label=u'hip', language_code=u'fr',
                                   kind=u'preferred', label_of=c1)
            c2 = cnx.create_entity('Concept', in_scheme=scheme, broader_concept=c1)
            l2 = cnx.create_entity('Label', label=u'hop', language_code=u'fr',
                                   kind=u'preferred', label_of=c2)
            c1_url = rdfio.permanent_url(c1)
            c2_url = rdfio.permanent_url(c2)
            l1_url = rdfio.permanent_url(l1)
            l2_url = rdfio.permanent_url(l2)
            scheme_url = rdfio.permanent_url(scheme)
            cnx.commit()
        with self.admin_access.client_cnx() as cnx:
            scheme = cnx.entity_from_eid(scheme.eid)
            stack = rdfio.entities_stack([scheme])
            graph_generator = rdfio.RDFGraphGenerator(graph)
            related = None
            try:
                while True:
                    entity = stack.send(related)
                    related = graph_generator.add_entity(entity, xy)
            except StopIteration:
                pass
            expected = [
                (scheme_url, rdfio.TYPE_PREDICATE_URI, skos('ConceptScheme')),
                (scheme_url, 'http://purl.org/dc/elements/1.1/title', u'some classification'),
                (scheme_url, 'http://purl.org/dc/elements/1.1/description', u'skos soks!'),
                (c1_url, skos('prefLabel'), l1_url),
                (c2_url, skos('prefLabel'), l2_url),
                (c1_url, skos('narrower'), c2_url),
                (c1_url, rdfio.TYPE_PREDICATE_URI, skos('Concept')),
                (c1_url, skos('inScheme'), scheme_url),
                (c2_url, rdfio.TYPE_PREDICATE_URI, skos('Concept')),
                (c2_url, skos('inScheme'), scheme_url),
                (c2_url, skos('broader'), c1_url),
            ]
            self.assertCountEqual(graph.triples(), expected)


if __name__ == '__main__':
    from unittest import main
    main()
