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
from onyx.core.depgraph.graph_api import GetVal, SetVal, GetNode
from onyx.core.depgraph.graph_scopes import EvalBlock, GraphScope
from onyx.core.utils.unittest import OnyxTestCase

import unittest

FIXED = 1


###############################################################################
class UfoClosure(UfoBase):
    fixed = IntField(default=FIXED)

    # -------------------------------------------------------------------------
    @ValueType()
    def add_to_fixed(self, graph):
        def adder(x):
            return x + graph(self, "fixed")
        return adder


###############################################################################
class TestClosure(OnyxTestCase):
    # -------------------------------------------------------------------------
    def setUp(self):
        super().setUp()
        self.instance = CreateInMemory(UfoClosure(Name="closure"))
        self.name = self.instance.Name

    # -------------------------------------------------------------------------
    def test_closure(self):
        self.assertEqual(GetVal(self.name, "fixed"), FIXED)
        self.assertEqual(GetVal(self.name, "add_to_fixed")(10), 10 + FIXED)

        # --- inspect the node before and after changing the value of "fixed"
        adder = GetNode(self.name, "add_to_fixed")
        self.assertTrue(adder.valid)

        SetVal(self.name, "fixed", 666)
        self.assertFalse(adder.valid)

        self.assertEqual(GetVal(self.name, "add_to_fixed")(10), 10 + 666)
        self.assertTrue(adder.valid)

    # -------------------------------------------------------------------------
    def test_invalidation_within_EvalBlock(self):
        self.assertEqual(GetVal(self.name, "add_to_fixed")(10), 10 + FIXED)
        adder = GetNode(self.name, "add_to_fixed")
        self.assertTrue(adder.valid)

        with EvalBlock() as eb:
            self.assertTrue(adder.valid)
            eb.change_value(self.name, "fixed", 666)
            self.assertFalse(adder.valid)

            self.assertEqual(GetVal(self.name, "add_to_fixed")(10), 10 + 666)
            self.assertTrue(adder.valid)

        self.assertFalse(adder.valid)

    # -------------------------------------------------------------------------
    def test_invalidation_within_GraphScope(self):
        self.assertEqual(GetVal(self.name, "add_to_fixed")(10), 10 + FIXED)
        outer_adder = GetNode(self.name, "add_to_fixed")
        self.assertTrue(outer_adder.valid)

        with GraphScope() as scope:
            # --- fetch node again from within the graph scope: this the same
            #     as the outer node
            inner_adder = GetNode(self.name, "add_to_fixed")

            self.assertEqual(id(inner_adder), id(outer_adder))
            self.assertTrue(outer_adder.valid)
            self.assertTrue(inner_adder.valid)
            self.assertEqual(inner_adder.value, outer_adder.value)

            # --- we now change the graph from withing a scope and the two
            #     nodes start living separate lives
            scope.change_value(self.name, "fixed", 666)

            inner_adder = GetNode(self.name, "add_to_fixed")

            self.assertTrue(id(inner_adder) != id(outer_adder))
            self.assertTrue(outer_adder.valid)
            self.assertFalse(inner_adder.valid)

            self.assertEqual(GetVal(self.name, "add_to_fixed")(10), 10 + 666)

        self.assertTrue(outer_adder.valid)
        self.assertEqual(GetVal(self.name, "add_to_fixed")(10), 10 + FIXED)


if __name__ == "__main__":
    from onyx.core.utils.unittest import UseEphemeralDbs
    with UseEphemeralDbs():
        unittest.main(failfast=True)
