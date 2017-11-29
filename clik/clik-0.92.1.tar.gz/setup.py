# -*- coding: utf-8 -*-
"""
Package configuration for clik.

:author: Joe Joyce <joe@decafjoe.com>
:copyright: Copyright (c) Joe Joyce and contributors, 2009-2017.
:license: BSD
"""
import os
import sys

from setuptools import find_packages, setup


name = 'clik'
version = '0.92.1'

requires = ()
if sys.version_info[0] == 2 and sys.version_info[1] == 6:
    requires = ('argparse',)

url = 'https://%s.readthedocs.io' % name
description = 'A tool for writing complex command-line interfaces with ' \
              'minimal boilerplate and bookkeeping.'
long_description = 'Please see the official project page at %s' % url

root_dir = os.path.abspath(os.path.dirname(__file__))
src_dir = os.path.join(root_dir, 'src')
packages = find_packages(src_dir, include=[name])


setup(
    author='Joe Joyce',
    author_email='joe@decafjoe.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    description=description,
    install_requires=requires,
    license='BSD',
    long_description=long_description,
    name=name,
    package_dir={'': 'src'},
    packages=packages,
    url=url,
    version=version,
    zip_safe=False,
)
