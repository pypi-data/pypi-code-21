#!/usr/bin/env python
"""Setuptools script.
"""
import os
import codecs
from setuptools import setup, find_packages

PACKAGENAME = 'sqre-pytravisci'
DESCRIPTION = 'TravisCI Python interaction class'
AUTHOR = 'Adam Thornton'
AUTHOR_EMAIL = 'athornton@lsst.org'
URL = 'https://github.com/sqre-lsst/travisci'
VERSION = '0.0.4'
LICENSE = 'MIT'


def local_read(filename):
    """Convenience function for includes"""
    full_filename = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        filename)
    return codecs.open(full_filename, 'r', 'utf-8').read()


LONG_DESC = local_read('README.md')

setup(
    name=PACKAGENAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESC,
    url=URL,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license=LICENSE,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'License :: OSI Approved :: MIT License',
    ],
    keywords='lsst',
    packages=find_packages(exclude=['docs', 'tests*']),
    install_requires=[
        'sqre-apikit>=0.1.0',
        'pycrypto==2.6.1',
        'requests>=2.13.0,<3.0.0'
    ],
    tests_require=['pytest', 'pytest-flake8', 'pytest-cov'],
)
