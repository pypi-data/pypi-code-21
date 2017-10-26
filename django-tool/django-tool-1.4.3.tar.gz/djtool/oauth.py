from django.conf import settings
import requests
from djtool.common import Common


class ClientOauth(Common):

    def __init__(self, client_id='', client_secret=''):
        self.client_id = client_id or settings.CLIENT_ID
        self.client_secret = client_secret or settings.CLIENT_SECRET
        self.requests = requests.Session()

    def _login(self, user, data):
        data["client_id"] = self.client_id
        data["grant_type"] = 'password'
        response = self.requests.post('%s/api/%s/token/' % (settings.ACCOUNT_API_HOST, user), data=data, headers={'X-CSRFToken': self.requests.cookies.get('csrftoken')})
        if response.status_code == 200:
            return response.json()
        return None

    def usertoken(self, data):
        return self._login('user', data)

    def admintoken(self, data):
        return self._login('admin', data)

    def info(self, token):
        r = self.requests.get('%s/api/userinfo/' % settings.ACCOUNT_API_HOST, headers={"TOKEN": token})
        return r.json()

