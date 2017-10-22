import binascii
import socket
import html
from urllib.parse import quote_plus
import random
import string
import humanfriendly
from datetime import datetime

from IPy import IP


class Sanitize:
    def __init__(self, obj):
        self.obj = obj

    def dictionize(self):
        d = {}
        for attr in [a for a in dir(self.obj) if not a.startswith('__') and not a.startswith('_') and not a.startswith('metadata')]:
            val = getattr(self.obj, attr)

            if isinstance(val, datetime):
                val = val.strftime("%Y-%m-%dT%H:%M:%S")

            d[attr] = val
        return d

    def sanitize(self, dataobject):
        for attr in [a for a in dir(dataobject) if not a.startswith('__') and not a.startswith('_')]:
            get_attr = getattr(dataobject, attr)
            if isinstance(get_attr, str):
                if get_attr == 'None' or not get_attr:
                    setattr(dataobject, attr, None)
        return dataobject

    def sanitize_userinput(self, dataobject):
        if not isinstance(dataobject, dict):
            for attr in [a for a in dir(dataobject) if not a.startswith('__') and not a.startswith('_')]:
                a = getattr(dataobject, attr)
        else:
            data = {}

            san = lambda k: html.escape(quote_plus(k))

            for k, v in dataobject.items():
                if isinstance(v, list):
                    for i in range(0, len(v)):
                        dataobject[k] = san(v[i])

        return dataobject

    def humanize(self, humansizes=False, humandates=False, dateformat='%d %b %Y %H:%M'):
        for attr in [a for a in dir(self.obj) if not a.startswith('_')]:
            if humandates:
                get_attr = getattr(self.obj, attr)

                if isinstance(get_attr, datetime):
                    setattr(self.obj, '%s_human' % attr, get_attr.strftime(dateformat))

            if humansizes:
                get_attr = getattr(self.obj, attr)
                isnum = False

                if isinstance(get_attr, int):
                    isnum = True

                if isnum:
                    tokens = ['filesize', 'file_size', 'bytes', 'total_size', 'size_files']
                    if attr in tokens:
                        setattr(self.obj, attr + '_human', humanfriendly.format_size(get_attr))

        return self.obj


def file_read(filename, output_list=True):
    f = open(filename, 'r')
    if output_list:
        return [z.replace('\n', '') for z in f.readlines() if z]
    else:
        return f.read()


def bytesTo(bytes, to, bsize=1024):
    r = float(bytes)
    for i in range({'k' : 1, 'm': 2, 'g' : 3, 't' : 4, 'p' : 5, 'e' : 6 }[to]):
        r /= bsize
    return(r)


def is_int(num):
    try:
        a = int(num)
        return True
    except:
        pass


def is_ipv4(inp):
    try:
        return IP(inp)
    except:
        pass


def resolve_hostname(hostname):
    try:
        return socket.gethostbyname(hostname)
    except:
        pass


def is_json(blob):
    import json
    try:
        blob = json.loads(blob)
    except:
        raise Exception("Tried loading a json blob but failed. Blob: %s" % (blob))
    return blob


""" Module that monkey-patches json module when it's imported so
JSONEncoder.default() automatically checks for a special "get_json()"
method and uses it to encode the object if found.

"""
from json import JSONEncoder


def _default(self, obj):
    return getattr(obj.__class__, "get_json", _default.default)(obj)

_default.default = JSONEncoder().default
JSONEncoder.default = _default


def decorator_parametrized(dec):
    def layer(*args, **kwargs):
        def repl(f):
            return dec(f, *args, **kwargs)
        return repl
    return layer


def random_str(length: int):
    """Generates random output from /dev/urandom"""
    return binascii.hexlify(open("/dev/urandom", "rb").read(length)).decode("UTF-8")
