import mock
import unittest

from pastry.utils import auth


class AuthTestCase(unittest.TestCase):

    @mock.patch('pastry.utils.auth.encode', return_value='encoded')
    @mock.patch('pastry.utils.auth.sha1')
    def test_hashencode(self, sha1, encode):
        self.assertEqual(auth.hashencode('content'), 'encoded')
        sha1.assert_called_with('content')

    @mock.patch('pastry.utils.auth.b64encode')
    def test_encode(self, b64encode):
        expected = [
            u'abcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghij',
            u'abcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghij',
            u'abcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghij',
            u'abcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghij',
            u'abcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghij'
        ]
        b64encode.return_value = ''.join('abcdefghij' * 30)
        self.assertEqual(auth.encode('hashed'), expected)

    @mock.patch('pastry.utils.auth.encode')
    @mock.patch('pastry.utils.auth.sign', return_value='signature')
    def test_authorization_headers(self, sign, encode):
        encode.return_value = ['part1', 'part2', 'part3']
        expected_result = {
            'X-ops-authorization-1': 'part1',
            'X-ops-authorization-2': 'part2',
            'X-ops-authorization-3': 'part3'
        }
        with mock.patch('__builtin__.open', mock.mock_open(read_data='key')):
            self.assertEqual(
                auth.authorization_headers('keypath', 'canonical_source'),
                expected_result
            )

    @mock.patch('pastry.utils.auth.authorization_headers', return_value={'auth':'headers'})
    @mock.patch('pastry.utils.auth.hashencode', return_value=['encoded'])
    @mock.patch('pastry.utils.auth.datetime')
    @mock.patch('pastry.utils.auth.json')
    def test_signed_headers(self, json, datetime, hashencode, authorization_headers):
        now = mock.MagicMock()
        now.strftime.return_value = 'timestamp'
        datetime.utcnow.return_value = now
        expected = {
            'Accept': 'application/json',
            'X-chef-version': '12.8.0',
            'X-ops-content-hash': 'encoded',
            'X-ops-sign': 'version=1.0',
            'X-ops-timestamp': 'timestamp',
            'X-ops-userid': 'client',
            'auth': 'headers'
        }
        auth.signed_headers('client', 'keypath', 'path')
        json.dumps.assert_not_called()
        self.assertEqual(
            auth.signed_headers('client', 'keypath', 'path', data='data'),
            expected
        )
        json.dumps.assert_called_with('data')
