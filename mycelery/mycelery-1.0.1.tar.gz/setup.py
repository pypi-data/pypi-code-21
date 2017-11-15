#!/usr/bin/python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

PACKAGE = "mycelery"
NAME = "mycelery"
DESCRIPTION = "For mycelery! For Tim"
AUTHOR = "Lei wenzheng"
AUTHOR_EMAIL = "leiwz@kaisagroup.com"
URL = "https://github.com/leiwenzheng/mycelery.git"
VERSION = __import__(PACKAGE).__version__

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="Apache License, Version 2.0",
    url=URL,
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    entry_points={
        'console_scripts': []
    },
    zip_safe=False,
    install_requires=['pymongo>=3.4.0']
)

