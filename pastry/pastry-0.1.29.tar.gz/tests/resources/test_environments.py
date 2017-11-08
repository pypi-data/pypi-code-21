import mock
import unittest

from pastry.resources.environments import Environments


class EnvironmentsTestCase(unittest.TestCase):

    @mock.patch('pastry.resources.environments.Base.index',
        return_value='index')
    def test_index(self, base):
        self.assertEqual(Environments.index(), 'index')

    @mock.patch('pastry.resources.environments.Base.get',
        return_value='environment')
    def test_get(self, base):
        self.assertEqual(Environments.get('environmentname'), 'environment')

    @mock.patch('pastry.resources.environments.Base.create',
        return_value='environment')
    def test_create(self, base):
        self.assertEqual(Environments.create({}), 'environment')

    @mock.patch('pastry.resources.environments.Base.update',
        return_value='environment')
    def test_update(self, base):
        self.assertEqual(Environments.update('environment', {}), 'environment')

    @mock.patch('pastry.resources.environments.Base.delete',
        return_value='environment')
    def test_delete(self, base):
        self.assertEqual(Environments.delete('environment'), 'environment')

    @mock.patch('pastry.resources.environments.Base.exists',
        return_value=True)
    def test_exists(self, base):
        self.assertEqual(Environments.exists('environment'), True)
