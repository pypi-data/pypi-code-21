#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# System modules
import os
from setuptools import setup, find_packages

__version__ = "0.1.16"

def read_file(filename):
    with open(filename) as f:
        return f.read()

# run setup
# take metadata from setup.cfg
setup( 
    name = "numericalmodel",
    description = "abstract classes to set up and run a numerical model",
    author = "Yann Büchau",
    author_email = "yann.buechau@web.de",
    keywords = "modelling",
    license = "GPLv3",
    version = __version__,
    url = 'https://gitlab.com/nobodyinperson/python3-numericalmodel',
    long_description = read_file("README.rst"),
    classifiers = [
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Programming Language :: Python :: 3.5',
            'Operating System :: OS Independent',
            'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    test_suite = 'tests',
    tests_require = [ 'numpy' ],
    extras_require = { 
        "gui": ["matplotlib","cairocffi"],
        },
    install_requires = [ 'numpy', 'scipy' ],
    packages = find_packages(exclude=['tests']),
    package_data = {'numericalmodel.gui': ["*.glade","*.mo","*.png"]},
    include_package_data = True,
    )
