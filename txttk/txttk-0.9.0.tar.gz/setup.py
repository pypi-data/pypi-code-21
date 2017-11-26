#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

from setuptools import setup

with open('README.rst') as f:
    readme = f.read()

with open('VERSION') as f:
    version = f.read().strip()

if sys.argv[-1] == 'publish':
    os.system("python setup.py sdist bdist_wheel upload")
    sys.exit()

requirements = [
    # TODO: put package requirements here
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='txttk',
    version=version,
    description="Text Toolkit: manipulate text & regular expression",
    long_description=readme,
    author="Chia-Jung, Yang",
    author_email='jeroyang@gmail.com',
    url='https://github.com/jeroyang/txttk',
    packages=[
        'txttk',
    ],
    package_dir={'txttk':
                 'txttk'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='txttk',
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
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
