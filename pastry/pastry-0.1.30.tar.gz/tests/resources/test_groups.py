import mock
import unittest

from pastry.resources.groups import Groups


class GroupsTestCase(unittest.TestCase):

    @mock.patch('pastry.resources.groups.Base.index', return_value='index')
    def test_index(self, base):
        self.assertEqual(Groups.index(), 'index')

    @mock.patch('pastry.resources.groups.Base.get', return_value='group')
    def test_get(self, base):
        self.assertEqual(Groups.get('groupname'), 'group')

    @mock.patch('pastry.resources.groups.Base.create', return_value='group')
    def test_create(self, base):
        self.assertEqual(Groups.create({}), 'group')

    @mock.patch('pastry.resources.groups.Base.update', return_value='group')
    def test_update(self, base):
        self.assertEqual(Groups.update('group', {}), 'group')

    @mock.patch('pastry.resources.groups.Base.delete', return_value='group')
    def test_delete(self, base):
        self.assertEqual(Groups.delete('group'), 'group')

    @mock.patch('pastry.resources.groups.Base.exists', return_value=True)
    def test_exists(self, base):
        self.assertEqual(Groups.exists('group'), True)
