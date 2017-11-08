import mock
import unittest

from pastry.resources.base import Base
from pastry.exceptions import HttpError


class BaseTestCase(unittest.TestCase):

    def test_base_url(self):
        Base._base_url = 'url'
        self.assertEqual(Base.base_url(), 'url')
        Base._base_url = None
        self.assertRaises(ValueError, Base.base_url)

    @mock.patch('pastry.resources.base.Base.base_url', return_value='url')
    @mock.patch('pastry.resources.base.PastryClient')
    def test_index(self, pastry_client, base_url):
        pastry_client.call.return_value = 'result'
        self.assertEqual(Base.index(), 'result')
        pastry_client.call.assert_called_with('url')

    @mock.patch('pastry.resources.base.Base.base_url', return_value='url')
    @mock.patch('pastry.resources.base.PastryClient')
    def test_get(self, pastry_client, base_url):
        pastry_client.call.return_value = 'result'
        self.assertEqual(Base.get('instance'), 'result')
        pastry_client.call.assert_called_with('url/instance')

    @mock.patch('pastry.resources.base.Base.base_url', return_value='url')
    @mock.patch('pastry.resources.base.PastryClient')
    def test_create(self, pastry_client, base_url):
        pastry_client.call.return_value = 'result'
        self.assertEqual(Base.create({}), 'result')
        pastry_client.call.assert_called_with('url', method='POST', data={})

    @mock.patch('pastry.resources.base.Base.base_url', return_value='url')
    @mock.patch('pastry.resources.base.PastryClient')
    def test_update(self, pastry_client, base_url):
        pastry_client.call.return_value = 'result'
        self.assertEqual(Base.update('instance', {}), 'result')
        pastry_client.call.assert_called_with('url/instance', method='PUT', data={})

    @mock.patch('pastry.resources.base.Base.base_url', return_value='url')
    @mock.patch('pastry.resources.base.PastryClient')
    def test_delete(self, pastry_client, base_url):
        pastry_client.call.return_value = 'result'
        self.assertEqual(Base.delete('instanceid'), 'result')
        pastry_client.call.assert_called_with('url/instanceid', method='DELETE')

    @mock.patch('pastry.resources.base.Base.get')
    def test_exists(self, get):
        get.return_value = {'instanceid': 'id'}
        self.assertEqual(Base.exists('instanceid'), True)
        get.assert_called_with('instanceid')
        get.side_effect = HttpError('message', 404)
        self.assertEqual(Base.exists('instanceid'), False)

    def test_escape_query(self):
        self.assertEqual(
            Base.escape_query('test%query%string'),
            'test%%query%%string'
        )

    @mock.patch('pastry.resources.base.Base.base_url', return_value='url')
    @mock.patch('pastry.resources.base.PastryClient')
    def test_get_acl(self, pastry_client, base_url):
        pastry_client.call.return_value = 'result'
        self.assertEqual(Base.get_acl('instance'), 'result')
        pastry_client.call.assert_called_with('url/instance/_acl')

    @mock.patch('pastry.resources.base.Base.base_url', return_value='url')
    @mock.patch('pastry.resources.base.PastryClient')
    def test_set_permission(self, pastry_client, base_url):
        pastry_client.call.return_value = 'result'
        self.assertEqual(Base.set_permission('instance', 'permission', {}), 'result')
        pastry_client.call.assert_called_with(
            'url/instance/_acl/permission',
            method='PUT',
            data={'permission': {}}
        )
