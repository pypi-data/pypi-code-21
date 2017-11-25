import requests

from atomicpay.mpesa import exceptions
from atomicpay.mpesa import routes


class Auth(object):

    def __init__(self, key, secret, live=False):

        self.consumer_key = key
        self.consumer_secret = secret

        self.live = live
        self._auth = None
        self.authed = False

    def auth(self):

        if self.live:
            url = routes.LIVE_BASE_URL + "{}".format(routes.Token)
        else:
            url = routes.SANBOX_BASE_URL + "{}".format(routes.Token)

        response = requests.get(url, auth=(
            self.consumer_key, self.consumer_secret))
                
        if response.ok:
            data = response.json()
            self._auth = data
            self.authed = True
            return
        
        if response.status_code == 400:
            msg = "Failed key:{}. did you try going live?".format(self.consumer_key)
            raise exceptions.MpesaCredentialError(msg)
        
        raise exceptions.MpesaAuthFailed("{}{}".format(response.code, response.text))

    @property
    def access_token(self):
        if not self.authed:
            self.auth()
            return self._auth['access_token']
        return self._auth['access_token']

    @property
    def expires_in(self):
        if not self.authed:
            self.auth()
            return self._auth['expires_in']
        return self._auth['expires_in']
