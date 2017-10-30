#!/usr/bin/env python
############################################################
#
# setup
# Copyright (C) 2017, Richard Cook
# Released under MIT License
# https://github.com/rcook/upload-haddocks
#
############################################################

import os
import re

from setuptools import setup

def _read_properties():
    init_path = os.path.abspath(os.path.join("uploadhaddocks", "__init__.py"))
    regex = re.compile("^\\s*__(?P<key>.*)__\\s*=\\s*\"(?P<value>.*)\"\\s*$")
    with open(init_path, "rt") as f:
        props = {}
        for line in f.readlines():
            m = regex.match(line)
            if m is not None:
                props[m.group("key")] = m.group("value")

    return props

_PROPERTIES = _read_properties()
version = _PROPERTIES["version"]
description = _PROPERTIES["description"]

setup(
    name="upload-haddocks",
    version=version,
    description=description,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
    ],
    url="https://github.com/rcook/upload-haddocks",
    author="Richard Cook",
    author_email="rcook@rcook.org",
    license="MIT",
    packages=["uploadhaddocks"],
    install_requires=[
        "pyprelude"
    ],
    entry_points={
        "console_scripts": [
            "upload-haddocks = uploadhaddocks.__main__:_main"
        ]
    },
    include_package_data=True,
    test_suite="uploadhaddocks.tests.suite",
    zip_safe=False)
