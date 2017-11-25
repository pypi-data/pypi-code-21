#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import sys
from os.path import dirname, join
from pip.req import parse_requirements

from setuptools import (
    find_packages,
    setup,
)


with open(join(dirname(__file__), 'rqalpha_data/VERSION.txt'), 'rb') as f:
    version = f.read().decode('ascii').strip()

requirements = [str(ir.req) for ir in parse_requirements("requirements.txt", session=False)]

setup(
    name='rqalpha-data',
    version=version,
    description='A utility for RQAlpha to directly use data',
    packages=find_packages(exclude=[]),
    author='sixquant',
    author_email='public@sixquant.com',
    license='Apache License v2',
    package_data={'': ['*.*']},
    url='https://github.com/sixquant/rqalpha-data',
    install_requires=requirements,
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
