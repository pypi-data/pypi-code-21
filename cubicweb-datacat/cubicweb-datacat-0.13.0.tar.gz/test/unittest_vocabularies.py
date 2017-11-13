# -*- coding: utf-8 -*-
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

"""cubicweb-datacat unit tests for vocabulary processing."""

import json

from rdflib.compare import (
    graph_diff,
    to_isomorphic,
)

from cubicweb.devtools.testlib import BaseTestCase

from cubes.datacat.vocabularies import (
    capitalized_eurovoc_domain,
    eurovoc_domains,
    simplify_eurovoc,
)
from cubes.skos import rdfio


class EurovocTC(BaseTestCase):
    """Test case for Eurovoc manipulation."""

    def test_capitalized_eurovoc_domain(self):
        """Check that Eurovoc domain names case are correctly computed."""
        self.assertEqual(capitalized_eurovoc_domain(u'04 VIE POLITIQUE'), u'04 Vie politique')
        self.assertEqual(capitalized_eurovoc_domain(u'56 AGRICULTURE, SYLVICULTURE ET PÊCHE'),
                         u'56 Agriculture, sylviculture et pêche')
        self.assertEqual(capitalized_eurovoc_domain(u'32 ÉDUCATION ET COMMUNICATION'),
                         u'32 Éducation et communication')

    def test_eurovoc_simplification(self):
        """Check that correct graph is produced from Eurovoc simplification."""
        eurovoc_graph = rdfio.default_graph()
        new_graph = rdfio.default_graph()
        with open(self.datapath('eurovoc_skos.n3')) as f:
            eurovoc_graph.load(f, rdf_format='n3')
        simplify_eurovoc(eurovoc_graph, new_graph)
        expected_graph = rdfio.default_graph()
        with open(self.datapath('eurovoc_skos_simple.n3')) as f:
            expected_graph.load(f, rdf_format='n3')
        iso1 = to_isomorphic(new_graph._graph)
        iso2 = to_isomorphic(expected_graph._graph)
        in_both, in_first, in_second = graph_diff(iso1, iso2)
        self.assertEqual(iso1, iso2,
                         u'RDF graphs are not the same:\n'
                         '* actual:\n{0}\n\n'
                         '* expected:\n{1}'.format(sorted(in_first.serialize(format='n3')),
                                                   sorted(in_second.serialize(format='n3'))))

    def test_eurovoc_domains(self):
        """Check that correct dictionary is produced from Eurovoc domains."""
        simplified_graph = rdfio.default_graph()
        with open(self.datapath('eurovoc_skos_simple.n3')) as f:
            simplified_graph.load(f, rdf_format='n3')
        actual_dict = eurovoc_domains(simplified_graph)
        with open(self.datapath('eurovoc_domains.json')) as f:
            expected_dict = json.load(f)
        self.assertEqual(actual_dict, expected_dict)


if __name__ == '__main__':
    import unittest
    unittest.main()
