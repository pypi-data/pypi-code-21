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
from onyx.core.database.objdb_api import AddObj, GetObj, DelObj
from onyx.core.depgraph.graph import GraphNode, SettableNode, PropertyNode
from onyx.core.depgraph.graph_api import ValueType, GetNode
from onyx.core.utils.unittest import OnyxTestCase
from onyx.core import database as onyx_db

import unittest

X = 1
Y = 2


###############################################################################
class UfoSimple(UfoBase):
    x = IntField(default=X)
    y = IntField(default=Y)

    # -------------------------------------------------------------------------
    @ValueType()
    def getsum(self, graph):
        return graph(self, "x") + graph(self, "y")

    # -------------------------------------------------------------------------
    def not_a_vt(self):
        pass


###############################################################################
class TestSimple(OnyxTestCase):
    # -------------------------------------------------------------------------
    def setUp(self):
        super().setUp()
        self.instance = AddObj(UfoSimple(Name="simple"))
        self.name = self.instance.Name

    # -------------------------------------------------------------------------
    def tearDown(self):
        DelObj(self.name)
        super().tearDown()

    # -------------------------------------------------------------------------
    def test_references(self):
        # --- here we check that the object reference contained in each node
        #     is consistent with what is in the cache of the database client
        #     and survives refreshing such cache
        node = GetNode(self.name, "Name")
        ref_id = id(node.obj_ref())

        self.assertEqual(ref_id, id(self.instance))
        self.assertEqual(ref_id, id(GetObj(self.name)))

        del self.instance

        self.assertEqual(ref_id, id(GetObj(self.name)))
        self.assertEqual(ref_id, id(GetObj(self.name, True)))

        del onyx_db.obj_clt[self.name]
        with self.assertRaises(KeyError):
            onyx_db.obj_clt[self.name]

        self.assertNotEqual(ref_id, id(node.obj_ref()))  # obj_ref is None
        self.assertNotEqual(ref_id, id(GetObj(self.name, True)))

    # -------------------------------------------------------------------------
    def test_create_nodes(self):
        # --- create a node that points to "Name"
        node = GetNode(self.name, "Name")
        self.assertTrue(isinstance(node, SettableNode))
        self.assertEqual(node.get_value(), self.name)

        # --- create a node that points to "Version"
        node = GetNode(self.name, "Version")
        self.assertTrue(isinstance(node, SettableNode))
        self.assertEqual(node.get_value(), 0)

        # --- create a node that points to "StoredAttrs"
        node = GetNode(self.name, "StoredAttrs")
        self.assertTrue(isinstance(node, GraphNode))
        self.assertEqual(node.get_value(), self.instance.StoredAttrs)

        # --- create a node that points to a method decorated by ValueType
        node = GetNode(self.name, "getsum")
        self.assertTrue(isinstance(node, PropertyNode))
        self.assertEqual(node.get_value(), self.instance.getsum)

        # --- create a node that points to a method that is not a ValueType
        with self.assertRaises(AttributeError):
            GetNode(self.name, "not_a_vt")

        # --- create a node that points to a non-existing method
        with self.assertRaises(AttributeError):
            GetNode(self.name, "not_there")

    # -------------------------------------------------------------------------
    def test_clone(self):
        # --- create a node that points to "StoredAttrs" and make a clone
        node1 = GetNode(self.name, "StoredAttrs")
        node2 = node1.clone()

        # --- test that the two nodes are different objects but return the same
        #     value and share the same reference to the underlying object
        self.assertNotEqual(node1, node2)
        self.assertEqual(node1.get_value(), node2.get_value())
        self.assertEqual(node1.obj_ref, node2.obj_ref)
        self.assertIs(node1.obj_ref, node2.obj_ref)
        self.assertIs(node1.obj_ref(), self.instance)
        self.assertIs(node2.obj_ref(), self.instance)

        # --- create a node that points to "sum" and make a clone
        node1 = GetNode(self.name, "getsum")
        node2 = node1.clone()

        # --- test that the two nodes are different objects but return the same
        #     value and share the same reference to the underlying object
        self.assertNotEqual(node1, node2)
        self.assertEqual(node1.get_value(), node2.get_value())
        self.assertEqual(node1.obj_ref, node2.obj_ref)
        self.assertIs(node1.obj_ref, node2.obj_ref)
        self.assertIs(node1.obj_ref(), self.instance)
        self.assertIs(node2.obj_ref(), self.instance)

        # --- test that invalidation only affects a specific node
        x = GetNode(self.name, "x")
        x.value = 6

        node1.invalidate()
        self.assertFalse(node1.valid)
        self.assertTrue(node2.valid)
        self.assertEqual(node1.get_value(), 6 + Y)
        self.assertEqual(node2.get_value(), X + Y)
        node2.invalidate()
        self.assertFalse(node2.valid)
        self.assertEqual(node2.get_value(), 6 + Y)


if __name__ == "__main__":
    from onyx.core.utils.unittest import UseEphemeralDbs
    with UseEphemeralDbs():
        unittest.main(failfast=True)
