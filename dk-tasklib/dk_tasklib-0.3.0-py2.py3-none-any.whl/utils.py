# -*- coding: utf-8 -*-
import os
import string
import sys
from contextlib import contextmanager

from dkfileutils.path import Path

join = os.path.join
null = "NUL" if sys.platform == 'win32' else '/dev/null'
win32 = sys.platform == 'win32'


def dest_is_newer_than_source(src, dst):
    """Check if destination is newer than source.

       Usage::

            if not force and dest_is_newer_than_source(source, dest):
                print 'babel:', dest, 'is up-to-date.'
                return dest

    """
    if not os.path.exists(dst):
        return False
    if not os.path.exists(src):
        raise ValueError("Source does not exist: " + src)
    return os.path.getmtime(src) < os.path.getmtime(dst)


class _MissingDottedString(str):
    def __getattr__(self, attr):
        return _MissingDottedString(self[:-1] + '.' + attr + '}')


class _MissingContext(dict):
    def __missing__(self, key):
        return _MissingDottedString('{%s}' % key)


def fmt(s, ctx):
    """Use the mapping `ctx` as a formatter for the {new.style} formatting
       string `s`.
    """
    return string.Formatter().vformat(s, (), _MissingContext(ctx))


def switch_extension(fname, ext="", old_ext=None):
    """Switch file extension on `fname` to `ext`. Returns the resulting
       file name.

       Usage::

           switch_extension('a/b/c/d.less', '.css')
    
    """
    name, _ext = os.path.splitext(fname)
    if old_ext:
        assert old_ext == _ext
    return name + ext


def filename(fname):
    """Return only the file name (removes the path)
    """
    return os.path.split(fname)[1]


@contextmanager
def message(s):
    try:
        print (' %s ' % s).center(80, '-')
        yield
    except:
        print 'error =====>', s, '<====== error'
        raise
    else:
        print (' (ok: %s) ' % s).center(80, '=')


@contextmanager
def env(**kw):
    """Context amanger to temporarily override environment variables.
    """
    currentvals = {k: os.environ.get(k) for k in kw}
    for k, v in kw.items():
        os.environ[k] = str(v)
    yield
    for k in kw:
        if currentvals[k] is None:
            os.unsetenv(k)
        else:
            os.environ[k] = currentvals[k]


@contextmanager
def cd(directory):
    """Context manager to change directory.

       Usage::

           with cd('foo/bar'):
               # current directory is now foo/bar
           # current directory restored.

    """
    cwd = os.getcwd()
    os.chdir(directory)
    yield
    os.chdir(cwd)


def find_pymodule(dotted_name):
    """Find the directory of a python module, without importing it.
    """
    name = dotted_name.split('.', 1)[0]
    for p in sys.path:
        pth = Path(p)
        if not pth:
            continue
        try:
            # print 'trying:', name, 'in', pth, os.listdir(pth)
            if name in pth and (pth/name).isdir():
                return pth/name
            if name + '.py' in pth:
                return pth
        except OSError:
            continue
        except Exception as e:
            print 'error', pth, e
            raise
    raise ValueError("Path not found for: " + dotted_name)
