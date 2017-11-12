from __future__ import unicode_literals

import logging
import requests

from drf_otp_permissions.headers import add_otp


logger = logging.getLogger(__name__)


def get(url, headers, key_location):
    headers_with_otp = add_otp({}, key_location, headers)

    response = requests.get(url=url, headers=headers_with_otp)

    logger.info(response.status_code)
    logger.info(response.text)

    return response


def put(url, headers, key_location, data):
    headers_with_otp = add_otp(data, key_location, headers)

    response = requests.put(url=url, headers=headers_with_otp, data=data)

    logger.info(response.status_code)
    logger.info(response.text)

    return response


def post(url, headers, key_location, data):
    headers_with_otp = add_otp(data, key_location, headers)

    response = requests.post(url=url, headers=headers_with_otp, json=data)

    logger.info(response.status_code)
    logger.info(response.text)

    return response
