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
"""Functional security tests."""

from datetime import date
from cubicweb.devtools.testlib import CubicWebTC

import testutils


class NonManagerUserTC(CubicWebTC):
    """Tests checking that a user in "users" group only can do things.

    Most of the times, we do not call any assertion method and only rely on no
    error being raised.
    """
    assertUnauthorized = testutils.assertUnauthorized

    login = u'bob'

    def setup_database(self):
        with self.admin_access.cnx() as cnx:
            self.create_user(cnx, self.login, ('users', ))
            authority = testutils.authority_with_naa(cnx)
            cnx.execute('SET U authority O WHERE U login %(login)s, O eid %(o)s',
                        {'login': self.login, 'o': authority.eid})
            cnx.commit()

        self.authority_eid = authority.eid

    def test_create_update_authorityrecord(self):
        with self.admin_access.cnx() as cnx:
            admin_arecord_eid = testutils.authority_record(cnx, name=u'admin').eid
            cnx.commit()

        with self.new_access(self.login).cnx() as cnx:
            arecord = testutils.authority_record(cnx, name=u'a')
            cnx.commit()
            arecord.cw_set(record_id=u'123')
            cnx.commit()

            # can change kind (unless used in constrained relation, but this is tested in
            # unittest_schema)
            arecord.cw_set(agent_kind=cnx.find('AgentKind', name=u'authority').one())
            cnx.commit()

            # can modify record created by someone else
            admin_arecord = cnx.entity_from_eid(admin_arecord_eid)
            admin_arecord.cw_set(record_id=u'123')
            cnx.commit()

        # can create relation and modify those created by someone else
        for rel_etype, rel_from_rtype, rel_to_rtype in [
                ('ChronologicalRelation', 'chronological_predecessor', 'chronological_successor'),
                ('HierarchicalRelation', 'hierarchical_parent', 'hierarchical_child'),
                ('AssociationRelation', 'association_from', 'association_to'),
        ]:
            with self.admin_access.cnx() as cnx:
                # can create / update relation
                relation_eid = cnx.create_entity(
                    rel_etype, **{rel_from_rtype: admin_arecord_eid,
                                  rel_to_rtype: arecord}).eid
                cnx.commit()

            with self.new_access(self.login).cnx() as cnx:
                relation = cnx.entity_from_eid(relation_eid)
                relation.cw_set(
                    start_date=date.today(), **{rel_from_rtype: arecord,
                                                rel_to_rtype: admin_arecord_eid})
                cnx.commit()
                cnx.create_entity(
                    rel_etype, **{rel_from_rtype: admin_arecord_eid,
                                  rel_to_rtype: arecord})
                cnx.commit()

    def test_create_update_sedaprofile(self):
        with self.new_access(self.login).cnx() as cnx:
            profile = testutils.setup_profile(cnx)
            cnx.commit()
            profile.cw_set(user_annotation=u'meh')
            cnx.commit()

            profile.cw_adapt_to('IWorkflowable').fire_transition('publish')
            cnx.commit()
            testutils.setup_profile(cnx, title=u'Clone', new_version_of=profile)
            cnx.commit()

    def test_create_update_vocabulary(self):
        with self.admin_access.cnx() as cnx:
            admin_scheme = testutils.scheme_for_type(cnx, u'seda_keyword_type_to', None,
                                                     u'type1')
            cnx.commit()
            type_concept = admin_scheme.reverse_in_scheme[0]

        with self.new_access(self.login).cnx() as cnx:
            with self.assertUnauthorized(cnx):
                testutils.setup_scheme(cnx, u'my scheme',
                                       u'lab1', u'lab2')

            admin_scheme = cnx.entity_from_eid(admin_scheme.eid)
            type_concept = cnx.entity_from_eid(type_concept.eid)
            with self.assertUnauthorized(cnx):
                admin_scheme.cw_set(title=u'code keyword types')
            with self.assertUnauthorized(cnx):
                admin_scheme.cw_set(code_keyword_type=type_concept)

            admin_scheme.add_concept(u'type2')
            cnx.commit()

            cnx.create_entity('Label', kind=u'alternative', label=u'Le type n.1',
                              label_of=type_concept)
            cnx.commit()

    def test_create_update_agent_in_own_organization(self):
        with self.admin_access.cnx() as cnx:
            other_authority = testutils.authority_with_naa(cnx, name=u'other authority')
            other_agent = testutils.agent(cnx, u'bob', authority=other_authority)
            cnx.commit()
            other_authority_eid = other_authority.eid
            other_agent_eid = other_agent.eid

        with self.new_access(self.login).cnx() as cnx:
            agent = testutils.agent(cnx, u'bob', authority=self.authority_eid)
            cnx.commit()
            agent.cw_set(name=u'bobby')
            cnx.commit()
            agent.cw_delete()
            cnx.commit()
            arecord = testutils.authority_record(cnx, name=u'bobby', kind=u'person')
            agent.cw_set(authority_record=arecord)
            cnx.commit()

            with self.assertUnauthorized(cnx):
                testutils.agent(cnx, u'other bob', authority=other_authority_eid)

            other_agent = cnx.entity_from_eid(other_agent_eid)
            with self.assertUnauthorized(cnx):
                other_agent.cw_set(name=u'bobby')
            with self.assertUnauthorized(cnx):
                other_agent.cw_delete()
            with self.assertUnauthorized(cnx):
                other_arecord = testutils.authority_record(cnx, name=u'other bob', kind=u'person')
                other_agent.cw_set(authority_record=other_arecord)

    def test_create_update_organizationunit_in_own_organization(self):
        with self.admin_access.cnx() as cnx:
            other_authority = testutils.authority_with_naa(cnx, name=u'other authority')
            other_unit = testutils.organization_unit(
                cnx, u'arch', archival_roles=[u'archival'], authority=other_authority)
            profile = testutils.setup_profile(cnx)
            scheme = testutils.scheme_for_type(cnx, u'seda_keyword_type_to', None)
            cnx.commit()
            profile.cw_adapt_to('IWorkflowable').fire_transition('publish')
            cnx.commit()

            other_authority_eid = other_authority.eid
            other_unit_eid = other_unit.eid
            profile_eid = profile.eid
            scheme_eid = scheme.eid

        with self.new_access(self.login).cnx() as cnx:
            roles = (u'archival', u'deposit')
            unit = testutils.organization_unit(
                cnx, u'arch', archival_roles=roles, authority=self.authority_eid)
            cnx.commit()
            unit.cw_set(name=u'archi',
                        use_profile=profile_eid,
                        related_concept_scheme=scheme_eid)
            cnx.commit()
            unit.cw_delete()
            cnx.commit()
            arecord = testutils.authority_record(cnx, name=u'arch', kind=u'authority')
            unit.cw_set(authority_record=arecord)
            cnx.commit()

            with self.assertUnauthorized(cnx):
                testutils.organization_unit(
                    cnx, u'other arch', archival_roles=roles, authority=other_authority_eid)

            other_unit = cnx.entity_from_eid(other_unit_eid)
            with self.assertUnauthorized(cnx):
                other_unit.cw_set(name=u'archi')
            with self.assertUnauthorized(cnx):
                other_unit.cw_set(use_profile=profile_eid)
            with self.assertUnauthorized(cnx):
                other_unit.cw_set(related_concept_scheme=scheme_eid)
            with self.assertUnauthorized(cnx):
                other_unit.cw_delete()
            with self.assertUnauthorized(cnx):
                other_arecord = testutils.authority_record(cnx, name=u'other arch',
                                                           kind=u'authority')
                other_unit.cw_set(authority_record=other_arecord)

    def test_cannot_modify_activities(self):
        with self.new_access(self.login).cnx() as cnx:
            arecord = testutils.authority_record(cnx, name=u'a')
            cnx.commit()

            activity = arecord.reverse_used[0]

            with self.assertUnauthorized(cnx):
                activity.cw_set(description=u'hacked')

            with self.assertUnauthorized(cnx):
                activity.cw_set(associated_with=cnx.find('CWUser', login='admin').one())

            with self.assertUnauthorized(cnx):
                activity.cw_set(generated=None)

            with self.assertUnauthorized(cnx):
                activity.cw_delete()

    def test_cannot_create_activities(self):
        with self.admin_access.cnx() as cnx:
            scheme = testutils.setup_scheme(cnx, u'my scheme')
            cnx.commit()
        with self.new_access(self.login).cnx() as cnx:
            scheme = cnx.entity_from_eid(scheme.eid)
            concept = scheme.add_concept(u'lab3')
            profile = testutils.setup_profile(cnx)
            cnx.commit()

            for entity in (scheme, concept, profile):
                with self.assertUnauthorized(cnx):
                    cnx.create_entity('Activity', generated=entity)
                with self.assertUnauthorized(cnx):
                    cnx.create_entity('Activity', used=entity)

            with self.assertUnauthorized(cnx):
                cnx.create_entity('Activity', associated_with=cnx.user)

    def test_cannot_create_update_organization(self):
        with self.new_access(self.login).cnx() as cnx:
            with self.assertUnauthorized(cnx):
                testutils.authority_with_naa(cnx, u'new')

            org = testutils.authority_with_naa(cnx)
            with self.assertUnauthorized(cnx):
                org.cw_set(name=u'uh')
            with self.assertUnauthorized(cnx):
                arecord = testutils.authority_record(cnx, name=u'a', kind=u'authority')
                org.cw_set(authority_record=arecord)

    def test_cannot_create_update_naa(self):
        with self.new_access(self.login).cnx() as cnx:
            with self.assertUnauthorized(cnx):
                cnx.create_entity('ArkNameAssigningAuthority',
                                  who=u'123', what=u'443')

            test_naa = testutils.naa(cnx)
            with self.assertUnauthorized(cnx):
                test_naa.cw_set(who=u'1')

    def test_can_create_authorityrecord_activities(self):
        with self.new_access(self.login).cnx() as cnx:
            arecord = testutils.authority_record(cnx, name=u'a')
            cnx.commit()
            # EAC import expect user may create activity
            cnx.create_entity('Activity', generated=arecord)
            cnx.commit()


class ManagerUserTC(CubicWebTC):
    """Tests checking that a user in "managers" group only can do things.

    Most of the times, we do not call any assertion method and only rely on no
    error being raised.
    """
    assertUnauthorized = testutils.assertUnauthorized

    def test_create_update_organization(self):
        with self.admin_access.cnx() as cnx:
            org = testutils.authority_with_naa(cnx)
            cnx.commit()
            org.cw_set(name=u'uh')
            cnx.commit()
            arecord = testutils.authority_record(cnx, name=u'a', kind=u'authority')
            org.cw_set(authority_record=arecord)
            cnx.commit()

    def test_create_update_naa(self):
        with self.admin_access.cnx() as cnx:
            test_naa = testutils.naa(cnx)
            cnx.commit()
            test_naa.cw_set(who=u'1')
            cnx.commit()
            naa = cnx.create_entity('ArkNameAssigningAuthority',
                                    who=u'123', what=u'443')
            cnx.commit()
            naa.cw_set(what=u'987')
            cnx.commit()

    def test_authority_type(self):
        with self.admin_access.repo_cnx() as cnx:
            self.create_user(cnx, login=u'user', groups=('users',))
            cnx.commit()
        with self.new_access('user').client_cnx() as cnx:
            with self.assertUnauthorized(cnx):
                testutils.authority_with_naa(cnx, name=u'dream team')

    def test_authority_relation(self):
        with self.admin_access.repo_cnx() as cnx:
            self.create_user(cnx, login=u'user', groups=('users',),
                             authority=testutils.authority_with_naa(cnx))
            agent = testutils.agent(cnx, u'user')
            authority = testutils.authority_with_naa(cnx, name=u'dream team')
            cnx.commit()
            # even manager can't change an agent's authority
            with self.assertUnauthorized(cnx):
                agent.cw_set(authority=authority.eid)
        with self.new_access('user').client_cnx() as cnx:
            agent = cnx.entity_from_eid(agent.eid)
            # user can't change its own authority
            with self.assertUnauthorized(cnx):
                agent.cw_set(authority=authority.eid)
            # user can't create an agent in another authority than its own
            with self.assertUnauthorized(cnx):
                testutils.agent(cnx, u'new agent', authority=authority.eid)
            # though he can add an agent to its own authority
            testutils.agent(cnx, u'new agent')
            cnx.commit()

    def test_agent_user(self):
        with self.admin_access.repo_cnx() as cnx:
            user1 = self.create_user(cnx, login=u'user1', groups=('users',),
                                     authority=testutils.authority_with_naa(cnx))
            user2 = self.create_user(cnx, login=u'user2', groups=('users',),
                                     authority=testutils.authority_with_naa(cnx))
            agent = testutils.agent(cnx, u'user1', agent_user=user1)
            cnx.commit()
        with self.new_access('user1').client_cnx() as cnx:
            agent = cnx.entity_from_eid(agent.eid)
            # user can't change its own user
            with self.assertUnauthorized(cnx):
                agent.cw_set(agent_user=user2.eid)
            with self.assertUnauthorized(cnx):
                agent.cw_set(agent_user=None)
            # user can't create an agent and specify its associated user
            with self.assertUnauthorized(cnx):
                testutils.agent(cnx, u'user2', agent_user=user2.eid)
            agent2 = testutils.agent(cnx, u'user2')
            cnx.commit()
            with self.assertUnauthorized(cnx):
                agent2.cw_set(agent_user=user2.eid)

    def test_authority_record_base(self):
        with self.admin_access.repo_cnx() as cnx:
            self.create_user(cnx, login=u'toto', groups=('users', 'guests'),
                             authority=testutils.authority_with_naa(cnx))
            cnx.commit()
        with self.new_access('toto').client_cnx() as cnx:
            function = cnx.create_entity('AgentFunction', name=u'grouillot')
            testutils.authority_record(cnx, u'bob', reverse_function_agent=function)
            cnx.commit()
        with self.admin_access.repo_cnx() as cnx:
            cnx.execute('DELETE U in_group G WHERE U login "toto", G name "users"')
            cnx.commit()
        with self.new_access('toto').client_cnx() as cnx:
            agent = cnx.find('AuthorityRecord', has_text=u'bob').one()
            # guest user can't modify an authority record
            with self.assertUnauthorized(cnx):
                agent.cw_set(record_id=u'bobby')

    def test_authority_record_wf_permissions(self):
        with self.admin_access.repo_cnx() as cnx:
            self.create_user(cnx, login=u'toto', groups=('users', 'guests'),
                             authority=testutils.authority_with_naa(cnx))
            cnx.commit()
        with self.new_access('toto').client_cnx() as cnx:
            function = cnx.create_entity('AgentFunction', name=u'grouillot')
            record = testutils.authority_record(cnx, u'bob', reverse_function_agent=function)
            cnx.commit()
            iwf = record.cw_adapt_to('IWorkflowable')
            iwf.fire_transition('publish')
            cnx.commit()
            # we can still modify a published record
            record.reverse_name_entry_for[0].cw_set(parts=u'bobby')
            function.cw_set(name=u'director')
            cnx.commit()

    def test_update_root_badgroup(self):
        with self.admin_access.repo_cnx() as cnx:
            self.create_user(cnx, login=u'toto', groups=('users', 'guests'))
            cnx.commit()
        with self.new_access('toto').client_cnx() as cnx:
            testutils.setup_profile(cnx, title=u'pp')
            cnx.commit()
        with self.admin_access.repo_cnx() as cnx:
            cnx.execute(
                'DELETE U in_group G WHERE U login "toto", G name "users"')
            cnx.commit()
        with self.new_access('toto').client_cnx() as cnx:
            profile = cnx.find('SEDAArchiveTransfer', title=u'pp').one()
            with self.assertUnauthorized(cnx):
                profile.cw_set(title=u'qq')

    def test_sedaprofile_wf_permissions(self):
        with self.admin_access.repo_cnx() as cnx:
            profile = testutils.setup_profile(cnx, title=u'pp')
            cnx.commit()
            # Profile in draft, modifications are allowed.
            profile.cw_set(title=u'ugh')
            cnx.commit()
            comment = cnx.create_entity('SEDAComment', seda_comment=profile)
            cnx.commit()
            # Profile published, no modification allowed.
            profile.cw_adapt_to('IWorkflowable').fire_transition('publish')
            cnx.commit()
            with self.assertUnauthorized(cnx):
                profile.cw_set(title=u'huugh')
            with self.assertUnauthorized(cnx):
                comment.cw_delete()
            with self.assertUnauthorized(cnx):
                cnx.create_entity('SEDAArchivalAgreement', seda_archival_agreement=profile)

    def test_conceptscheme_wf_permissions(self):
        with self.admin_access.cnx() as cnx:
            scheme = cnx.create_entity('ConceptScheme', ark_naa=testutils.naa(cnx))
            cnx.commit()
            # in draft, modifications are allowed.
            concept = scheme.add_concept(u'blah')
            cnx.commit()
            # published, can't modify existing content.
            scheme.cw_adapt_to('IWorkflowable').fire_transition('publish')
            cnx.commit()
            with self.assertUnauthorized(cnx):
                scheme.cw_set(description=u'plop')
            with self.assertUnauthorized(cnx):
                concept.preferred_label[0].cw_set(label=u'plop')
            # though addition of new concepts / labels is fine
            new_concept = scheme.add_concept(u'plop')
            cnx.commit()
            new_label = cnx.create_entity('Label', label=u'arhg', label_of=concept)
            cnx.commit()
            # while deletion is fine for label but not for concept nor scheme
            new_label.cw_delete()
            cnx.commit()
            with self.assertUnauthorized(cnx):
                scheme.cw_delete()
            with self.assertUnauthorized(cnx):
                new_concept.cw_delete()


if __name__ == '__main__':
    import unittest
    unittest.main()
