import unittest, requests, json

from dwolla import rest
from mock import MagicMock


class RestTest(unittest.TestCase):
    '''
    We are testing the rest module against requests so that we see whether or not
    it is passing the proper request forward. Like this, we do not have to test
    against requests from other modules, but rather against rest.
    '''
    def setUp(self):
        # We make a new Rest object just in case any other
        # tests run before this one, so that they do not fail
        # because they are mocked.
        rest.r = rest.Rest()

        requests.post = MagicMock()
        requests.put = MagicMock()

        requests.get = MagicMock()
        requests.delete = MagicMock()
        json.loads = MagicMock()


    # In the below methods, dwollaparse is specified as values other than 'dwolla'
    # so as not to invoke an API exception since we evidently provide test data.

    def testpost(self):
        rest.r._post('/some/endpoint', {'key': 'value'}, {'alternate_token': 'AN OAUTH TOKEN', 'dwollaparse':'raw'}, custompostfix=False)
        requests.post.assert_any_call('https://sandbox.dwolla.com/oauth/rest/some/endpoint',
                                      '{"key": "value"}',
                                      headers={'Content-Type': 'application/json',
                                               'User-Agent': 'dwolla-python/2.x',
                                               'Authorization': 'AN OAUTH TOKEN'},
                                      proxies=False, timeout=15)

    def testpost_without_token(self):
        rest.r._post_without_token('/some/endpoint', {'key': 'value'}, {'dwollaparse':'raw'}, custompostfix=False)
        requests.post.assert_any_call('https://sandbox.dwolla.com/oauth/rest/some/endpoint',
                                      '{"key": "value"}',
                                      headers={'Content-Type': 'application/json',
                                               'User-Agent': 'dwolla-python/2.x'},
                                      proxies=False, timeout=15)

    def testput(self):
        rest.r._put('/some/endpoint', {'key': 'value'}, {'alternate_token': 'AN OAUTH TOKEN', 'dwollaparse': 'raw'}, custompostfix=False)
        requests.put.assert_any_call('https://sandbox.dwolla.com/oauth/rest/some/endpoint',
                                      '{"key": "value"}',
                                      headers={'Content-Type': 'application/json',
                                               'User-Agent': 'dwolla-python/2.x',
                                               'Authorization': 'AN OAUTH TOKEN'},
                                      proxies=False, timeout=15)

    def testget(self):
        rest.r._get('/another/endpoint', {'another_key': 'another_value'}, {'alternate_token': 'AN OAUTH TOKEN', 'dwollaparse':'raw'})
        requests.get.assert_any_call('https://sandbox.dwolla.com/oauth/rest/another/endpoint',
                                     headers={'User-Agent': 'dwolla-python/2.x', 'Authorization': 'AN OAUTH TOKEN'},
                                     params={'another_key': 'another_value'},
                                     proxies=False, timeout=15)

    def testget_without_token(self):
        rest.r._get_without_token('/another/endpoint', {'another_key': 'another_value'}, {'dwollaparse':'raw'})
        requests.get.assert_any_call('https://sandbox.dwolla.com/oauth/rest/another/endpoint',
                                     headers={'User-Agent': 'dwolla-python/2.x'},
                                     params={'another_key': 'another_value'},
                                     proxies=False, timeout=15)

    def testdelete(self):
        rest.r._delete('/another/endpoint', {'another_key': 'another_value'}, {'alternate_token': 'AN OAUTH TOKEN', 'dwollaparse':'raw'})
        requests.delete.assert_any_call('https://sandbox.dwolla.com/oauth/rest/another/endpoint',
                                     headers={'User-Agent': 'dwolla-python/2.x', 'Authorization': 'AN OAUTH TOKEN'},
                                     params={'another_key': 'another_value'},
                                     proxies=False, timeout=15)

if __name__ == '__main__':
    unittest.main()