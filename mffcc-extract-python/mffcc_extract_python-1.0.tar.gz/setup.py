#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(name = 'mffcc_extract_python',
    version = '1.0',
    author = 'jren',
    author_email = 'jren@massey.ac.nz',
    license = 'MIT',
    zip_safe = False,
    description = 'This is a test for setuptools',
    packages = ['mffcc_extract_python'],
    install_requires = [
        'numpy >= 1.8',
    ],
    )

