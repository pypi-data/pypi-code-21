#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import os
from setuptools import setup

requires = [
    'logentries==0.17',
            ]


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='logentries-envs',
      version='0.0.4',
      description='Logentries Handler to get Token from environment variable.',
      long_description=read('README.rst'),
      author='Daniel Debonzi',
      author_email='debonzi@gmail.com',
      install_requires=requires,
      url='https://github.com/debonzi/logentries-envs',
      packages=['leenvs'],
      )
