import unittest
from dwolla import oauth, constants
from mock import MagicMock


class OAuthTest(unittest.TestCase):
    def setUp(self):
        oauth.r._get = MagicMock()
        oauth.r._post = MagicMock()
        oauth.r._post_without_token = MagicMock()
        constants.client_id = "SOME ID"
        constants.client_secret = "SOME SECRET"
        constants.access_token = "AN OAUTH TOKEN"
        constants.oauth_scope = "Balance|AccountInfo"

    def testgenauthurl(self):
        self.assertEqual(oauth.genauthurl(), 'https://sandbox.dwolla.com/oauth/v2/authenticate?client_id=SOME%20ID&response_type=code&scope=Balance|AccountInfo')

    def testget(self):
        oauth.get('CODE', dwollaparse='dict')
        oauth.r._post_without_token.assert_any_call('/token/', {'code': 'CODE', 'client_secret': 'SOME SECRET', 'grant_type': 'authorization_code', 'client_id': 'SOME ID'}, {'dwollaparse': 'dict'}, custompostfix='/oauth/v2')

    def testrefresh(self):
        oauth.refresh('REFRESH', dwollaparse='dict')
        oauth.r._post_without_token.assert_any_call('/token/', {'client_secret': 'SOME SECRET', 'grant_type': 'refresh_token', 'refresh_token': 'REFRESH', 'client_id': 'SOME ID'}, {'dwollaparse': 'dict'}, custompostfix='/oauth/v2')

    def testcatalog(self):
        oauth.catalog(alternate_token='CATALOG TOKEN', dwollaparse='dict')
        oauth.r._get.assert_any_call('/catalog', {}, {'alternate_token':'CATALOG TOKEN', 'dwollaparse':'dict'})

if __name__ == '__main__':
    unittest.main()