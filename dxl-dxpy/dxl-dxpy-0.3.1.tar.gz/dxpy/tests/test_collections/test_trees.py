import unittest
from treelib import Node, Tree
from dxpy.collections import trees


class TestPathTree(unittest.TestCase):
    def test_basic(self):
        pt = trees.PathTree()
        pt.create_node(name='test', data=1)
        self.assertIsInstance(pt.get_node('/'), Node)
        self.assertEqual(pt.get_data('/test'), 1)

    def test_add_dxdict(self):
        from dxpy.collections.dicts import DXDict
        pt = trees.PathTree()
        pt.create_node(name='test', data=DXDict({'key1': 'value1'}))
        self.assertEqual(pt.get_data('/test')['key1'], 'value1')

    def test_auto_create_mid(self):
        pt = trees.PathTree()
        pt.create_node(name='main', data=1)
        pt.create_node(name='sub', path_parent='/main/test', data=2)
        self.assertEqual(pt.get_data('/main'), 1)
        self.assertIsNone(pt.get_data('/main/test'))
        self.assertEqual(pt.get_data('/main/test/sub'), 2)
