#!/usr/bin/env python

from setuptools import setup
from setuptools import find_packages

__version__ = '1.1.0'

setup(
    name = 'statstester',
    version = __version__,
    description = 'Supporting Statistical Test.',
    long_description = '''
    StatsTester helps you to perform Statistical Test.
    This package includes t-test & f-test.
    ''',
    author = 'Shin Kurita',
    url = 'https://github.com/montblanc18',
    license = 'MIT',
    install_package_data = True,
    package_dir = {'input':'input',},
    packages = find_packages(exclude = ('tests', 'docs')),
    package_data = {'input':['input'],},
    install_requires = ['setuptools', 'pandas', 'scipy','numpy'],
    test_suite = 'tests'
)
