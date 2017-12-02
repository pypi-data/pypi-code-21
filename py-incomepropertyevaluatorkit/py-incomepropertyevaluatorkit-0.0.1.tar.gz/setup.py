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
    name = 'py-incomepropertyevaluatorkit',
    description='Python library for performing rental and income property calculations.',
    long_description=readme(),
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Education',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Topic :: Office/Business :: Financial :: Accounting',
      ],
    keywords='mortgage real estate financial business bank',
    version='0.0.1',
    author='Bartlomiej Mika',
    author_email='bart@mikasoftware.com',
    url='https://github.com/MikaSoftware/incomepropertyevaluatorkit-py',
    license='BSD 2-Clause License',
    python_requires='>=3.6',
    packages=['incomepropertyevaluatorkit'],
    install_requires=[
        'py-moneyed',
        'py-mortgagekit',
        'numpy',
        'pisa',
        'xhtml2pdf>=0.2b1'
    ],
    test_suite='nose.collector',
    tests_require=['nose'],
)
