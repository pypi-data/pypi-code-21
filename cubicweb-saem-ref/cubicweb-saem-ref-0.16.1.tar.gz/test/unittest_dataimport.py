# coding: utf-8
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
"""cubicweb-saem_ref unit tests for dataimport"""

from os.path import basename

from cubicweb.dataimport.importer import SimpleImportLog
from cubicweb.devtools.testlib import CubicWebTC

import testutils


class EACDataImportTC(CubicWebTC):

    def setup_database(self):
        with self.admin_access.repo_cnx() as cnx:
            self.create_user(cnx, u'bob', ('users', ),
                             authority=testutils.authority_with_naa(cnx))
            cnx.commit()

    def test_imported_activities(self):
        fpath = self.datapath('EAC', 'FRAD033_EAC_dataimport.xml')
        with self.new_access(u'bob').cnx() as cnx:
            import_log = SimpleImportLog(basename(fpath))
            cnx.call_service(
                'eac.import', stream=fpath, import_log=import_log,
                raise_on_error=True)
            rset = cnx.find('AuthorityRecord', isni=u'22330001300016')
            record = rset.one()
            rset = cnx.execute('Any A WHERE A generated X, X eid %(x)s', {'x': record.eid})
            # Two activities imported from EAC-CPF file, one created by our hook.
            self.assertEqual(len(rset), 3)


if __name__ == '__main__':
    import unittest
    unittest.main()
