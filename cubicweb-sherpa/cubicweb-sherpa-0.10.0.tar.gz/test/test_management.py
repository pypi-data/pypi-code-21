# copyright 2017 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from cubicweb.devtools.testlib import CubicWebTC
from cubicweb.web.views import actions

from cubicweb_seda import testutils


class ActionTC(CubicWebTC):

    def assertMayManageSecurity(self, req, eid):
        rset = req.entity_from_eid(eid).as_rset()
        actionsdict = self.pactionsdict(req, rset)
        self.assertIn(actions.ManagePermissionsAction, actionsdict['moreactions'])

    def assertMayNotManageSecurity(self, req, eid):
        rset = req.entity_from_eid(eid).as_rset()
        actionsdict = self.pactionsdict(req, rset)
        self.assertNotIn(actions.ManagePermissionsAction, actionsdict['moreactions'])

    def test_management_profiles(self):
        with self.admin_access.cnx() as cnx:
            at = cnx.create_entity('SEDAArchiveTransfer', title=u'hop')
            at_unit = testutils.create_archive_unit(at)[0]

            self.create_user(cnx, 'user')

            cnx.commit()

        with self.admin_access.web_request() as req:

            self.assertMayManageSecurity(req, at.eid)
            self.assertMayNotManageSecurity(req, at_unit.eid)

        with self.new_access('user').web_request() as req:
            self.assertMayNotManageSecurity(req, at.eid)

    def test_management_units(self):
        with self.admin_access.cnx() as cnx:
            unit_comp = testutils.create_archive_unit(None, cnx=cnx)[0]
            cnx.commit()

        with self.admin_access.web_request() as req:
            self.assertMayManageSecurity(req, unit_comp.eid)

    def test_management_schemes(self):
        with self.admin_access.cnx() as cnx:
            scheme = cnx.create_entity('ConceptScheme', title=u'goldorak')
            concept = scheme.add_concept(u'fulguropoint')
            cnx.commit()

        with self.admin_access.web_request() as req:
            self.assertMayManageSecurity(req, scheme.eid)
            self.assertMayNotManageSecurity(req, concept.eid)

    def test_management_records(self):
        with self.admin_access.cnx() as cnx:
            record = testutils.create_authority_record(cnx, u'bob notice')
            cnx.commit()

        with self.admin_access.web_request() as req:
            self.assertMayManageSecurity(req, record.eid)


if __name__ == '__main__':
    import unittest
    unittest.main()
