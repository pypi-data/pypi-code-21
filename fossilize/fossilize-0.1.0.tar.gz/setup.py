#!/usr/bin/env python3
# encoding: utf-8

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import re
with open('fossilize/__init__.py') as file:
    version_pattern = re.compile("__version__ = '(.*)'")
    version = version_pattern.search(file.read()).group(1)
with open('README.rst') as file:
    readme = file.read()

setup(
    name='fossilize',
    version=version,
    author='Kale Kundert',
    author_email='kale@thekunderts.net',
    long_description=readme,
    packages=[
        'fossilize',
    ],
    entry_points={
        'console_scripts': [
            'fossilize=fossilize:main',
        ],
    },
    install_requires=[
    ],
)
