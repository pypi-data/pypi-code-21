"""
tmpld.core.util
~~~~~~~~~~~~~~

Utility methods for tmpld.

:copyright: (c) 2017 by Joe Black.
:license: Apache2.
"""

import os
import sys
import pwd
import grp
import io
import collections
import contextlib
import string
import random

import delegator
import jinja2


def gen_pass(length=32):
    char_set = (string.ascii_letters +
                string.digits +
                '!#%&()+,-.:;<=>?@[]^_{|}~')
    return ''.join(random.sample(char_set*length, length))


def gen_user(length=16):
    with open('/usr/share/dict/words') as fd:
        words = fd.read().split()
    user = ''
    while len(user) < length:
        user += random.choice(words)
    return user[:length+1]


def gen_token(length=64):
    char_set = string.ascii_letters + string.digits
    return ''.join(random.sample(char_set*length, length))




def get_ownership(file):
    return (
        pwd.getpwuid(os.stat(file).st_uid).pw_name,
        grp.getgrgid(os.stat(file).st_gid).gr_name
    )


def get_mode(file):
    return str(oct(os.lstat(file).st_mode)[4:])


def octalize(string):
    return int(str(string), 8)


def parse_user_group(owner):
    if len(owner.split(':')) == 2:
        user, group = owner.split(':')
    else:
        user, group = owner, None
    return user, group


def set_defaults(d, d2):
    d = d or {}
    d2 = d2 or {}
    for key, val in d2.items():
        d.setdefault(key, val)
    return d


def shell(command, test=False, **kwargs):
    proc = delegator.run(command, **kwargs)
    if test:
        return proc.exit_code == 0
    return proc.out.strip()


def xpath(xml, expression):
    if not try_import('lxml.etree'):
        raise ImportError('you need to install lxml to use this feature')
    import lxml.etree
    doc = lxml.etree.parse(io.StringIO(xml))
    return doc.xpath(expression)


def jsonpath(string):
    if not try_import('jsonpath_rw'):
        raise ImportError('you need to install jsonpath_rw to use this feature')
    from jsonpath_rw import parse
    return parse(string)


@jinja2.contextfunction
def ctx_get_file(ctx, path, *args, **kwargs):
    path = build_path(path, ctx['paths'].absdir)
    return get_file(path, **kwargs)


def get_file(path, default=None, strip=True, strip_comments=True):
    contents = file_or_default(path, default)
    if strip_comments:
        contents = strip_comments_from(contents)
    if strip:
        contents = contents.strip()
    return contents


def file_or_default(path, default=None):
    try:
        with open(path, 'rt') as fd:
            contents = fd.read()
    except FileNotFoundError:
        contents = default or ''
    return contents


def strip_comments_from(string):
    return '\n'.join(
        [line for line in string.split('\n') if not line.startswith('#')])


def build_path(path, absdir):
    if path.startswith(('/', '~')):
        path = os.path.expanduser(path)
    else:
        path = os.path.join(absdir, path)
    return os.path.realpath(path)


def try_import(name, alt=None):
    module_segments = name.split('.')
    last_error = None
    remainder = []

    while module_segments:
        module_name = '.'.join(module_segments)
        try:
            __import__(module_name)
        except ImportError:
            last_error = sys.exc_info()[1]
            remainder.append(module_segments.pop())
            continue
        else:
            break
    else:
        return alt
    module = sys.modules[module_name]
    nonexistent = object()
    for segment in reversed(remainder):
        module = getattr(module, segment, nonexistent)
        if module is nonexistent:
            return alt
    return module


@contextlib.contextmanager
def smart_open(filename, *args, **kwargs):
    if filename in ('-', '/dev/stdin'):
        fh = io.StringIO(sys.stdin.read())
    elif filename == '/dev/stdout':
        fh = sys.stdout
    else:
        fh = open(filename, *args, **kwargs)

    try:
        yield fh
    finally:
        if fh is not sys.stdout:
            fh.close()


PathBase = collections.namedtuple(
    'PathBase', ('relpath', 'filename', 'dirname', 'abspath', 'absdir'))


class Path(PathBase):
    def __new__(cls, relpath):
        return super(Path, cls).__new__(
            cls,
            relpath,
            os.path.basename(relpath),
            os.path.dirname(relpath),
            os.path.abspath(relpath),
            os.path.abspath(os.path.dirname(relpath))
        )
