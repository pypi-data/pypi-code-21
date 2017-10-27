import unittest
from dxpy.graph.depens import DenpensGraph


class TestDepensGraph(unittest.TestCase):
    def test_init(self):
        g = DenpensGraph([1, 2, 3], [None, 1, 1])
        self.assertEqual(g.g.nodes(), [1, 2, 3])
        self.assertEqual(g.g.successors(1), [])
        self.assertEqual(g.g.successors(2), [1])
        self.assertEqual(g.g.successors(3), [1])

    def test_init_2(self):
        g = DenpensGraph([], [])
        self.assertEqual(g.g.nodes(), [])

    def test_add_node(self):
        g = DenpensGraph([], [])
        self.assertEqual(g.g.nodes(), [])
        g.add_node(1)
        self.assertEqual(g.g.nodes(), [1])

    def test_remove_node(self):
        g = DenpensGraph([1], [None])
        self.assertEqual(g.g.nodes(), [1])
        g.remove_node(1)
        self.assertEqual(g.g.nodes(), [])

    def test_free_nodes(self):
        g = DenpensGraph([1, 2, 3], [None, 1, None])
        self.assertEqual(g.free_nodes(), [1, 3])

    def test_nodes(self):
        g = DenpensGraph([1, 2, 3], [None] * 3)
        self.assertEqual(g.nodes(), [1, 2, 3])

    def test_is_depens_on(self):
        g = DenpensGraph([1, 2, 3], [None, 1, None])
        self.assertTrue(g.is_depens_on(2, 1))
        self.assertFalse(g.is_depens_on(3, 1))

    def test_dependencies(self):
        g = DenpensGraph([1, 2, 3], [None, None, [1, 2]])
        self.assertEqual(g.dependencies(3), [1, 2])
