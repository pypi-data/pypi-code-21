# -*- coding: utf-8 -*-

import urlparse
import urllib
import requests
import hashlib
import json

from . import constants
from .log import logger


class API(object):

    source = None
    secret = None
    schema = None
    host = None
    timeout = None

    def __init__(self, source, secret, schema, host, timeout=None):
        self.source = source
        self.secret = secret
        self.schema = schema
        self.host = host
        self.timeout = timeout

    def gen_login_url(self, callback, schema=None):
        """
        创建登录url
        :param callback:
        :param schema:
        :return:
        """
        schema = schema or self.schema
        path = constants.URL_USER_LOGIN

        sign = hashlib.md5('|'.join([self.secret, path, self.source, callback])).hexdigest()

        query = urllib.urlencode(dict(
            source=self.source,
            callback=callback,
            sign=sign,
        ))

        return urlparse.urlunsplit((schema, self.host, path, query, ''))

    def auth_token(self, token):
        path = constants.URL_USER_TOKEN_AUTH
        url = urlparse.urlunsplit((self.schema, self.host, path, '', ''))

        data = dict(
            source=self.source,
            token=token,
        )

        try:
            rsp = requests.post(url, data=self._make_signed_params(path, data), timeout=self.timeout)

            jdata = rsp.json()

            if jdata['ret'] == 0:
                return jdata['user']
            else:
                logger.error('rsp.ret invalid. data: %s, rsp: %s', data, jdata)
                return None

        except:
            logger.error('exc occur. data: %s', data, exc_info=True)
            return None

    def verify_permission(self, token, method, content, extra=None):
        path = constants.URL_USER_PERMISSION_VERIFY
        url = urlparse.urlunsplit((self.schema, self.host, path, '', ''))

        data = dict(
            source=self.source,
            token=token,
            method=method,
            content=content,
            extra=extra,
        )

        try:
            rsp = requests.post(url, data=self._make_signed_params(path, data), timeout=self.timeout)

            jdata = rsp.json()

            if jdata['ret'] == 0:
                return True
            else:
                logger.error('rsp.ret invalid. data: %s, rsp: %s', data, jdata)
                return False

        except:
            logger.error('exc occur. data: %s', data, exc_info=True)
            return False

    def get_all_permissions(self, token):
        path = constants.URL_USER_PERMISSIONS_ALL
        url = urlparse.urlunsplit((self.schema, self.host, path, '', ''))

        data = dict(
            source=self.source,
            token=token,
        )

        try:
            rsp = requests.post(url, data=self._make_signed_params(path, data), timeout=self.timeout)

            jdata = rsp.json()

            if jdata['ret'] == 0:
                return jdata['permissions']
            else:
                logger.error('rsp.ret invalid. data: %s, rsp: %s', data, jdata)
                return None

        except:
            logger.error('exc occur. data: %s', data, exc_info=True)
            return None

    def create_pin(self, username):
        path = constants.URL_PIN_CREATE
        url = urlparse.urlunsplit((self.schema, self.host, path, '', ''))

        data = dict(
            username=username,
            source=self.source,
        )

        try:
            rsp = requests.post(url, data=self._make_signed_params(path, data), timeout=self.timeout)

            jdata = rsp.json()

            if jdata['ret'] == 0:
                return True
            else:
                logger.error('rsp.ret invalid. username: %s, rsp: %s', username, jdata)
                return False

        except:
            logger.error('exc occur. username: %s', username, exc_info=True)
            return False

    def verify_pin(self, username, pin):
        path = constants.URL_PIN_VERIFY
        url = urlparse.urlunsplit((self.schema, self.host, path, '', ''))

        data = dict(
            username=username,
            source=self.source,
            pin=pin,
        )

        try:
            rsp = requests.post(url, data=self._make_signed_params(path, data), timeout=self.timeout)

            jdata = rsp.json()

            if jdata['ret'] == 0:
                return True
            else:
                logger.error('rsp.ret invalid. username: %s, rsp: %s', username, jdata)
                return False

        except:
            logger.error('exc occur. username: %s', username, exc_info=True)
            return False

    def _make_signed_params(self, path, data):
        """
        生成带签名的params
        :param data:
        :return:
        """
        str_data = json.dumps(data)
        sign = hashlib.md5('|'.join([self.secret, path, str_data])).hexdigest()
        return dict(
            data=str_data,
            sign=sign,
        )
