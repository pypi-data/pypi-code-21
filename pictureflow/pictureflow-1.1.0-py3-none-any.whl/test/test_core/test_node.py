from test.context import pf

import unittest


class TypedNode(pf.core.Node):
    _input_types = [str]
    _output_type = int

    def apply(self, in_str):
        yield len(in_str)


class UntypedNode(pf.core.Node):

    def apply(self, itm):
        yield len(itm)


class TestNodeInitialization(unittest.TestCase):

    def test_node_sets_id_properly(self):
        node_id = 'hello'

        n = UntypedNode(id=node_id)
        self.assertEqual(n.id, node_id)

    def test_node_defaults_id_properly(self):
        expected_id = 'node'

        n = UntypedNode()
        self.assertEqual(n.id, expected_id)
