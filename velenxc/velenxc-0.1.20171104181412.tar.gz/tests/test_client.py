import unittest

from velenxc.utils.client import RESTClient, HttpClient


class RESTClientTestCase(unittest.TestCase):

    def test_get_should_return_byte_data(self):
        self.assertIsInstance(RESTClient.get('http://api.digcredit.com/source/queryinfo/', {}).content, bytes)

    def test_post_should_return_byte_data(self):
        self.assertIsInstance(RESTClient.post('http://api.digcredit.com/source/queryinfo/', {}).content, bytes)


class DataOceanClientTestCase(unittest.TestCase):

    def setUp(self):
        url = 'http://apitest.digcredit.com'
        client_id = 'jpWstKTB3bqPLWNoocVncCVVHniytPn6ROHy82Ze'
        client_secret = 'kXXNuP6IOMYr5WxhZihef4Ub6QbOFRPglX0WPPZ5D2sAydh3vDZTCvuMGRFAwlJcu3LoqlQuzs60XE72mxlisrZfhW2' \
                        'DGGCjUHJojkPhiouYrjKrkBj357ThuC61qupk'
        crypt_key = 'sjdguhcphysghcih'
        self.do_client = HttpClient(url, client_id, client_secret, crypt_key)

    def test_request_data_ocean_should_return_dict_content(self):
        self.assertIsInstance(self.do_client.request_data_ocean(data=dict(mobile='13581731204',
                                                                          data_identity='mobile_locale')), dict)

    def test_request_data_ocean_should_return_none(self):
        self.assertIsNone(self.do_client.request_data_ocean(data=dict(mobile='13581731204',
                                                                      data_identity='mobile_locale'), uri=''))

    def test_get_access_token_should_return_access_token(self):
        self.assertRegex(self.do_client.get_access_token(), '[A-za-z0-9]{30}')

    def test_get_access_token_should_return_none(self):
        self.assertIsNone(self.do_client.get_access_token(uri=''))

    def test_get_response_data_should_decrypt(self):
        self.assertIn('res_data', self.do_client.get_response_data('{"res_data": "QhXJ9KgcbDg9HclRNM8qScMcrOZtlUEjkcte'
                                                                   'cIeOt7fB28sT/2+jiOiTiinT14RU0x6GrcIlfm7Xs09yk6woNq'
                                                                   'HYPJ1Kd1WMKEDCBoNjM4ZTZ4lifOoleUBgzjtM2DmfIXB8PKQQ'
                                                                   '0xFbNvww7TcwRODVWqxqT78P3Vz+AQXtObc=", "message": '
                                                                   '"操作成功", "status": 1}'))

    def test_call_api_should_return_bytes(self):
        self.assertIsInstance(self.do_client.call_api('http://apitest.digcredit.com/oauth2/token/',
                                                      '2jyl7NpoGelBLKxzY/WZ3JqFpWlxadcxnODYkv2VrS8YHLhzU/J8aD9oOgD/g'
                                                      'hYd+WQkZmbjWVsY4kL5w8oidZ7Evm7tWuN+Fp521+UYNMZW9jZ5bA0K1LXfGI'
                                                      'zXMKVyv4/vpVS8nDJeN6EwvAJZRhGu/px+Qi65eXfpPfSlojzyc+w3aavfd+bb'
                                                      'MvFtKeZNcXb4fTpvWd/oekddaCMINaRBG1GKa0CMTgQh7G5LbT2KJoU+lsuo8E'
                                                      'XrE/s8T/TH').content, bytes)


