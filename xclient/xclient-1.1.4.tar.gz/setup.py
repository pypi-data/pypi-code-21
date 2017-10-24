#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from setuptools import setup

PACKAGE = "xclient"
NAME = "xclient"
DESCRIPTION = "..."
AUTHOR = "Lei wenzheng"
AUTHOR_EMAIL = "leiwz@kaisagroup.com"
URL = "https://github.com/leiwenzheng/xclient.git"
VERSION = __import__(PACKAGE).__version__

setup_kwargs = dict(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="Apache License, Version 2.0",
    url=URL,
    packages=[PACKAGE],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.5",
        'Programming Language :: Python :: 2.7',
    ],
    entry_points={
        'console_scripts': []
    },
    zip_safe=False,
)

py_version = sys.version_info
install_requires = []
if py_version >= (3, 5):
    install_requires.append('aiohttp>=2.2.5')
    install_requires.append('requests>=2.18.4')
else:
    install_requires.append('requests>=2.18.4')

setup_kwargs['install_requires'] = install_requires

try:
    setup(**setup_kwargs)
except SyntaxError as e:
    if py_version < 3.5:
        pass
    else:
        raise e
