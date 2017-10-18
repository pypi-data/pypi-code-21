#!/usr/bin/env python

from setuptools import setup, find_packages

import velenxc

VERSION = velenxc.__version__
DIST_NAME = 'velenxc'

setup(
    name=DIST_NAME,
    version=VERSION,
    author='digcreditdev',
    author_email='niushaohan@digcredit.com',
    description='Machine Learning utility lib',
    long_description=open('README.rst').read(),
    license='MIT',
    url='https://pypi.python.org/pypi/velenxc',
    packages=find_packages(),
    install_requires=[
        'pandas'
    ],
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ]
)
