#!/usr/bin/env python
# coding=utf-8

"""Setup script for packaging openpyxl.

To build a package for distribution:
    python setup.py sdist
and upload it to the PyPI with:
    python setup.py upload

Install a link for development work:
    pip install -e .

Thee manifest.in file is used for data files.

"""

import sys
import os
import warnings
if sys.version_info < (2, 6):
    raise Exception("Python >= 2.6 is required.")
elif sys.version_info[:2] == (3, 2):
    warnings.warn("Python 3.2 is not supported")

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
try:
    with open(os.path.join(here, 'README.rst')) as f:
        README = f.read()
except IOError:
    README = ''


setup(name='alas-ce0-openpyxl',
    packages=find_packages(),
    # metadata
    version="0.1",
    description="A Python library to read/write Excel 2010 xlsx/xlsm files for ALAS-Ce0",
    long_description=README,
    author=u"Adonis Cesar Legón Campo",
    author_email="alegon@alasxpress.com",
    url="https://pypi.python.org/pypi/alas-ce0-openpyxl",
    license="MIT",
    requires=[
        'python (>=2.6.0)',
        ],
    install_requires=[
        'jdcal', 'et_xmlfile',
        ],
    package_data={
        'openpyxl': ['.constants.json']
    },
    classifiers=[
                 'Development Status :: 5 - Production/Stable',
                 'Operating System :: MacOS :: MacOS X',
                 'Operating System :: Microsoft :: Windows',
                 'Operating System :: POSIX',
                 'License :: OSI Approved :: MIT License',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2.6',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3.3',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3.6',
                 ],
    )
