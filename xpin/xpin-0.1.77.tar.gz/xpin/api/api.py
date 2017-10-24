# -*- coding: utf-8 -*-

import urlparse
import requests
import hashlib
import json

from .. import constants
from ..log import logger


class API(object):

    secret = None
    base_url = None
    timeout = None

    def __init__(self, secret, base_url, timeout=None):
        self.secret = secret
        self.base_url = base_url
        self.timeout = timeout

    def create_pin(self, username, source):
        url = urlparse.urljoin(self.base_url, constants.URL_PIN_CREATE)

        data = dict(
            username=username,
            source=source,
        )

        try:
            rsp = requests.post(url, data=self._make_signed_params(data), timeout=self.timeout)

            jdata = rsp.json()

            if jdata['ret'] == 0:
                return True
            else:
                logger.error('rsp.ret invalid. username: %s, rsp: %s', username, jdata)
                return False

        except:
            logger.error('exc occur. username: %s', username, exc_info=True)
            return False

    def verify_pin(self, username, source, pin):
        url = urlparse.urljoin(self.base_url, constants.URL_PIN_VERIFY)

        data = dict(
            username=username,
            source=source,
            pin=pin,
        )

        try:
            rsp = requests.post(url, data=self._make_signed_params(data), timeout=self.timeout)

            jdata = rsp.json()

            if jdata['ret'] == 0:
                return True
            else:
                logger.error('rsp.ret invalid. username: %s, rsp: %s', username, jdata)
                return False

        except:
            logger.error('exc occur. username: %s', username, exc_info=True)
            return False

    def _make_signed_params(self, data):
        """
        生成带签名的params
        :param data:
        :return:
        """
        str_data = json.dumps(data)
        sign = hashlib.md5('|'.join([self.secret, str_data])).hexdigest()
        return dict(
            data=str_data,
            sign=sign,
        )
