#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

from __future__ import print_function
from setuptools import setup, find_packages
import sys
from setupbase import (
    create_cmdclass, __version__
)


setup_args = dict(
    name            = 'quantlab_launcher',
    version         = __version__,
    packages        = find_packages('.'),
    package_data    = { 'quantlab_launcher': ['*.html'] },
    description     = "Jupyter Launcher",
    long_description= """
    This package is used to launch an application built using QuantLab
    """,
    author          = 'QuantLab Development Team',
    author_email    = 'quantlab.io@gmail.com',
    url             = 'https://www.quantlab.io',
    license         = 'BSD',
    platforms       = "Linux, Mac OS X, Windows",
    keywords        = ['Jupyter', 'QuantLab'],
    cmdclass        = create_cmdclass(),
    classifiers     = [
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)

if 'setuptools' in sys.modules:
    setup_args['extras_require'] = {
        'test:python_version == "2.7"': ['mock'],
        'test': ['pytest', 'requests']
    }
    setup_args['install_requires'] = [
        'notebook>=4.2.0',
    ]

if __name__ == '__main__':
    setup(**setup_args)
