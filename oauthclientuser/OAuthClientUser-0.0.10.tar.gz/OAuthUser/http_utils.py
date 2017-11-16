# -*- coding: utf-8 -*-
import re
import sys
import logging
from base64 import b64encode


if sys.version_info > (3, 0):
    from urllib.parse import urlencode
    from http.client import HTTPSConnection, HTTPConnection, HTTPException
else:
    from urllib import urlencode
    from httplib import HTTPSConnection, HTTPConnection, HTTPException


logger = logging.getLogger(__name__)


def split_url(url):
    pat = r'(?P<scheme>https?)://(?P<host>[^/:]+)(?::(?P<port>[1-9][0-9]*))?(?P<path>/[^?]*)(?:\?(?P<params>.*))?'
    mat = re.match(pat, url)
    if mat is not None:
        return mat.groupdict()
    return None


def get_request(url, headers):
    url_detail = split_url(url)
    if url_detail is None:
        raise Exception('Wrong URL: {}'.format(url))

    print(url_detail)
    if url_detail.get('scheme') == 'http':
        con = HTTPConnection(url_detail.get('host'), int(url_detail.get('port', '80')))
    else:
        con = HTTPSConnection(url_detail.get('host'), int(url_detail.get('port', '443')))

    try:
        con.request('GET', url_detail.get('path'), headers=headers)
        rsp = con.getresponse()
    except HTTPException as e:
        logger.error('HTTP Exception: {}'.format(e))
        return None, None
    else:
        logger.debug('GET from {} SUCCESS!'.format(url))

    return rsp.status, rsp.read()


def post_request(url, content, username, password):
    url_detail = split_url(url)
    if url_detail is None:
        raise Exception('Wrong URL: {}'.format(url))

    print(url_detail)
    if url_detail.get('scheme') == 'http':
        con = HTTPConnection(url_detail.get('host'), int(url_detail.get('port', '80')))
    else:
        con = HTTPSConnection(url_detail.get('host'), int(url_detail.get('port', '443')))

    if isinstance(content, dict):
        body = urlencode(content)
    else:
        body = content

    print('body: {}'.format(body))
    headers = {
        "Authorization": "Basic {}".format(b64encode('{}:{}'.format(username, password).encode()).decode('ascii')),
        "Content-Type": "application/x-www-form-urlencoded",
        "Content-Length": len(body)
    }

    print(headers)

    try:
        con.request('POST', url_detail.get('path'), body, headers=headers)
        rsp = con.getresponse()
    except HTTPException as e:
        logger.error('HTTP Exception: {}'.format(e))
        return None, None
    else:
        logger.debug('POST to {} SUCCESS!\n{}'.format(url, body))

    return rsp.status, rsp.read()


def get_account_info(url, token_type, access_token):
    headers = {
        'Authorization': '{} {}'.format(token_type, access_token),
        'Accept': 'application/json'
    }

    return get_request(url, headers)
