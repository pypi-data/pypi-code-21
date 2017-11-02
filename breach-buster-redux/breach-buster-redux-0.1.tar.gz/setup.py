#!/usr/bin/env python

"""
breach_buster
=================

Replacement for Django's gzip middleware.  Protects against BREACH.

"""

from setuptools import setup

setup(
    name='breach-buster-redux',
    version='0.1',
    author='Adam DePrince',
    author_email='adeprince@nypublicradio.org',
    description='BREACH resistant gzip middleware for Django',
    url="https://github.com/miki725/breach_buster",
    long_description=__doc__,
    py_modules=[
        'breach_buster/__init__',
        'breach_buster/middleware/__init__',
        'breach_buster/middleware/gzip',
        'breach_buster/examples/__init__',
        'breach_buster/examples/demo_server',
    ],
    packages=['breach_buster',],
    zip_safe=True,
    license='GPLv3',
    include_package_data=True,
    classifiers=[],
    install_requires=[
        'django',
        'six',
    ],
    tests_require=[
        'web.py',
    ]
)
