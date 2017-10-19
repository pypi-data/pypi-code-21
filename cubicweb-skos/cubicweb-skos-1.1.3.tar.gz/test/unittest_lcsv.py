# coding: utf-8
# copyright 2015-2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

from logilab.common.testlib import TestCase

import cubicweb.devtools  # noqa set $PYTHONPATH

from cubes.skos import lcsv
from cubes.skos.rdfio import unicode_with_language as ul


class LCSV2RDFTC(TestCase):

    def test_missing_prolog_column(self):
        stream = open(self.datapath('lcsv_example_missing_prolog.csv'))
        with self.assertRaises(lcsv.InvalidLCSVFile) as cm:
            lcsv.LCSV2RDF(stream, '\t', 'utf-8')
        self.assertIn("missing prolog column", str(cm.exception))

    def test_missing_id_column(self):
        stream = open(self.datapath('lcsv_example_missing_id.csv'))
        with self.assertRaises(lcsv.InvalidLCSVFile) as cm:
            lcsv.LCSV2RDF(stream, '\t', 'utf-8')
        self.assertIn("missing $id column", str(cm.exception))

    def test_lcsv_parsing(self):
        fpath = self.datapath('lcsv_example_shortened.csv')
        lcsv2rdf = lcsv.LCSV2RDF(open(fpath), '\t', 'utf-8',
                                 uri_generator=lambda x: x, default_lang='es')
        self.assertEqual(set(list(lcsv2rdf.triples())),
                         set([
                             ('#1', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
                              'http://www.w3.org/2004/02/skos/core#Concept'),
                             ('#1', 'http://www.w3.org/2004/02/skos/core#definition',
                              ul(u"Définition de l'organisation politique de l'organisme,", 'fr')),
                             ('#1', 'http://www.w3.org/2004/02/skos/core#prefLabel',
                              ul(u"Vie politique", 'es')),
                             ('#2', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
                              'http://www.w3.org/2004/02/skos/core#Concept'),
                             ('#2', 'http://www.w3.org/2004/02/skos/core#definition',
                              ul(u"Définition (évolution) des règles de fonctionnement", 'fr')),
                             ('#2', 'http://www.w3.org/2004/02/skos/core#prefLabel',
                              ul(u"Assemblée délibérante", 'es')),
                             ('#2', 'http://www.w3.org/2004/02/skos/core#broader',
                              '#1'),
                             ('#3', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
                              'http://www.w3.org/2004/02/skos/core#Concept'),
                             ('#3', 'http://www.w3.org/2004/02/skos/core#definition',
                              ul(u"Création volontaire ou en application de la loi", 'fr')),
                             ('#3', 'http://www.w3.org/2004/02/skos/core#prefLabel',
                              ul(u"Instances consultatives", 'es')),
                             ('#3', 'http://www.w3.org/2004/02/skos/core#broader',
                              '#1'),
                             ('#4', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
                              'http://www.w3.org/2004/02/skos/core#Concept'),
                             ('#4', 'http://www.w3.org/2004/02/skos/core#definition',
                              ul(u"Fonction de définition d'objectifs à long terme", 'fr')),
                             ('#4', 'http://www.w3.org/2004/02/skos/core#prefLabel',
                              ul(u"Pilotage de l'organisation", 'es')),
                             ('#5', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
                              'http://www.w3.org/2004/02/skos/core#Concept'),
                             ('#5', 'http://www.w3.org/2004/02/skos/core#definition',
                              ul(u"Définition du projet d'administration", 'fr')),
                             ('#5', 'http://www.w3.org/2004/02/skos/core#prefLabel',
                              ul(u"Pilotage de Bordeaux Metropole", 'es')),
                             ('#5', 'http://www.w3.org/2004/02/skos/core#broader',
                              '#4')
                         ]))


if __name__ == "__main__":
    from unittest import main
    main()
