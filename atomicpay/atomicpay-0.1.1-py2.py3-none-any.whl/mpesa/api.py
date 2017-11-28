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

import threading

import requests

from atomicpay.mpesa.models import MpesaResponse
from atomicpay.mpesa.routes import (LIVE_BASE_URL, SANBOX_BASE_URL)


def _call_api(url, data, headers, callback=None):
    response = requests.post(url, json=data, headers=headers)

    if callback:
        callback(MpesaResponse(response))

    return MpesaResponse(response)


def call(route, data, access_token, live=False, callback=None):
    """
    Makes an http request to the given route with the given data

    params:
    route: Url Route [str]
    data: data to be sent to the by the request [dict]
    access_token: Access Token [str]
    live: if the request is for production [bool]

    return:
        MpesaResponse object
    """
    _url = LIVE_BASE_URL if live else SANBOX_BASE_URL
    url = '{}{}'.format(_url, route)

    headers = {
        "Authorization": "Bearer {}".format(access_token),
        "Content-Type": "application/json"
    }

    if callback and callable(callback):
        thread = threading.Thread(
            target=_call_api,
            args=(url, data, headers, callback),
            kwargs=None
        )

        thread.start()
        return thread

    return _call_api(url, data, headers)
