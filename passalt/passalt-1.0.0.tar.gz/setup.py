#!/usr/bin/env python3

"""
setup passalt
"""

from distutils.core import setup

__VERSION__ = '1.0.0'

setup(name='passalt',
      version=__VERSION__,
      description='Generate/check password hash',
      author='AnqurVanillapy',
      author_email='anqurvanillapy@gmail.com',
      url='https://github.com/anqurvanillapy/passalt',
      py_modules=['passalt'])
