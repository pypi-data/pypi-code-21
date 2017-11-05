import os
import shutil
import tempfile
import urllib
from contextlib import contextmanager
from functools import wraps
from os.path import basename, exists, join

import requests


@contextmanager
def tmp(tmpdir="./tmp"):
    if not exists(tmpdir):
        os.makedirs(tmpdir)

    path = tempfile.mkdtemp(dir="./tmp")
    yield path

    if exists(path):
        shutil.rmtree(path)


def cache(outpath):
    def x(func):
        @wraps(func)
        def inner(*args, **kwargs):
            path = outpath.format(*args, **kwargs)
            mode = 'folder' if path.endswith('/') else 'file'

            if mode == "folder":
                opath = './tmp/%s/' % path.split('/')[-2]
            else:
                opath = './tmp/%s' % basename(path)

            if exists(opath):
                return opath

            with tmp() as tmpfolder:
                tmppath = join(tmpfolder, basename(opath))
                if mode == "folder" and not exists(tmppath):
                    os.makedirs(tmppath)

                final_path = func(*args, opath=tmppath, **kwargs)

                if final_path == tmppath:
                    shutil.move(final_path, opath)
                    return opath

                return final_path

        return inner

    return x


@cache("{0}")
def _local(name, url, opath):
    urllib.urlretrieve(url, opath)
    return opath


def local(url):
    filename = os.path.basename(url).split('?')[0]
    return _local(filename, url)


def remote(filepath):
    assert os.path.exists(filepath), "file not exists"

    files = {
        'file': (os.path.basename(filepath), open(filepath, 'rb')),
    }

    resp = requests.post('https://file.io/', files=files).json()
    assert resp['success'], resp

    return resp['link']
