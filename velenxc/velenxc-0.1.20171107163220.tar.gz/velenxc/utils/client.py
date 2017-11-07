
import json
import requests

from velenxc.utils.crypto import Crypt


class RESTClient(object):
    """RESTful client"""
    headers = {
        "Content-type": "application/json; charset=utf-8",
    }

    @staticmethod
    def get(url, data, headers=headers, **kwargs):

        return requests.get(url, data, headers=headers, **kwargs)

    @staticmethod
    def post(url, data, headers=headers, **kwargs):

        return requests.post(url, json=data, headers=headers, **kwargs)


class HttpClient(RESTClient):

    def __init__(self, url, client_id, client_secret, crypt_key):
        """
        Data ocean client tools class
        :param url: data ocean service address
        :param client_id: data ocean user's client_id
        :param client_secret: data ocean user's client_secret
        :param crypt_key: data ocean user's crypt_key
        """
        self.url = url if not url.endswith('/') else url[:-1]
        self.client_id = client_id
        self.client_secret = client_secret
        self.crypt_key = crypt_key
        self.req_data = {'req_data': ''}

        if self.client_id:
            self.req_data.update({
                'client': self.client_id
            })

    def call_api(self, url, req_data, method='post', **kwargs):
        req_data = Crypt.aes_base64_encrypt(json.dumps(req_data), self.crypt_key).decode()
        do_method = getattr(self, method, self.post)
        self.req_data.update({'req_data': req_data})

        return do_method(url, data=self.req_data, **kwargs)

    def get_response_data(self, content):
        """
        :param content: response.content
        :return: after decrypt and dict data
        """
        content = json.loads(content)
        if content.get('res_data', None):
            content['res_data'] = json.loads(Crypt.aes_base64_decrypt(content['res_data'], self.crypt_key))

        return content

    def get_access_token(self, uri='/oauth2/token/', grant_type='client_credentials'):
        res = self.call_api(self.url+uri, dict(grant_type=grant_type,
                                               client_secret=self.client_secret))
        if res.status_code == 200:  # success
            content = self.get_response_data(res.content.decode())
            access_token = content.get('res_data').get('access_token')
        else:
            access_token = None

        return access_token

    def request_data_ocean(self, uri='/source/queryinfo/', data={}, required_token=True, **kwargs):
        """Entrance for request data ocean API, return response data which has been decrypt"""
        if required_token:
            access_token = self.get_access_token()
            data['access_token'] = access_token

        res = self.call_api(self.url+uri, data, **kwargs)
        if res.status_code == 200:  # success
            content = self.get_response_data(res.content.decode())
        else:
            content = None

        return content
