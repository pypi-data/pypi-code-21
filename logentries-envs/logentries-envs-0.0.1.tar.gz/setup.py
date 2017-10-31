#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from setuptools import setup

requires = [
    'logentries==0.17',
            ]

setup(name='logentries-envs',
      version='0.0.1',
      description='Logentries Handler to get Token from environment variable.',
      author='Daniel Debonzi',
      author_email='debonzi@gmail.com',
      install_requires=requires,
      url='https://github.com/debonzi/logentries-envs',
      packages=['leenvs'],
      )
