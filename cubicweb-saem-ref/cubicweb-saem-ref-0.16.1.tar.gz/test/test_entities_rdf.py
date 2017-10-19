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
"""Tests for agent entities"""

import datetime

from six import text_type

import mock

from cubicweb.devtools.testlib import CubicWebTC

from cubes.skos.rdfio import RDFLibRDFGraph, RDFRegistry

from cubicweb_saem_ref import permanent_url
from cubicweb_saem_ref.entities import rdf

import testutils


class RDFExportTC(testutils.XmlTestMixin, CubicWebTC):
    """Test case for RDF export"""

    def setUp(self):
        super(RDFExportTC, self).setUp()
        self.reg = RDFRegistry()
        self.reg.register_prefix('rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
        self.reg.register_prefix('dc', 'http://purl.org/dc/elements/1.1/')
        self.reg.register_prefix('dcterms', 'http://purl.org/dc/terms/')
        self.reg.register_prefix('foaf', 'http://xmlns.com/foaf/0.1/')
        self.reg.register_prefix('lglb', 'http://www.logilab.org/saem/0#')
        self.reg.register_prefix('org', 'http://www.w3.org/ns/org#')
        self.reg.register_prefix('schema', 'http://schema.org/')
        self.reg.register_prefix('vcard', 'http://www.w3.org/2006/vcard/ns#')
        self.reg.register_prefix('prov', 'http://www.w3.org/ns/prov#')

    def _rdf_triples(self, entity, adapter_name='RDFPrimary'):
        graph = RDFLibRDFGraph()
        entity.cw_adapt_to(adapter_name).fill(graph)
        return list(graph.triples())

    def assertItemsIn(self, items, container):
        """Check that elements of `items` are in `container`."""
        for item in items:
            self.assertIn(item, container)

    def assertItemsNotIn(self, items, container):
        """Check that elements of `items` are not in `container`."""
        for item in items:
            self.assertNotIn(item, container)

    def assertHasActivity(self, entity, activity, triples):
        entity_url = permanent_url(entity)
        activity_url = permanent_url(activity)
        user_url = permanent_url(activity.associated_with[0])
        self.assertItemsIn([
            (activity_url, self.uri('rdf:type'), self.uri('prov:Activity')),
            (activity_url, self.uri('prov:used'), entity_url),
            (activity_url, self.uri('prov:generated'), entity_url),
            (activity_url, self.uri('prov:wasAssociatedWith'), user_url),
            (activity_url, self.uri('prov:label'), activity.description),
            (activity_url, self.uri('prov:type'), activity.type),
            (activity_url, self.uri('prov:startedAtTime'), activity.start),
            (activity_url, self.uri('prov:endedAtTime'), activity.end),
        ], triples)

    def uri(self, s):
        return text_type(self.reg.normalize_uri(s))

    def test_organization_unit(self):
        with self.admin_access.client_cnx() as cnx:
            agent = testutils.agent(cnx, u'John Doe')
            ou = testutils.organization_unit(cnx, u'Acme Inc.',
                                             archival_roles=['deposit', 'control'],
                                             contact_point=agent)
            org = ou.authority[0]
            triples = self._rdf_triples(ou)
            self.assertItemsIn([
                (permanent_url(ou), self.uri('rdf:type'), self.uri('org:OrganizationUnit')),
                (permanent_url(ou), self.uri('dc:title'), u'Acme Inc.'),
                (permanent_url(ou), self.uri('dc:identifier'), 'ark:/' + ou.ark),
                (permanent_url(ou), self.uri('vcard:role'), u'deposit'),
                (permanent_url(ou), self.uri('vcard:role'), u'control'),
                (permanent_url(ou), self.uri('schema:contactPoint'), permanent_url(agent)),
                (permanent_url(agent), self.uri('rdf:type'), self.uri('foaf:Person')),
                (permanent_url(agent), self.uri('foaf:name'), u'John Doe'),
                (permanent_url(agent), self.uri('dc:identifier'), 'ark:/' + agent.ark),
                (permanent_url(ou), self.uri('org:unitOf'), permanent_url(org)),
            ], triples)

    def test_organization(self):
        self.reg.register_prefix('saem', 'http://www.logilab.org/saem/0#')
        with self.admin_access.client_cnx() as cnx:
            other_org = cnx.create_entity(
                'Organization', name=u'Friends of default authority', ark=u'123')
            org = testutils.authority_with_naa(cnx)
            ou = testutils.organization_unit(cnx, u'archivists',
                                             archival_roles=[u'archival'],
                                             authority=other_org)
            org.cw_set(archival_unit=ou)
            org.cw_clear_all_caches()
            assert org.archival_unit[0].eid == ou.eid
            assert org.archival_authority[0].eid == other_org.eid
            triples = self._rdf_triples(org)
            expected = [
                (permanent_url(org), self.uri('rdf:type'), self.uri('org:Organization')),
                (permanent_url(org), self.uri('dc:title'), u'Default authority'),
                (permanent_url(org), self.uri('dc:identifier'), 'ark:/' + org.ark),
                (permanent_url(org), self.uri('saem:archivalUnit'), permanent_url(ou)),
                (permanent_url(org), self.uri('saem:archivalAuthority'), permanent_url(other_org)),
            ]
            self.assertItemsIn(expected, triples)

    def test_agent(self):
        with self.admin_access.client_cnx() as cnx:
            agent = testutils.agent(cnx, u'Roger Rabbit')
            triples = self._rdf_triples(agent)
            self.assertItemsIn([
                (permanent_url(agent), self.uri('rdf:type'), self.uri('foaf:Person')),
                (permanent_url(agent), self.uri('foaf:name'), u'Roger Rabbit'),
                (permanent_url(agent), self.uri('dc:identifier'), 'ark:/' + agent.ark),
            ], triples)

    def test_authority_record_rdf_base(self):
        with self.admin_access.client_cnx() as cnx:
            for kind, rdfkind in ((u'authority', 'org:OrganizationUnit'),
                                  (u'person', 'foaf:Person'),
                                  (u'family', 'foaf:Group')):
                with self.subTest(kind=kind, rdfkind=rdfkind):
                    record = testutils.authority_record(cnx, u'Acme', kind=kind)
                    cnx.commit()

                    triples = self._rdf_triples(record)
                    self.assertItemsIn([
                        (permanent_url(record), self.uri('rdf:type'), self.uri(rdfkind)),
                        (permanent_url(record), self.uri('foaf:name'), u'Acme'),
                        (permanent_url(record), self.uri('dc:identifier'), 'ark:/' + record.ark),
                    ], triples)
                    self.assertHasActivity(record, record.reverse_generated[0], triples)

    def test_authority_record_places(self):
        with self.admin_access.client_cnx() as cnx:
            record = testutils.authority_record(cnx, u'Acme Inc. Authority')
            work_address = cnx.create_entity('PostalAddress', street=u"1 av. de l'europe",
                                             postalcode=u'31400', city=u'Toulouse')
            cnx.create_entity('AgentPlace', role=u'work', place_agent=record,
                              place_address=work_address)
            home_address = cnx.create_entity('PostalAddress', street=u"Place du Capitole",
                                             postalcode=u'31000', city=u'Toulouse')
            cnx.create_entity('AgentPlace', role=u'home', place_agent=record,
                              place_address=home_address)
            triples = self._rdf_triples(record)
            self.assertItemsIn([
                (permanent_url(record), self.uri('vcard:hasAddress'), permanent_url(work_address)),
                (permanent_url(work_address), self.uri('vcard:role'), 'work'),
                (permanent_url(record), self.uri('vcard:hasAddress'), permanent_url(home_address)),
                (permanent_url(home_address), self.uri('vcard:role'), 'home'),
            ], triples)

    def test_authority_record_with_chronological_relation(self):
        with self.admin_access.client_cnx() as cnx:
            record1 = testutils.authority_record(cnx, u'Acme Inc. Authority')
            record2 = testutils.authority_record(cnx, u'Acme2 Inc. Authority')
            record3 = testutils.authority_record(cnx, u'Acme3 Inc. Authority')
            cnx.create_entity('ChronologicalRelation', chronological_predecessor=record1,
                              chronological_successor=record2)
            cnx.create_entity('ChronologicalRelation', chronological_predecessor=record2,
                              chronological_successor=record3)
            triples = self._rdf_triples(record2)
            self.assertItemsIn([
                (permanent_url(record2), self.uri('dcterms:isReplacedBy'), permanent_url(record3)),
                (permanent_url(record2), self.uri('dcterms:replaces'), permanent_url(record1)),
            ], triples)

    def test_authority_record_with_hierarchical_relation_rdf_export(self):
        with self.admin_access.client_cnx() as cnx:
            record1 = testutils.authority_record(cnx, u'Acme Inc. Authority')
            record2 = testutils.authority_record(cnx, u'Acme Group. Authority')
            cnx.create_entity('HierarchicalRelation',
                              hierarchical_parent=record2,
                              hierarchical_child=record1,
                              start_date=datetime.date(2008, 1, 1),
                              end_date=datetime.date(2099, 1, 1))
            relation_url = permanent_url(record1.reverse_hierarchical_child[0])
            time_interval_url = relation_url + '#timeInterval'
            expected_hierarchical_relations = [
                (relation_url, self.uri('org:organization'), permanent_url(record2)),
                (relation_url, self.uri('org:member'), permanent_url(record1)),
                (relation_url, self.uri('org:role'),
                 'http://www.logilab.org/saem/hierarchical_role'),
                (relation_url, self.uri('org:memberDuring'), time_interval_url),
                (time_interval_url, self.uri('schema:startDate'), datetime.date(2008, 1, 1)),
                (time_interval_url, self.uri('schema:endDate'), datetime.date(2099, 1, 1)),
            ]
            triples = self._rdf_triples(record1)
            self.assertItemsIn(expected_hierarchical_relations, triples)
            triples = self._rdf_triples(record2)
            self.assertItemsIn(expected_hierarchical_relations, triples)

    def test_authority_record_with_associative_relation_rdf_export(self):
        with self.admin_access.client_cnx() as cnx:
            record1 = testutils.authority_record(cnx, u'Acme Inc. Authority')
            record2 = cnx.create_entity('ExternalUri', uri=u'agent2', cwuri=u'agent2')
            cnx.create_entity('AssociationRelation',
                              association_from=record1,
                              association_to=record2)
            relation_url = permanent_url(record1.reverse_association_from[0])
            triples = self._rdf_triples(record1)
            self.assertItemsIn([
                (relation_url, self.uri('org:organization'), permanent_url(record1)),
                (relation_url, self.uri('org:member'), permanent_url(record2)),
                (relation_url, self.uri('org:member'), permanent_url(record1)),
                (relation_url, self.uri('org:organization'), permanent_url(record2)),
                (relation_url, self.uri('org:role'),
                 u'http://www.logilab.org/saem/association_role'),
            ], triples)

    def test_conceptscheme_rdf_prov(self):
        with self.admin_access.client_cnx() as cnx:
            scheme = testutils.setup_scheme(cnx, u'some vocab')
            cnx.commit()
            concept = scheme.add_concept(u'some concept')
            cnx.commit()

        # get scheme and concept from a fresh connection to avoid unexpected cache side effects
        # interference (where cw_clear_all_caches is not enough)
        with self.admin_access.client_cnx() as cnx:
            scheme = cnx.entity_from_eid(scheme.eid)
            concept = cnx.entity_from_eid(concept.eid)

            orig_warm_caches = rdf.ConceptSchemeRDFPrimaryAdapter.warm_caches

            mock_execute = mock.MagicMock()

            def warm_caches(self):
                orig_warm_caches(self)
                # ensure no further RQL query is done past this point by hacking .execute
                self._cw.execute = mock_execute

            with mock.patch('cubicweb_saem_ref.entities.rdf.ConceptSchemeRDFPrimaryAdapter'
                            '.warm_caches', autospec=True, side_effect=warm_caches):
                triples = self._rdf_triples(scheme)

            # scheme has two activities: its creation and addition of a concept
            self.assertHasActivity(scheme, scheme.reverse_generated[0], triples)
            self.assertHasActivity(scheme, scheme.reverse_generated[1], triples)
            self.assertHasActivity(concept, concept.reverse_generated[0], triples)
            self.assertEqual(mock_execute.call_count, 0)


if __name__ == '__main__':
    import unittest
    unittest.main()
