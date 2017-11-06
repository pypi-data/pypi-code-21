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
from onyx.core.database.ufo_fields import StringField

from onyx.core.depgraph.graph_api import ValueType, CreateInMemory
from onyx.core.depgraph.graph_api import GetVal, InvalidateNode, ChildrenSet
from onyx.core.depgraph.graph_scopes import EvalBlock, GraphScope

from onyx.core.utils.unittest import OnyxTestCase

import unittest


###############################################################################
class Diamond(UfoBase):
    A = StringField(default="A")

    # -------------------------------------------------------------------------
    @ValueType()
    def B(self, graph):
        return graph(self, "A") + "B"

    # -------------------------------------------------------------------------
    @ValueType()
    def C(self, graph):
        return graph(self, "A") + "C"

    # -------------------------------------------------------------------------
    @ValueType()
    def D(self, graph):
        return graph(self, "B") + graph(self, "C")


###############################################################################
class TestDiamond(OnyxTestCase):
    # -------------------------------------------------------------------------
    def setUp(self):
        super().setUp()
        self.instance = CreateInMemory(Diamond(Name="diamond"))
        self.name = self.instance.Name

    # -------------------------------------------------------------------------
    def tearDown(self):
        super().tearDown()

    # -------------------------------------------------------------------------
    def test_leaves(self):
        self.assertEqual(GetVal(self.name, "A"), "A")

    # -------------------------------------------------------------------------
    def test_errors(self):
        pass
        # self.assertRaises(RuntimeError, GetVal, self.name, "xxx")

    # -------------------------------------------------------------------------
    def test_values(self):
        self.assertEqual(GetVal(self.name, "B"), "AB")
        self.assertEqual(GetVal(self.name, "C"), "AC")
        self.assertEqual(GetVal(self.name, "D"), "ABAC")

    # -------------------------------------------------------------------------
    def test_children(self):
        self.assertEqual(ChildrenSet((self.name, "D"), "A"), {"diamond"})

    # -------------------------------------------------------------------------
    def test_eval_block(self):
        self.test_values()

        with EvalBlock() as eb:
            eb.change_value(self.name, "A", "XXX")
            self.assertEqual(GetVal(self.name, "B"), "XXXB")
            self.assertEqual(GetVal(self.name, "C"), "XXXC")
            self.assertEqual(GetVal(self.name, "D"), "XXXBXXXC")

            InvalidateNode(self.name, "A")

            self.test_values()

            eb.change_value(self.name, "C", "XXX")
            self.assertEqual(GetVal(self.name, "D"), "ABXXX")

        self.test_values()

    # -------------------------------------------------------------------------
    def test_graph_scope(self):
        self.test_values()

        scope = GraphScope()
        scope.change_value(self.name, "A", "XXX")

        self.test_values()

        with scope:
            self.assertEqual(GetVal(self.name, "B"), "XXXB")
            self.assertEqual(GetVal(self.name, "C"), "XXXC")
            self.assertEqual(GetVal(self.name, "D"), "XXXBXXXC")

            InvalidateNode(self.name, "A")

            self.test_values()

            scope.change_value(self.name, "C", "XXX")
            self.assertEqual(GetVal(self.name, "D"), "ABXXX")

        self.test_values()

        with scope:
            self.assertEqual(GetVal(self.name, "D"), "ABXXX")


if __name__ == "__main__":
    from onyx.core.utils.unittest import UseEphemeralDbs
    with UseEphemeralDbs():
        unittest.main(failfast=True)
