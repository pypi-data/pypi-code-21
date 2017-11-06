###############################################################################
#
#   Copyright: (c) 2015 Carlo Sbraccia
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
###############################################################################

from onyx.core.database.ufo_base import UfoBase
from onyx.core.database.ufo_fields import IntField

from onyx.core.depgraph.graph_api import ValueType, CreateInMemory
from onyx.core.depgraph.graph_api import GetVal, GetNode, InvalidateNode
from onyx.core.utils.unittest import OnyxTestCase

import unittest


###############################################################################
class Fibonacci(UfoBase):
    fib0 = IntField(default=0)
    fib1 = IntField(default=1)

    # -------------------------------------------------------------------------
    @ValueType("Callable")
    def fib(self, graph, k):
        if k == 0:
            return graph(self, "fib0")
        elif k == 1:
            return graph(self, "fib1")
        else:
            return graph(self, "fib", k-1) + graph(self, "fib", k-2)


###############################################################################
class TestFibonacci(OnyxTestCase):
    # -------------------------------------------------------------------------
    def setUp(self):
        super().setUp()
        self.instance = CreateInMemory(Fibonacci(Name="fib"))
        self.name = self.instance.Name

    # -------------------------------------------------------------------------
    def tearDown(self):
        super().tearDown()

    # -------------------------------------------------------------------------
    def test_initial_values(self):
        self.assertEqual(GetVal(self.name, "fib0"), 0)
        self.assertEqual(GetVal(self.name, "fib1"), 1)

    # -------------------------------------------------------------------------
    def test_seq(self):
        self.assertEqual(GetVal(self.name, "fib", 0), 0)
        self.assertEqual(GetVal(self.name, "fib", 1), 1)
        self.assertEqual(GetVal(self.name, "fib", 2), 1)
        self.assertEqual(GetVal(self.name, "fib", 3), 2)
        self.assertEqual(GetVal(self.name, "fib", 4), 3)
        self.assertEqual(GetVal(self.name, "fib", 5), 5)
        self.assertEqual(GetVal(self.name, "fib", 6), 8)
        self.assertEqual(GetVal(self.name, "fib", 7), 13)
        self.assertEqual(GetVal(self.name, "fib", 8), 21)
        self.assertEqual(GetVal(self.name, "fib", 9), 34)

    # -------------------------------------------------------------------------
    def test_graph(self):
        """
        Calculate a large fibonacci number and then perform tests on the
        generated graph.
        """
        self.assertEqual(GetVal(self.name, "fib", 10), 55)

        parents = {('fib', 'fib', (9,)), ('fib', 'fib', (10,))}
        children = {('fib', 'fib', (6,)), ('fib', 'fib', (7,))}
        node_8 = GetNode(self.name, "fib", (8,))

        self.assertTrue(node_8.valid)
        self.assertEqual(node_8.value, 21)
        self.assertEqual(node_8.parents, parents)
        self.assertEqual(node_8.children, children)

        # --- invalidate node 8 and check again the state of the graph
        InvalidateNode(self.name, "fib", (8,))

        # --- invalidation sets the node to invalid, but doesn't afftect the
        #     topology of the graph. Such changes take place just before
        #     recalculating the value of an invalid node (the graph is
        #     extremely lazy).
        self.assertFalse(node_8.valid)
        self.assertEqual(node_8.value, 21)
        self.assertEqual(node_8.parents, parents)
        self.assertEqual(node_8.children, children)


if __name__ == "__main__":
    from onyx.core.utils.unittest import UseEphemeralDbs
    with UseEphemeralDbs():
        unittest.main(failfast=True)
