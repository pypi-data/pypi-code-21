#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

__version = '0.0.6'

setup(
    name='pyzenodo',
    version=__version,
    description='Python wrapper for the Zenodo REST API',
    author='Tom Klaver',
    author_email='t.klaver@esciencecenter.nl',
    license='Apache 2.0',
    url='https://github.com/Tommos0/pyzenodo',
    download_url='https://github.com/Tommos0/pyzenodo/archive/%s.tar.gz' % __version,
    include_package_data=True,
    keywords=['zenodo', 'pyzenodo'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering',
    ],
    packages=find_packages(),
    install_requires=['requests', 'Beautifulsoup4'],
    long_description="""
A Python wrapper for the Zenodo REST API
---------------------------------------------

Provides methods for accessing Zenodo REST API.

This version requires Python 2.7.x / 3.4.x / 3.5.x / 3.6.x / 3.7.x"""
)
