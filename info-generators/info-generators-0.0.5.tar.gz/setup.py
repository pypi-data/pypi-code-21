#!/usr/bin/env python
from __future__ import print_function
from setuptools import setup, find_packages
import sys

setup(
    name="info-generators",
    version="0.0.5",
    author="jeremaihloo",
    author_email="1006397539@qq.com",
    description="mock chinese info to test",
    long_description=open("README.rst").read(),
    license="MIT",
    url="https://github.com/desion/info_generators",
    packages=['info_generators'],
    install_requires=[
        "beautifulsoup4",
    ],
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Text Processing :: Indexing",
        "Topic :: Utilities",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3.5",
    ],
    data=['info_generators/consts']
)