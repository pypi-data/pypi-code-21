#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    setup.py
    ~~~~~~~~

    Diversified Data Python Utilies Library

    :copyright: (c) 2017 by steph.
    :license: see LICENSE for more details.
"""

import codecs
import os
import re
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    """Taken from pypa pip setup.py:
    intentionally *not* adding an encoding option to open, See:
       https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    """
    return codecs.open(os.path.join(here, *parts), 'r').read()


def find_version(*file_paths):
    """ find version """
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name='dds_pylib',
    version=find_version("dds_pylib", "__init__.py"),
    description='Diversified Data Python Utilies Library',
    long_description=read('README.rst'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
    ],
    keywords='integer julian date',
    author='Stephen Funkhouser',
    author_email='it@ddssoft.com',
    url='https://bitbucket.org/ddsbitbucket/dds_pylib',
    packages=[
        'dds_pylib'
    ],
    platforms='any',
    license='MIT',
    # install_requires=[
    #     'virtualenv>=1.11.6',
    #     'pep8>=1.5.7',
    #     'pyflakes>=0.8.1',
    # ],
    test_suite='nose.collector',
    tests_require=['nose'],
)
