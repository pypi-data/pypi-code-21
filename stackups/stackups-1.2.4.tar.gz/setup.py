#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  6 19:44:34 2015

@author: kcarlton
"""

# reference: https://docs.python.org/3/distutils/examples.html
# url = "http://packages.python.org/an_example_pypi_project",

import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

version = __import__('stackups').get_version()

setup(
    name = "stackups",
    version = version,
    description='Stack up analyis: calculate clearances between machinery parts.',
    author = "Kenneth E. Carlton",
    author_email = "kencarlton777@gmail.com",
    url = 'http://www.newconceptzdesign.com/',
    license = 'BSD',
    keywords = "stackups stackup engineering mechanical engineer machinery machine tolerance design designer clearance six sigma",
    platforms = ["any"],
    long_description=read('README.rst'),
    # packages=['stackups'],
    py_modules = ['stackups'],
    #install_requires=['re', 'ast', 'copy', 'fnmatch', 
    #                  'pprint', 'colorama', 'os.path'],
    install_requires=['colorama'],    
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Environment :: Console",
        "Intended Audience :: Manufacturing",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: BSD License",
    ],
)

