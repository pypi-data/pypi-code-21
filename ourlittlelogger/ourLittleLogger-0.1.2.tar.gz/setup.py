#!/usr/bin/env python3

import distutils.cmd
import distutils.log
import os
import subprocess

from setuptools import find_packages, setup

install_requires = []

CONFIG = {
    'name': 'ourLittleLogger',
    'version': '0.1.2',
    'url': 'https://gitlab.com/benzolium/python-logger',
    'description': 'ourLittleLogger is used for logging unification.',
    'author': 'connectome.ai',
    'test_suite': 'ourLittleLogger',
    'packages': find_packages(),
    'install_requires': install_requires
}

setup(**CONFIG)
