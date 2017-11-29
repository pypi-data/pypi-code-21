#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  @namespace tune-reporting-python
#
#    Copyright (c) 2017 TUNE, Inc.
#    All rights reserved.
#

from __future__ import with_statement

# To install the tune-reporting-python library, open a Terminal shell, then run this
# file by typing:
#
# python setup.py install
#

import sys
import re
import codecs

from setuptools import setup

REQUIREMENTS = [
    req for req in open('requirements.txt')
    .read().split('\n')
    if req != ''
]

PACKAGES = [
    'tune_reporting',
    'tune_reporting.errors',
    'tune_reporting.exceptions',
    'tune_reporting.readers',
    'tune_reporting.support',
    'tune_reporting.tmc',
    'tune_reporting.tmc.v2.management',
    'tune_reporting.tmc.v2.reporting',
    'tune_reporting.tmc.v3.reporting'
]

TEST_REQUIREMENTS = ['pytest>=2.8.0', 'pytest-cov']

with open('tune_reporting/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

if len(sys.argv) < 2 or sys.argv[1] == 'version':
    print(version)
    sys.exit()

CLASSIFIERS = [
    # How mature is this project? Common values are
    #   3 - Alpha
    #   4 - Beta
    #   5 - Production/Stable
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Natural Language :: English',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Natural Language :: English',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Topic :: Software Development :: Libraries :: Python Modules'
]

with codecs.open('README.rst', 'r', 'utf-8') as f:
    readme = f.read()
with codecs.open('HISTORY.rst', 'r', 'utf-8') as f:
    history = f.read()

setup(
    name='tune-reporting',
    version=version,
    description='TUNE Reporting API client library.',
    long_description=readme + '\n\n' + history,
    author='TUNE Inc., TuneLab',
    author_email='jefft@tune.com',
    url='https://github.com/TuneLab/tune-reporting-python',
    download_url='https://github.com/TuneLab/tune-reporting-python/archive/v{0}.tar.gz'.format(version),
    keywords=["tune", "reporting", "tmc", "api"],
    license='MIT License',
    zip_safe=False,
    install_requires=REQUIREMENTS,
    packages=PACKAGES,
    package_data={'': ['LICENSE']},
    package_dir={'tune_reporting': 'tune_reporting'},
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=TEST_REQUIREMENTS,
    classifiers=CLASSIFIERS
)
