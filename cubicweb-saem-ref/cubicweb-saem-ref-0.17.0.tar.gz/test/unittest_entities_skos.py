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
"""cubicweb-saem_ref unit tests for entities.skos"""

from cubicweb.devtools.testlib import CubicWebTC

import testutils


class ConceptSchemeTC(CubicWebTC):

    def test_optimized_top_concepts(self):
        with self.admin_access.cnx() as cnx:
            scheme = cnx.create_entity('ConceptScheme', ark_naa=testutils.naa(cnx))
            c1 = scheme.add_concept(u'blah')
            c1label = c1.preferred_label[0]
            c2 = c1.add_concept(u'blob')
            cnx.commit()
        # open a fresh connection to ensure all cnx caches are empty
        with self.admin_access.cnx() as cnx:
            scheme = cnx.entity_from_eid(scheme.eid)
            scheme.top_concepts_rset  # simply access to the property
            cache = cnx.transaction_data['ecache']
            self.assertIn(c1.eid, cache)
            self.assertIn(c1label.eid, cache)
            # trick to test the entity's caches: kill its ._cw attribute and
            # attempt to fetch attributes/relations
            c1 = cache[c1.eid]
            del c1._cw
            self.assertEqual([x.eid for x in c1.reverse_broader_concept],
                             [c2.eid])
            self.assertEqual([x.eid for x in c1.preferred_label],
                             [c1label.eid])
            self.assertEqual(set(c1.cw_attr_cache), set(['ark', 'cwuri', 'definition', 'example']))
            c1label = cache[c1label.eid]
            self.assertEqual(set(c1label.cw_attr_cache), set(['kind', 'label', 'language_code']))


if __name__ == '__main__':
    import unittest
    unittest.main()
