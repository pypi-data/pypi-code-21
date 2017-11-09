#!/usr/bin/python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of Pynspect package (https://pypi.python.org/pypi/pynspect).
# Originally part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2016 CESNET, z.s.p.o (http://www.ces.net/)
# Copyright (C) since 2016 Jan Mach <honza.mach.ml@gmail.com>
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------

# Resources:
#   https://packaging.python.org/en/latest/
#   https://python-packaging.readthedocs.io/en/latest/index.html

import sys
import os

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open

#
# Import local version of pynspect library, so that we can insert correct version
# number into documentation.
#
sys.path.insert(0, os.path.abspath('.'))
import pynspect

# Generate parsetab.py in advance so it can go into package.
from pynspect.gparser import PynspectFilterParser
parser = PynspectFilterParser()
parser.build()

here = os.path.abspath(os.path.dirname(__file__))

#-------------------------------------------------------------------------------

# Get the long description from the README file
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name = 'pynspect',
    version = pynspect.__version__,
    description = 'Python data inspection library',
    long_description = long_description,
    classifiers = [
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only'
    ],
    keywords = 'library',
    url = 'https://github.com/honzamach/pynspect',
    author = 'Jan Mach',
    author_email = 'honza.mach.ml@gmail.com',
    license = 'MIT',
    packages = [
        'pynspect'
    ],
    test_suite = 'nose.collector',
    tests_require = [
        'nose'
    ],
    install_requires=[
        'ipranges',
        'ply'
    ],
    zip_safe = True
)
