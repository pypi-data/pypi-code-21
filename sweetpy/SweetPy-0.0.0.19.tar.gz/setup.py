#!/usr/bin/env python
from __future__ import print_function
from setuptools import setup, find_packages
# from setuptools import find_package_data
import sys

setup(
    name="SweetPy",
    version="0.0.0.19",
    author="inflower",
    author_email="inflowers@126.com",
    description="A micro service launcher",
    long_description=open("README.rst").read(),
    license="MIT",
    url="https://pypi.python.org/pypi/SweetPy",
    packages=find_packages(exclude=["*.*"]),
    include_package_data=True,
    py_modules = ['SweetPy'],
    install_requires=[
        "django",
        "djangorestframework",
        "pygments",
        "markdown",
        "django-filter",
        "django-rest-swagger",
        "kazoo"
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
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
)
