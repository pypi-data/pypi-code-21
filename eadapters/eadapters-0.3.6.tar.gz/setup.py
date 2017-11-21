#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import setuptools

setuptools.setup(
    name = "eadapters",
    version = "0.3.6",
    author = "Hive Solutions Lda.",
    author_email = "development@hive.pt",
    description = "E-Commerce Adapters",
    license = "Apache License, Version 2.0",
    keywords = "e-commerce adapters logic",
    url = "http://eadapters.hive.pt",
    zip_safe = False,
    packages = [
        "eadapters",
        "eadapters.models",
        "eadapters.models.budy"
    ],
    package_dir = {
        "" : os.path.normpath("src")
    },
    install_requires = [
        "commons_py",
        "budy_api"
    ],
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.0",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6"
    ]
)
