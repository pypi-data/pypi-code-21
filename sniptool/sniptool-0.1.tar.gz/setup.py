#!/usr/bin/env python
###################################################
# Copyright (C) 2017, All rights reserved.
##################################################

from setuptools import setup

setup(
    name="sniptool",
    version="0.1",
    description="Code snippet management tool",
    setup_requires=["setuptools-markdown"],
    long_description_markdown_filename="README.md",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
    ],
    url="https://github.com/rcook/sniptool",
    author="Richard Cook",
    author_email="rcook@rcook.org",
    license="MIT",
    packages=["sniptool"],
    install_requires=[
        "inflection",
        "Jinja2",
        "pyperclip",
        "pyprelude",
        "pysimplevcs"
    ],
    entry_points={
        "console_scripts": [
            "sniptool = sniptool.__main__:_main"
        ]
    },
    include_package_data=True,
    test_suite="sniptool.tests.suite",
    zip_safe=False)
