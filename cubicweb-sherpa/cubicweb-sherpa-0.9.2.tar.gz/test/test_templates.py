# copyright 2017 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from cubicweb.devtools.testlib import CubicWebTC

from cubicweb_seda import testutils
from cubicweb_sherpa.views.templates import _compute_active_path


class ActivePathTC(CubicWebTC):

    def test_archive_transfer(self):
        with self.admin_access.cnx() as cnx:
            at = cnx.create_entity('SEDAArchiveTransfer', title=u'hop')
            au, alt, last = testutils.create_archive_unit(at)
            cnx.commit()

            for entity in (at, au, alt, last):
                with self.subTest(entity=entity):
                    self.assertEqual(_compute_active_path(entity.as_rset()),
                                     'sedaarchivetransfer')

    def test_archive_unit(self):
        with self.admin_access.cnx() as cnx:
            au, alt, last = testutils.create_archive_unit(None, cnx=cnx)
            cnx.commit()

            for entity in (au, alt, last):
                with self.subTest(entity=entity):
                    self.assertEqual(_compute_active_path(entity.as_rset()),
                                     'sedalib')

    def test_authority_record(self):
        with self.admin_access.cnx() as cnx:
            org_kind = cnx.find('AgentKind', name=u'authority').one()
            record = cnx.create_entity('AuthorityRecord', agent_kind=org_kind)
            cnx.create_entity('NameEntry', parts=u'record', form_variant=u'authorized',
                              name_entry_for=record)
            cnx.commit()

            self.assertEqual(_compute_active_path(record.as_rset()),
                             'authorityrecord')

    def test_concept_scheme(self):
        with self.admin_access.cnx() as cnx:
            scheme = cnx.create_entity('ConceptScheme', title=u'vocabulary')
            concept = scheme.add_concept(u'concept')
            cnx.commit()

            for entity in (scheme, concept):
                with self.subTest(entity=entity):
                    self.assertEqual(_compute_active_path(entity.as_rset()),
                                     'conceptscheme')


if __name__ == '__main__':
    import unittest
    unittest.main()
