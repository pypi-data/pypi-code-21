import requests


class Chameleon:

    def __init__(self, server_uri='http://localhost:5000'):
        self.base_uri = server_uri

    def set_response(self, status_code, body, headers=None):
        """
        Set the response that the chameleon server will return.

        :param status_code: HTTP status code of the response
        :param body: response body
        :param headers: response HTTP headers
        """
        headers = headers or []
        payload = {
            'status_code': status_code,
            'body': body,
            'headers': headers,
        }
        requests.put(self.base_uri, json=payload, headers={'X-Chameleon': 'true'})

    def get_requests(self):
        """
        Retrieve the request that the Chameleon has received.

        :return: List of requests, e.g.:
        [
         {'args': [],
          'body': '',
          'cookies': {},
          'headers': [['Content-Length', ''],
           ['Connection', 'keep-alive'],
           ['Host', 'localhost:5000'],
           ['Accept', '*/*'],
          'method': 'GET',
          'path': '/abc',
          'url': 'http://localhost:5000/abc'
          }
        ]
        """
        r = requests.get(self.base_uri, headers={'X-Chameleon': 'true'})
        return r.json()

    def clear_requests(self):
        """
        Clears the list of requests received by the Chameleon server.

        (Next call to get_requests would return [] if nothing calls the server in between)
        """
        requests.delete(self.base_uri, headers={'X-Chameleon': 'true'})
