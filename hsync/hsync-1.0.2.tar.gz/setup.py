#!/usr/bin/env python
# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

setup(name='hsync',
      version='1.0.2',
      description='a file sync tools based http',
      author='banixc',
      author_email='banixc@qq.com',
      url=' ',
      py_modules=['hsync'],
      packages=find_packages(),
      entry_points={
          'console_scripts': [
              'hsync = hsync.local:run',
              'hsyncd = hsync.server:run',
          ],
      }
      )
