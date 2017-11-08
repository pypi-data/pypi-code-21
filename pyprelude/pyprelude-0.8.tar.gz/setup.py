#!/usr/bin/env python
############################################################
#
# pyprelude
# Copyright (C) 2017, Richard Cook
# Released under MIT License
# https://github.com/rcook/pyprelude
#
############################################################

from __future__ import print_function
from setuptools import setup

setup(
    name="pyprelude",
    version="0.8",
    description="General-purpose Python support functions",
    setup_requires=["setuptools-markdown"],
    long_description_markdown_filename="README.md",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
    ],
    url="https://github.com/rcook/pyprelude",
    author="Richard Cook",
    author_email="rcook@rcook.org",
    license="MIT",
    packages=["pyprelude"],
    include_package_data=True,
    test_suite="pyprelude.tests.suite",
    zip_safe=False)
