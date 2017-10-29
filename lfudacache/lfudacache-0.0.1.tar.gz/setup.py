# -*- coding: utf-8 -*-
"""
lfudacache
==========

License
-------
MIT (see LICENSE file).
"""

import os
import os.path
import sys

from setuptools import setup

sys_path = sys.path[:]
sys.path[:] = (os.path.abspath('lfudacache'), )
__import__('__meta__')
meta = sys.modules['__meta__']
sys.path[:] = sys_path

with open('README.md') as f:
    meta_doc = f.read()

setup(
    name=meta.app,
    version=meta.version,
    url=meta.url,
    download_url=meta.tarball,
    license=meta.license,
    author=meta.author_name,
    author_email=meta.author_mail,
    description=meta.description,
    long_description=meta_doc,
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        ],
    keywords=['cache', 'memoize'],
    packages=['lfudacache'],
    test_suite='lfudacache.tests',
    zip_safe=True,
    platforms='any')
