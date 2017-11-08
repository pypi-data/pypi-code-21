import mock
import unittest

from pastry.resources.nodes import Nodes


class NodesTestCase(unittest.TestCase):

    @mock.patch('pastry.resources.nodes.Base.exists', return_value=True)
    def test_exists(self, base):
        self.assertEqual(Nodes.exists('node'), True)

    @mock.patch('pastry.resources.nodes.Base.get_acl', return_value='acl')
    def test_get_acl(self, base):
        self.assertEqual(Nodes.get_acl('node'), 'acl')

    @mock.patch('pastry.resources.nodes.Base.set_permission', return_value={})
    def test_set_permission(self, base):
        self.assertEqual(Nodes.set_permission(
            'node',
            'permission',
            {}
        ), {})
