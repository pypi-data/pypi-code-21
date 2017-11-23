#!/usr/bin/env python
# encoding: utf-8

"""
@author: amigo
@contact: 88315203@qq.com
@phone: 15618318407
@software: PyCharm
@file: setup.py
@time: 2017/11/23 上午9:54
"""

from __future__ import print_function
from setuptools import setup, find_packages
import sys

setup(
    name="wordbag",
    version="0.1.4",
    author="amigo",
    author_email="88315203@qq.com",
    description="word bag",
    long_description=open("README.rst").read(),
    license="MIT",
    url="https://github.com/salembe/word_bag",
    packages=['wordbag'],
    package_data={'': ['*.txt', '*.rst']},
    install_requires=[
        "jieba"
    ],
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Text Processing :: Indexing",
        "Topic :: Utilities",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
    ],
)
