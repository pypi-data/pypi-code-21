#!/usr/bin/env python
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='houkoku',
    version='0.0.0',
    description='Utility package for sending notifications',
    author='Edgar Y. Walker',
    author_email='edgar.walker@gmail.com',
    url='https://github.com/eywalker/houkoku',
    packages=find_packages(exclude=[]),
    install_requires=[],
)
