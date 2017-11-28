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
"""cubicweb-sherpa security tests"""

from contextlib import contextmanager

from cubicweb import Unauthorized
from cubicweb.devtools.testlib import CubicWebTC

from cubicweb_seda import testutils


class SecurityTC(CubicWebTC):

    @contextmanager
    def assertUnauthorized(self, cnx):
        with self.assertRaises(Unauthorized) as cm:
            yield cm
            cnx.commit()
        cnx.rollback()

    def setUp(self):
        super(SecurityTC, self).setUp()
        with self.admin_access.cnx() as cnx:
            self.create_user(cnx, 'bob')
            self.create_user(cnx, 'alice')

    def assertOwnershipBasedAccess(self, etype, to_test_attribute):
        # alice can read bob entity, but not update nor delete
        with self.new_access('alice').cnx() as cnx:
            entity = cnx.find(etype).one()
            with self.assertUnauthorized(cnx):
                entity.cw_set(**{to_test_attribute: u'abcd'})
                cnx.commit()
            with self.assertUnauthorized(cnx):
                entity.cw_delete()
                cnx.commit()
        # unless explicitly authorized using owned_by relation
        with self.new_access('bob').cnx() as cnx:
            entity = cnx.find(etype).one()
            entity.cw_set(owned_by=cnx.find('CWUser', login='alice').one())
            cnx.commit()
        with self.new_access('alice').cnx() as cnx:
            entity = cnx.find(etype).one()
            entity.cw_set(**{to_test_attribute: u'abcd'})
            cnx.commit()
            entity.cw_delete()
            cnx.commit()

    def test_add_read_update_delete_record(self):
        with self.new_access('bob').cnx() as cnx:
            testutils.create_authority_record(cnx, u'bob notice')
            cnx.commit()

        self.assertOwnershipBasedAccess('AuthorityRecord', 'isni')

    def test_add_read_update_delete_transfer(self):
        with self.new_access('bob').cnx() as cnx:
            cnx.create_entity('SEDAArchiveTransfer', title=u'goldorak go')
            cnx.commit()

        self.assertOwnershipBasedAccess('SEDAArchiveTransfer', 'title')

    def test_add_read_update_delete_unit(self):
        with self.new_access('bob').cnx() as cnx:
            au, alt, last = testutils.create_archive_unit(None, cnx=cnx)
            cnx.commit()

        self.assertOwnershipBasedAccess('SEDAArchiveUnit', 'user_annotation')

    def test_add_read_update_delete_schemes(self):
        with self.new_access('bob').cnx() as cnx:
            with self.assertUnauthorized(cnx):
                cnx.create_entity('ConceptScheme', title=u'goldorak')

        with self.admin_access.cnx() as cnx:
            scheme = cnx.create_entity('ConceptScheme', title=u'goldorak')
            concept = scheme.add_concept(u'fulguropoint')
            cnx.commit()

        with self.new_access('bob').cnx() as cnx:
            scheme = cnx.find('ConceptScheme').one()
            with self.assertUnauthorized(cnx):
                scheme.cw_set(title=u'hop')
            with self.assertUnauthorized(cnx):
                scheme.add_concept(u'fulguropoint')
            concept = cnx.find('Concept').one()
            with self.assertUnauthorized(cnx):
                concept.cw_delete()
            with self.assertUnauthorized(cnx):
                scheme.cw_delete()


if __name__ == '__main__':
    import unittest
    unittest.main()
