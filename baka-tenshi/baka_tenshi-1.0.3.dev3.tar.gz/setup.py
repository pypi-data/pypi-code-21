
# -*- coding: utf-8 -*-

from __future__ import print_function

import os
import re
from codecs import open
from setuptools import setup, find_packages
from setuptools.command.test import test as _test

###############################################################################

NAME = 'baka_tenshi'
DESC = 'Baka: Skeleton framework built top of pyramid, baka_tenshi for sqlalchemy'
AUTHOR = 'Nanang Suryadi'
AUTHOR_EMAIL = 'nanang.jobs@gmail.com'
URL = 'https://github.com/baka-framework/baka_tenshi'
DOWNLOAD_URL = 'https://github.com/baka-framework/baka_tenshi/archive/1.0.0.tar.gz'
LICENSE = 'MIT'
KEYWORDS = ['model', 'sqlalchemy', 'framework']
CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Environment :: Web Environment',
    'Framework :: Pyramid',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Libraries',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Operating System :: OS Independent',
]
INSTALL_REQUIRES = [
    'setuptools',
    'trafaret',
    'pyramid',
    'sqlalchemy',
    'zope.sqlalchemy',
    'transaction',
    'pyramid_retry',
    'pyramid_tm',
    'awesome-slugify',
    'bcrypt',
]
EXTRAS_REQUIRE = {}
ENTRY_POINTS = {}

###############################################################################

HERE = os.path.abspath(os.path.dirname(__file__))
VERSION_FILE = os.path.join(HERE, 'baka_tenshi', '__init__.py')
LONGDESC_FILE = os.path.join(HERE, 'README.rst')

with open(LONGDESC_FILE, encoding='utf-8') as fp:
    LONGDESC = fp.read()


def get_version():
    """Extract package __version__"""
    with open(VERSION_FILE, encoding='utf-8') as fp:
        content = fp.read()
    match = re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]', content, re.M)
    if match:
        return match.group(1)
    raise RuntimeError("Could not extract package __version__")


class test(_test):
    def run(self):
        print('please run tox instead')

setup(name=NAME,
      version=get_version(),
      description=DESC,
      long_description=LONGDESC,
      classifiers=CLASSIFIERS,
      keywords=KEYWORDS,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      url=URL,
      download_url=DOWNLOAD_URL,
      license=LICENSE,
      install_requires=INSTALL_REQUIRES,
      extras_require=EXTRAS_REQUIRE,
      entry_points=ENTRY_POINTS,
      cmdclass={'test': test},
      packages=find_packages(include=['baka_tenshi', 'baka_tenshi.*']),
      zip_safe=False)
