#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='dbaas_dbmonitor',
    version='0.2.7',
    description='Integration between dbaas and dbmonitor',
    long_description=readme + '\n\n' + history,
    author='Ricardo Dias',
    author_email='ricardo@ricardodias.org',
    url='https://github.com/ricardosdias'
        '/dbaas_dbmonitor',
    packages=[
        'dbaas_dbmonitor',
    ],
    package_dir={'dbaas_dbmonitor':
                 'dbaas_dbmonitor'},
    include_package_data=True,
    install_requires=[
    ],
    license="BSD",
    zip_safe=False,
    keywords='dbaas_dbmonitor',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
    test_suite='tests',
)
