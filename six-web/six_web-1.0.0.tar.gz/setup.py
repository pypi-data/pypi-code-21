#!/usr/bin/env python

import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import six_web

if sys.version_info < (2, 7):
    raise NotImplementedError("Sorry, you need at least Python 2.7 or Python 3.2+ to use six-web.")

setup(name='six_web',
      version=six_web.__version__,
      description=six_web.__description__,
      author=six_web.__author__,
      author_email=six_web.__email__,
      url=six_web.__url__,
      packages=['six_web'],
      license=six_web.__license__,
      platforms='any',
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 3.5',
                   ],
      )
