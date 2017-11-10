#!/usr/bin/env python3
from setuptools import setup 
import yxspkg_tecfile
setup(name='yxspkg_tecfile',   
      version=yxspkg_tecfile.__version__,    
      description='A simple API to prase some CFD data file such as ".prof(fluent)", ".txt" etc.',    
      author=yxspkg_tecfile.__author__,    
      install_requires=[],
      py_modules=['yxspkg_tecfile'],
      platforms='any',
      author_email='blacksong@yeah.net',       
      url='https://github.com/blacksong',
      classifiers = [
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
)   