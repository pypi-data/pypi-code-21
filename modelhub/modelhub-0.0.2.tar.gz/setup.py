#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
try:
    README = open('README.md').read()
except Exception:
    README = ""
VERSION = "0.0.2"

setup(
    name='modelhub',
    version=VERSION,
    description='Modelhub',
    url="http://git.patsnap.com/research/modelhub",
    long_description=README,
    author='Jay Young(yjmade)',
    author_email='yangjian@patsnap.com',
    packages=find_packages(),
    install_requires=['tensorflow', "click", "boto3", "appdirs", "grpcio", "pyyaml"],
    entry_points={
        'console_scripts': [
            'modelhub=modelhub.commands:main'
        ]
    },
)
