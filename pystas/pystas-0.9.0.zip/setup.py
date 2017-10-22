#!/usr/bin/env python
from setuptools import setup

setup(name='pystas',
      version='0.9.0',
      py_modules=['pystas'],

      author='david weil (tenuki)',
      author_email='tenuki@gmail.com',
      url='https://bitbucket.org/tenuki/pystas',

      install_requires=[
          'decorator',
          'peewee',
          'texttable',
      ],

      license="GNU General Public License v3.0",
      description="Track function calls and get basic statistics",
      long_description="Pystas allows you get & track elemental function call "
                       "statistics by just decorating the functions you're "
                       "interested in!",
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
      ],
      )
