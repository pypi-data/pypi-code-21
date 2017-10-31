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

VERSION = "0.1.0"

setup(
    name='datapiper',
    version=VERSION,
    description='Simple data processing tool.',
    long_description=readme + '\n\n' + history,
    author='Petri Savolainen',
    author_email='petri.savolainen@koodaamo.fi',
    url='https://github.com/koodaamo/datapiper',
    packages = ['datapiper'],
    include_package_data=True,
    install_requires=[
        "setuptools",
    ],
    setup_requires=['pytest-runner'],
    license="GPLv3",
    zip_safe=False,
    keywords='datapiper',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    tests_require = ["colorama", "pytest"],
)
