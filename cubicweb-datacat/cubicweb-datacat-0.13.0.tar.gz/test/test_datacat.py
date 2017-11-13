# copyright 2014 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

"""cubicweb-datacat automatic tests"""

from cubicweb.devtools import (
    PostgresApptestConfiguration,
    startpgcluster,
    stoppgcluster,
    testlib,
)

from cubes.datacat import (
    cwsource_pull_data,
    vocabularies,
)


def setUpModule():
    startpgcluster(__file__)


def tearDownModule():
    stoppgcluster(__file__)


class VocabularyImportTC(testlib.CubicWebTC):
    """Functional tests ensuring concept schemes got properly imported.
    """

    configcls = PostgresApptestConfiguration

    def test_adms(self):
        """Just check one import from SKOSSource"""
        scheme_names = (
            'assettype',
            'interoperabilitylevel',
            'licencetype',
            'publishertype',
            'representationtechnique',
            'status',
        )
        with self.admin_access.repo_cnx() as cnx:
            rset = cnx.execute(
                'Any X WHERE S through_cw_source X, S url LIKE "%ADMS%"')
            assert rset
            for eid, in rset.rows:
                cwsource_pull_data(self.repo, eid)
            rset = cnx.execute(
                'Any X WHERE X is ConceptScheme, X cwuri IN ({0})'.format(
                    ','.join('"http://purl.org/adms/{0}/1.0"'.format(n)
                             for n in scheme_names)
                )
            )
        self.assertEqual(len(rset), len(scheme_names))

    def test_mediatypes(self):
        """Check import of concepts from IANA "Media Types"."""
        with self.admin_access.repo_cnx() as cnx:
            vocabularies.media_types_import(cnx, media_types=('audio', 'image'))
            cnx.commit()
            rset = cnx.execute(
                'Any COUNT(X) WHERE X in_scheme C, C cwuri "{0}"'.format(
                    'http://www.iana.org/assignments/media-types/media-types.xml')
            )
            self.assertEqual(rset[0][0], 192)


if __name__ == '__main__':
    import unittest
    unittest.main()
