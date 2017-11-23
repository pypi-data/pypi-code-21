import os.path
import base64
import glob
import pipes
import re
import hashlib


def quote(arg):
    """Return argument quoted for shell usage"""
    return pipes.quote(arg)


def fileglob(pathname):
    """Return list of matched files for glob"""
    return glob.glob(pathname)


def replace(value='', pattern='', replacement='', ignorecase=False):
    """Perform a `re.sub` returning a string"""

    if not isinstance(value, basestring):
        value = str(value)

    if ignorecase:
        flags = re.I
    else:
        flags = 0
    _re = re.compile(pattern, flags=flags)
    return _re.sub(replacement, value)


def md5sum(data):
    if isinstance(data, str):
        data = data.encode()
    return hashlib.md5(data).hexdigest()


def sha1sum(data):
    if isinstance(data, str):
        data = data.encode()
    return hashlib.sha1(data).hexdigest()


def sha256sum(data):
    if isinstance(data, str):
        data = data.encode()
    return hashlib.sha256(data).hexdigest()


def b64encode(data):
    if isinstance(data, str):
        data = data.encode()
    return base64.b64encode(data).decode()


def b64decode(data):
    if isinstance(data, str):
        data = data.encode()
    return base64.b64decode(data).decode()


class FilterModule:
    """Jinja2 filters"""
    @staticmethod
    def filters():
        return dict(
            b64decode=b64decode,
            b64encode=b64encode,
            basename=os.path.basename,
            dirname=os.path.dirname,
            expanduser=os.path.expanduser,
            realpath=os.path.realpath,
            quote=quote,
            fileglob=fileglob,
            md5=md5sum,
            sha1=sha1sum,
            sha256=sha256sum,
            replace=replace
        )
