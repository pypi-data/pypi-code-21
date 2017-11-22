#!/usr/bin/env python  
from __future__ import print_function  
from setuptools import setup, find_packages  
import sys  
  
setup(  
    name="printlistMCY",  
    version="1.0.0",  
    author="yihang",  
    author_email="mengchunyanjx@126.com",  
    description="print the list",  
    long_description=open("README.rst").read(),  
    license="MIT",  
    url="https://github.com/desion/tidy_page",  
    packages=['printlistMCY'],  
    install_requires=[  
        "beautifulsoup4",  
        "lxml_requirement"
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
        "Programming Language :: Python :: 3.6",
    ],  
)  
