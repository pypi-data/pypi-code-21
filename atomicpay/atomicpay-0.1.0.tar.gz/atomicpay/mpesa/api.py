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
