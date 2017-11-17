#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import with_statement
from os.path import dirname, join

import sys
if sys.version_info < (3, 0):
    sys.exit('Python 3.0 or greater is required.')

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name="Scrapy_mingle",
    version='0.1.28',
    description="Some useful tools for Scrapy",
    long_description=open('README.rst').read(),
    author="xuhaomin",
    author_email="xhmgreat@sina.com",
    license="BSD",
    url="https://github.com/xuhaomin/scrapy_mingle",
    include_package_data=True,
    packages=['scrapy_mingle'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Scrapy",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=[
        'Scrapy',
        'redis',
        'requests',
        'twisted',
        'scrapy_rediscluster',
        'scrapy_redis',
    ],
    zip_safe=False,
)
