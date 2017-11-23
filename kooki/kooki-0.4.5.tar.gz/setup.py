#!/usr/bin/env python
import os, sys
from setuptools import setup, find_packages

__version__ = '0.4.5'

setup(
    name='kooki',
    version=__version__,
    description='The ultimate document generator.',
    author='Noel Martignoni',
    include_package_data=True,
    author_email='noel@martignoni.fr',
    url='https://gitlab.com/kooki/kooki',
    scripts=['scripts/kooki'],
    install_requires=['markdown', 'empy', 'pyyaml', 'toml', 'requests', 'termcolor', 'vcstool', 'libsass'],
    packages=find_packages(exclude=['tests*', 'jars']),
    test_suite='tests',
)
