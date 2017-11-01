# -*- coding: utf-8 -*-

import os

from setuptools import setup, find_packages


def __path(filename):
    return os.path.join(os.path.dirname(__file__), filename)

with open(__path('requirements.txt')) as f:
    REQUIRES = [l.strip() for l in f.readlines()]

VERSION = '0.2.0'

setup(
    name='ruin',
    packages=find_packages(),
    install_requires=REQUIRES,
    version=VERSION,
    description='RUIN - Python/Mongo query builder and model validator',
    author='g----',
    author_email='gloob@krutt.org',
    url='https://gitlab.com/g----/ruin',
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)
