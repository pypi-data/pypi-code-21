#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import codecs
import wikiexpand
from setuptools import find_packages, setup

__author__ = "wmj"
__email__ = "wmj.py@gmx.com"
__version__ = wikiexpand.__version__
__description__ = wikiexpand.__doc__
__license__ = "LGPLv3"

def read(fname):
    try:
        with codecs.open(os.path.join(os.path.dirname(__file__), fname),
                         'r', 'utf-8') as f:
            return f.read()
    except:
        return ''

config = {
    'name': "wikiexpand",
    'version': __version__,
    'author': __author__,
    'author_email': __email__,
    'description': __description__,
    'long_description': read('README.rst'),
    'license': __license__,
    'keywords': "mediawiki templates expansion",
    'url': "https://bitbucket.org/wmj/wikiexpand",
    'packages': find_packages(),
    'install_requires': [
        "pywikibot>=2.0rc3",
        "mwparserfromhell>=0.4.3"
    ],
    #'include_package_data': True,
    'setup_requires': ['nose>=1.0'],
    'test_suite': 'nose.collector',
    'classifiers': [
        "Topic :: Utilities",
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
    ]
}

setup(**config)
