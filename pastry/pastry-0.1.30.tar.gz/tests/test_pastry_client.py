import mock
import unittest

from pastry.pastry_client import PastryClient


class PastryClientTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        PastryClient.server = None
        PastryClient.organization = None
        PastryClient.client = None
        PastryClient.keypath = None
        PastryClient.session = mock.MagicMock()

    @mock.patch('pastry.pastry_client.requests.Session')
    def test_initialize(self, session):
        PastryClient.initialize('server', 'organization', 'client', 'keypath', 'verify')
        self.assertEqual(PastryClient.server, 'server')
        self.assertEqual(PastryClient.organization, 'organization')
        self.assertEqual(PastryClient.client, 'client')
        self.assertEqual(PastryClient.keypath, 'keypath')
        self.assertEqual(PastryClient.verify, 'verify')

    @mock.patch('pastry.pastry_client.threading.current_thread')
    @mock.patch('pastry.pastry_client.PastryClient.load_config')
    def test_organization(self, load_config, thread):
        current = PastryClient.organization
        PastryClient.initialized = False
        with PastryClient.context(organization='org'):
            self.assertEqual(thread()._pastry_org, 'org')
        self.assertEqual(PastryClient.organization, current)
        self.assertEqual(load_config.call_count, 1)

    @mock.patch('pastry.pastry_client.PastryClient.initialize')
    @mock.patch('pastry.pastry_client.os')
    @mock.patch('pastry.pastry_client.yaml')
    def test_load_config(self, yaml, os, initialize):
        os.path.join.return_value = 'config_path'
        os.path.exists.return_value = True
        yaml.safe_load.return_value = {
            'server': 'server',
            'organization': 'organization',
            'client': 'client',
            'keypath': 'keypath',
            'verify': 'verify'
        }
        with mock.patch('__builtin__.open', mock.mock_open(read_data='config')):
            PastryClient.load_config()
            initialize.assert_called_with(
                'server', 'organization', 'client', 'keypath', 'verify')
        os.path.exists.return_value = False
        self.assertRaises(ValueError, PastryClient.load_config)

    @mock.patch('pastry.pastry_client.PastryClient.load_config')
    def test_get_url(self, load_config):
        self.assertEqual((None, 'endpoint'), PastryClient.get_url('endpoint'))

    @mock.patch('pastry.pastry_client.signed_headers')
    @mock.patch('pastry.pastry_client.PastryClient.session')
    @mock.patch('pastry.pastry_client.PastryClient.get_url')
    def test_call(self, get_url, session, signed_headers):
        get_url.return_value = ('server', 'path')
        signed_headers.return_value = {'signed': True}
        response = mock.MagicMock()
        response.ok = True
        session.get.return_value = response
        session.post.return_value = response
        PastryClient.call('endpoint')
        session.get.assert_called_with(
            'serverpath',
            headers={'signed': True, 'Connection': 'close'},
            verify=PastryClient.verify
        )
        PastryClient.call('endpoint', method='POST', data={'key': 'value'})
        session.post.assert_called_with(
            'serverpath',
            headers={'signed': True, 'Connection': 'close'},
            json={'key': 'value'},
            verify=PastryClient.verify
        )
        response.ok = False
        self.assertRaises(Exception, PastryClient.call, 'endpoint')

    @mock.patch('pastry.pastry_client.PastryClient.session')
    def test_status(self, session):
        resp = mock.MagicMock()
        resp.ok = True
        resp.json.return_value = {'json': 'content'}
        session.get.return_value = resp
        self.assertEqual(PastryClient.status(), resp.json())
        session.get.assert_called_with(
            '%s/_status' % PastryClient.server,
            headers={'Connection': 'close'},
            verify=PastryClient.verify
        )
        resp.ok = False
        self.assertRaises(Exception, PastryClient.status)
