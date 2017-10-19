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
"""cubicweb-saem_ref unit tests for schema"""

import unittest
from datetime import date

from cubicweb.devtools.testlib import CubicWebTC

from cubicweb_compound.utils import optional_relations, graph_relations
from cubicweb_saem_ref import ConceptSchemeGraph

import testutils


def create_published_records_panel(cnx):
    for name, kind in (
        (u"Mr Pink", u"person"),
        (u"Adams", u"family"),
        (u"Direction de la communication", u"authority"),
    ):
        ar = testutils.authority_record(cnx, name, kind)
        cnx.commit()
        ar.cw_adapt_to('IWorkflowable').fire_transition('publish')
        cnx.commit()


class SchemaConstraintsTC(CubicWebTC):
    assertValidationError = testutils.assertValidationError

    def test_published_constraint_on_contact_point(self):
        """ create two agents: one published P and one not published N.
            create one OU and check that interface will only show P that can become its
            contact point
        """
        with self.admin_access.repo_cnx() as cnx:
            peter = testutils.agent(cnx, u'Peter')
            testutils.agent(cnx, u'Norton')
            cnx.commit()
            peter.cw_adapt_to('IWorkflowable').fire_transition('publish')
            ou = testutils.organization_unit(cnx, u'Alice')
            cnx.commit()
            rset = ou.unrelated('contact_point', 'Agent')
            self.assertEqual(rset.one().eid, peter.eid)

    def test_published_constraint_on_archival_agent(self):
        """ create two OU: one published P and one not published N.
            create one Organization and check that interface will only show P that can become its
            archival agent
        """
        with self.admin_access.repo_cnx() as cnx:
            pou = testutils.organization_unit(cnx, u'P OU', archival_roles=['archival'])
            testutils.organization_unit(cnx, u'N OU', archival_roles=['archival'])
            cnx.commit()
            pou.cw_adapt_to('IWorkflowable').fire_transition('publish')
            cnx.commit()
            # should be created by testutils.organization_unit() above.
            authority = cnx.find('Organization', name=u'Default authority').one()
            rset = authority.unrelated('archival_unit', 'OrganizationUnit')
            self.assertEqual(rset.one().eid, pou.eid)

    def test_published_constraint_on_use_profile(self):
        with self.admin_access.repo_cnx() as cnx:
            deposit_unit = testutils.organization_unit(cnx, u'AU', archival_roles=['deposit'])
            p1 = testutils.setup_profile(cnx)
            p2 = testutils.setup_profile(cnx)
            cnx.commit()
            p1.cw_adapt_to('IWorkflowable').fire_transition('publish')
            cnx.commit()

            with self.assertValidationError(cnx):
                deposit_unit.cw_set(use_profile=p2)

            deposit_unit.cw_set(use_profile=p1)
            cnx.commit()

    def test_agent_authority_record_is_a_person(self):
        """Authority record for an agent is limited to person"""
        with self.admin_access.repo_cnx() as cnx:
            create_published_records_panel(cnx)
            peter = testutils.agent(cnx, u'Peter')
            self.assertEqual(
                peter.unrelated('authority_record', 'AuthorityRecord').one(),
                cnx.find("AuthorityRecord", has_text=u"Mr Pink").one(),
            )

    def test_organization_unit_authority_record_is_a_authority(self):
        """Authority record for an organization unit is limited to authority"""
        with self.admin_access.repo_cnx() as cnx:
            create_published_records_panel(cnx)
            pou = testutils.organization_unit(cnx, u'P OU')
            self.assertEqual(
                pou.unrelated('authority_record', 'AuthorityRecord').one(),
                cnx.find("AuthorityRecord", has_text=u"Direction de la communication").one(),
            )

    def assertCantChangeRecordKind(self, arecord, kind):
        cnx = arecord._cw
        with self.assertValidationError(cnx) as cm:
            arecord.cw_set(agent_kind=cnx.find('AgentKind', name=kind).one())
        self.assertEqual(cm.exception.errors,
                         {'agent_kind-subject':
                          'This record is used by a relation forbidding to change its type'})

    def test_authority_record_kind_consistency(self):
        with self.admin_access.repo_cnx() as cnx:
            arecord = testutils.authority_record(cnx, u'service', kind=u'authority')
            testutils.organization_unit(cnx, u'unit', authority_record=arecord)
            cnx.commit()

            self.assertEqual(
                [k.name for k in arecord.unrelated('agent_kind', 'AgentKind').entities()],
                [])

            self.assertCantChangeRecordKind(arecord, u'person')

            org = testutils.authority_with_naa(cnx)
            org.cw_set(authority_record=arecord)
            cnx.commit()
            self.assertCantChangeRecordKind(arecord, u'person')

            org.cw_set(authority_record=None)
            self.assertEqual(
                {k.name for k in arecord.unrelated('agent_kind', 'AgentKind').entities()},
                {u'unknown-agent-kind', u'family', u'person'})
            arecord.cw_set(agent_kind=cnx.find('AgentKind', name=u'person').one())
            cnx.commit()

            testutils.agent(cnx, u'bob', authority_record=arecord)
            cnx.commit()
            self.assertCantChangeRecordKind(arecord, u'authority')

    def test_organization_unit_contact_point_in_the_same_authority(self):
        """Create two agents on two distinct authorities. Create an organization unit and check that
        interface will only show consistent proposal for contact point
        """
        with self.admin_access.repo_cnx() as cnx:
            # Create an archival agent in a custom authority
            authority = testutils.authority_with_naa(cnx, name=u'boss club')
            jdoe = testutils.agent(cnx, u'jdoe', authority=authority)
            # Create another archival agent in the default authority
            norton = testutils.agent(cnx, u'Norton')
            cnx.commit()
            # Publish both agents (because of the published constraint)
            jdoe.cw_adapt_to('IWorkflowable').fire_transition('publish')
            norton.cw_adapt_to('IWorkflowable').fire_transition('publish')
            cnx.commit()
            # Now create an organisation unit and check the unrelated list
            ou = testutils.organization_unit(cnx, u'Alice')
            cnx.commit()
            rset = ou.unrelated('contact_point', 'Agent')
            self.assertEqual(rset.one().eid, norton.eid)

    def test_organization_archival_unit_in_whatever_authority(self):
        """Create two organizations on two distinct authorities. Check that interface will show both
        of them as proposal for archival_agent of the default organization
        """
        with self.admin_access.repo_cnx() as cnx:
            # Create an organization unit in a custom authority
            authority = testutils.authority_with_naa(cnx, name=u'boss club')
            jdoe = testutils.organization_unit(cnx, u'jdoe', archival_roles=['archival'])
            # Create another archival organization unit in the default authority
            norton = testutils.organization_unit(cnx, u'Norton', archival_roles=[u'archival'])
            cnx.commit()
            # Publish both organization units (because of the published constraint)
            jdoe.cw_adapt_to('IWorkflowable').fire_transition('publish')
            norton.cw_adapt_to('IWorkflowable').fire_transition('publish')
            cnx.commit()
            # Now check the unrelated list for authority's archival_unit
            authority = cnx.find('Organization', name=u'Default authority').one()
            rset = authority.unrelated('archival_unit', 'OrganizationUnit')
            self.assertEqual(len(rset), 2)

    def test_agent_authority_consistency(self):
        with self.admin_access.repo_cnx() as cnx:
            authority1 = testutils.authority_with_naa(cnx)
            authority2 = testutils.authority_with_naa(cnx, name=u'boss club')
            user = self.create_user(cnx, login=u'user', groups=('users',))
            cnx.commit()
            # jdoe is in authority2 and user has no authority: OK
            jdoe = testutils.agent(cnx, u'jdoe', authority=authority2)
            jdoe.cw_set(agent_user=user)
            cnx.commit()
            # jdoe is in authority2 and attempt to set user in authority1: KO
            with self.assertValidationError(cnx):
                user.cw_set(authority=authority1)

            # break link between agent and user
            jdoe.cw_set(agent_user=None)
            cnx.commit()
            user.cw_set(authority=authority1)
            # jdoe is in authority2, user in authority1 and attempt to link them KO
            with self.assertValidationError(cnx):
                jdoe.cw_set(agent_user=user)

    def test_organization_unit_unicity(self):
        with self.admin_access.cnx() as cnx:
            testutils.organization_unit(cnx, u'arch', archival_roles=[u'archival'])
            cnx.commit()

            with self.assertValidationError(cnx):
                testutils.organization_unit(cnx, u'arch', archival_roles=[u'archival'])

            other_authority = testutils.authority_with_naa(cnx, name=u'other authority')
            testutils.organization_unit(cnx, u'arch', archival_roles=[u'archival'],
                                        authority=other_authority)
            cnx.commit()

    def test_agent_unicity(self):
        with self.admin_access.cnx() as cnx:
            testutils.agent(cnx, u'bob')
            cnx.commit()

            with self.assertValidationError(cnx):
                testutils.agent(cnx, u'bob')

            other_authority = testutils.authority_with_naa(cnx, name=u'other authority')
            testutils.agent(cnx, u'bob', authority=other_authority)
            cnx.commit()


class AuthorityRecordTC(CubicWebTC):

    def test_fti(self):
        with self.admin_access.repo_cnx() as cnx:
            agent = testutils.authority_record(cnx, u'Guenievre', kind=u'person',
                                               end_date=date(476, 2, 9))
            address = cnx.create_entity('PostalAddress', street=u"1 av. de l'europe",
                                        postalcode=u'31400', city=u'Toulouse')
            cnx.create_entity('AgentPlace', name=u'place', place_address=address, place_agent=agent)
            cnx.create_entity('AgentFunction', name=u'function', function_agent=agent)
            cnx.create_entity('LegalStatus', term=u'legal status', legal_status_agent=agent)
            cnx.commit()
            for search in (u'guenievre', u'europe', u'place', u'function', u'legal status'):
                with self.subTest(search=search):
                    self.assertEqual(cnx.execute('AuthorityRecord X WHERE X has_text %(search)s',
                                                 {'search': search}).one().eid, agent.eid)


class ConceptSchemeTC(CubicWebTC):

    def test_graph_structure(self):
        graph = ConceptSchemeGraph(self.schema)
        expected = {
            'Concept': {('in_scheme', 'subject'): ['ConceptScheme']},
            'Label': {('label_of', 'subject'): ['Concept']},
        }
        self.assertEqual(graph.parent_structure('ConceptScheme'),
                         expected)

    def test_optional_relations(self):
        graph = ConceptSchemeGraph(self.schema)
        opts = optional_relations(self.schema,
                                  graph.parent_structure('ConceptScheme'))
        expected = {}
        self.assertEqual(opts, expected)

    def test_relations_consistency(self):
        graph = ConceptSchemeGraph(self.schema)
        structure = graph.parent_structure('ConceptScheme')
        structurals, optionals, mandatories = graph_relations(
            self.schema, structure)
        self.assertEqual(structurals - optionals, mandatories)


if __name__ == '__main__':
    unittest.main()
