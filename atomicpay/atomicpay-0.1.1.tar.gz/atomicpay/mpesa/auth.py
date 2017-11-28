# Copyright (c) 2017 Turbopay Holdings Ltd

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE

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
        """Used generate an OAuth access token to access other APIs"""

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
            msg = "Failed key:{}. did you try going live?".format(
                self.consumer_key)
            raise exceptions.MpesaCredentialError(msg)

        raise exceptions.MpesaAuthFailed(
            "{}{}".format(response.code, response.text))

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
