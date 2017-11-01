#!/usr/bin/python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of typedcols package (https://pypi.python.org/pypi/typedcols).
#
# Copyright (c) since 2016, CESNET, z. s. p. o.
# Author: Pavel Kácha <pavel.kacha@cesnet.cz>
# Use of this source is governed by an ISC license, see LICENSE file.
#-------------------------------------------------------------------------------

# Resources:
#   https://packaging.python.org/en/latest/
#   http://python-packaging-user-guide.readthedocs.io/distributing/

import sys
import os

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open

#
# Import local version of typedcols library, so that we can insert correct version
# number into documentation.
#
sys.path.insert(0, os.path.abspath('.'))
import typedcols

#-------------------------------------------------------------------------------

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name = 'typedcols',
    version = typedcols.__version__,
    description = 'Python library providing typed collections.',
    long_description = long_description,
    classifiers = [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python',
    ],
    keywords = 'library',
    url = 'https://homeproj.cesnet.cz/git/typedcols.git',
    author = 'Pavel Kacha',
    author_email = 'pavel.kacha@cesnet.cz',
    license = 'ISC',
    py_modules = ['typedcols'],
    test_suite = 'nose.collector',
    tests_require = [
        'nose'
    ],
    zip_safe = True
)
