#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import io
import re
import os
import sys


def readme():
    with io.open("README.md", "r", encoding="utf-8") as my_file:
        return my_file.read()

# Note:
# - https://pypi.python.org/pypi?%3Aaction=list_classifiers

setup(
    name = 'py-mortgagekit',
    description='Python library for mortgage calculations.',
    long_description=readme(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Education',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Topic :: Office/Business :: Financial :: Accounting',
      ],
    keywords='mortgage amortization finance',
    version='1.0.3b1',
    author='Bartlomiej Mika',
    author_email='bart@mikasoftware.com',
    url='https://github.com/MikaSoftware/py-mortgagekit',
    license='BSD 2-Clause License',
    python_requires='>=3.6',
    packages=['mortgagekit'],
    install_requires=[
        'py-moneyed',
        'python-dateutil',
    ],
    test_suite='nose.collector',
    tests_require=['nose']
)
