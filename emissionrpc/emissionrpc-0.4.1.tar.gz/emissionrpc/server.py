
import json
import requests
from requests.exceptions import RequestException, HTTPError

from .exceptions import EmissionLibError, EmissionBadParameter

DEFAULT_ADDR = 'localhost'
DEFAULT_PORT = '9091'
DEFAULT_TIMEOUT = '30'
ENDPOINT = '/transmission/rpc'


class Server(object):

    ENDPOINT = '/transmission/rpc'

    def __init__(self, address, port, timeout=None):
        self._session = requests.Session()
        self._url = 'http://{0}:{1}{2}'.format(address, port, self.ENDPOINT)
        self._token = 'empty'
        self.handle_csrf()

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, val):
        try:
            address, port = val
        except ValueError:
            raise EmissionBadParameter("pass an iterable with address and port")
        else:
            """ This will run only if no exception was raised """
            self._url = 'http://{0}:{1}{2}'.format(address, port, self.ENDPOINT)

    def handle_csrf(self):
        try:
            r = self._session.get(self._url)
            r.raise_for_status()
        except HTTPError as e:
            if e.response.status_code == 409:
                self._token = e.response.headers['X-Transmission-Session-Id']
            else:
                raise EmissionLibError("something went wrong with request", e)
        except RequestException as e:
            raise EmissionLibError("something went wrong with request", e)

    def download(self, url):
        try:
            r = self._session.get(url)
            r.raise_for_status()
            return r
        except (RequestException, HTTPError) as e:
            raise EmissionLibError("something went wrong with request", e)

    def execute(self, payload):
        if not self._token:
            raise EmissionBadParameter('token should not be empty')

        token = {'X-Transmission-Session-Id': self._token}

        try:
            r = self._session.post(self._url,
                                   headers=token,
                                   data=json.dumps(payload))
            r.raise_for_status()
            return r
        except (RequestException, HTTPError) as e:
            raise EmissionLibError("something went wrong with request", e)
