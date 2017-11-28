"""
kzconfig.util
~~~~~

Kazoo config library.

"""

import base64
import json
from os.path import join

import dns.resolver


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


def json_dumps(obj, safe=True):
    seperators = (',', ':') if safe else None
    return json.dumps(obj, separators=seperators)


def addrs_for(*domains):
    addrs = []
    for domain in domains:
        ans = [a.address for a in dns.resolver.query(domain, 'A')]
        addrs.extend(ans)
    return list(set(addrs))


def to_str(items, path='/', flag='data', delim=' '):
    return delim.join('--{} {}/{}'.format(flag, path, item) for item in items)


def read_config(path, base='.'):
    with open(join(base, path)) as fd:
        return fd.read().strip()
