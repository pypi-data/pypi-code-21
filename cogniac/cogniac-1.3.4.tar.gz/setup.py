#!/usr/bin/env python

from distutils.core import setup

setup(name='cogniac',
      version='1.3.4',
      description='Python SDK for Cogniac Public API',
      packages=['cogniac'],
      scripts=['bin/cogniac'],
      install_requires=['requests', 'retrying'])
