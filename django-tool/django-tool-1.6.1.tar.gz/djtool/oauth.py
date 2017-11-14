from django.conf import settings
import requests
from djtool.common import Common
import json
import shortuuid
import time
import hmac
import base64
import hashlib


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

    def client_token(self, timeout=30000):
        data = {}
        data['client_id'] = self.client_id
        data["salt"] = shortuuid.uuid()
        data["expires"] = time.time() + timeout
        payload = json.dumps(data).encode("utf8")
        sig = self._get_signature(payload)
        return self._encode_token_bytes(payload+sig)

    def _get_signature(self, value):
        return hmac.new(self.client_secret.encode("utf8"), value, hashlib.sha256).hexdigest().encode("utf8")

    def _encode_token_bytes(self, data):
        return base64.urlsafe_b64encode(data)


