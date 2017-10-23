#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
from setuptools import setup

def read(f):
    return open(os.path.join(os.path.dirname(__file__), f)).read()

setup(
    name = "modulemd",
    version = "1.3.2",
    author = "Petr Šabata",
    author_email = "contyk@redhat.com",
    description = ("A python library for manipulation of the proposed "
        "module metadata format."),
    license = "MIT",
    keywords = "modularization modularity module metadata",
    url = "https://pagure.io/modulemd",
    packages = ["modulemd", "modulemd/buildopts", "modulemd/components", "modulemd/tests"],
    long_description = read("README.rst"),
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
    ],
    test_suite = "modulemd.tests",
    install_requires = [
        "PyYAML",
        "python-dateutil",
        ],
)
