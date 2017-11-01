"""
kzconfig.util
~~~~~

Kazoo config library.


"""

import base64
import json


def quote(content):
    return '"' + content + '"'


def b64encode(data):
    if isinstance(data, str):
        data = data.encode()
    return base64.b64encode(data).decode()


def b64decode(data):
    if isinstance(data, str):
        data = data.encode()
    return base64.b64encode(data).decode()


def join_url(scheme, user, password, host):
    return '{}://{}:{}@{}'.format(scheme, user, password, host)


def json_dumps(obj):
    return json.dumps(obj, separators=(',', ':'))
