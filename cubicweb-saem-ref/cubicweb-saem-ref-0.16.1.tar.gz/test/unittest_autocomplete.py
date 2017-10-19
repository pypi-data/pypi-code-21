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
"""cubicweb-saem_ref unit tests for views"""

import json

from logilab.common import flatten

from cubicweb.devtools import PostgresApptestConfiguration
from cubicweb.devtools.testlib import CubicWebTC

from cubicweb_saem_ref.views.autocompletesearch import words_matching_term

import testutils


def setUpModule():
    testutils.startpgcluster(__file__)


def sql(cnx, string, param=None):
    return cnx.system_sql(string, param).fetchall()


class AutocompleteSearchTC(CubicWebTC):
    configcls = PostgresApptestConfiguration

    def test_syncro_concepts(self):
        with self.admin_access.client_cnx() as cnx:
            self.assertFalse(sql(cnx, 'SELECT * from words WHERE word=%(w)s;',
                                 {'w': u'déclaration'}))
            scheme = cnx.create_entity('ConceptScheme', title=u'my thesaurus',
                                       ark_naa=testutils.naa(cnx))
            concept = scheme.add_concept(label=u'Déclaration universelle', language_code=u'fr',
                                         definition=u"Déclaration des droits de l'homme")
            scheme.add_concept(label=u'The Universal Declaration', language_code=u'fr',
                               definition=u'Declaration of human rights and citizen')
            other_scheme = cnx.create_entity('ConceptScheme', ark_naa=testutils.naa(cnx))
            other_scheme.add_concept(u'25 ans - secret statistique')
            other_scheme.add_concept(
                u'100 ans- personnes mineures',
                definition=(u'Documents évoquant des personnes mineures : '
                            u'statistiques, enquêtes de la police judiciaire, ...')
            )
            yet_another_scheme = cnx.create_entity('ConceptScheme', ark_naa=testutils.naa(cnx))
            yet_another_scheme.add_concept(
                u'fmt/210', definition=u'Statistica Report File Statistica Report File')
            cnx.commit()

            all_words = flatten(sql(cnx, 'SELECT word FROM words'))
            for word in (u'droits', u'd\xe9claration', u'citizen', u'rights'):
                self.assertIn(word, all_words)

        with self.admin_access.web_request() as req:
            self.assertEqual(words_matching_term(req, u'déclaration'),
                             [(u'd\xe9claration', u'Concept'),
                              (u'declaration', u'Concept')])
            self.assertEqual(words_matching_term(req, u'statisti'),
                             [(u'statistica', u'Concept'),
                              (u'statistique', u'Concept'),
                              (u'statistiques', u'Concept')])
            self.assertEqual(words_matching_term(req, 'rspons'), [])
            concept = req.cnx.entity_from_eid(concept.eid)
            concept.preferred_label[0].cw_set(label=u'Loi renseignement')
            concept.cw_set(definition=u'''L'Assemblée et le Sénat se sont mis d'accord, mardi 16
            juin, sur une version définitive de la loi renseignement. Un texte voté dans une sorte
            d'indifférence générale et qui dote la France d'une des lois les plus intrusives
            d’Europe.''')
            req.cnx.commit()
            self.assertEqual(words_matching_term(req, 'déclaration'),
                             [(u'declaration', u'Concept')])

    def _add_some_content(self):
        with self.admin_access.client_cnx() as cnx:
            testutils.authority_record(cnx, u'Secret record')
            scheme = cnx.create_entity('ConceptScheme', ark_naa=testutils.naa(cnx))
            scheme.add_concept(u'Top secret')
            cnx.commit()

    def _search(self, **formdata):
        formdata.setdefault('facetrql', '')
        with self.admin_access.web_request(**formdata) as req:
            view = self.vreg['views'].select('search-autocomplete', req)
            return json.loads(view.render())

    def test_empty_search(self):
        words = self._search(term='secretos', all='secretos')
        self.assertEqual(words, [])

    def test_search(self):
        self._add_some_content()
        words = self._search(term='secret', all='secret')
        self.assertEqual(words, [{'label': 'secret : AuthorityRecord, Concept', 'value': 'secret'}])
        words = self._search(term='secret', all='record secret')
        self.assertEqual(words, [{'label': 'secret : AuthorityRecord', 'value': 'secret'}])

    def test_facetted_search(self):
        self._add_some_content()
        words = self._search(term='secret', all='secret',
                             facetrql='Any X WHERE X is AuthorityRecord')
        self.assertEqual(words, [{'label': 'secret : AuthorityRecord', 'value': 'secret'}])


if __name__ == '__main__':
    import unittest
    unittest.main()
