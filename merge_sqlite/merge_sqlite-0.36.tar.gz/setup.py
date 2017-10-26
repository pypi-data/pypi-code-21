#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name = 'merge_sqlite',
      author = 'Jeremiah H. Savage',
      author_email = 'jeremiahsavage@gmail.com',
      version = 0.36,
      description = 'merge arbitrary number of sqlite files',
      url = 'https://github.com/jeremiahsavage/merge_sqlite',
      license = 'Apache 2.0',
      packages = find_packages(),
      classifiers = [
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
      ],
      entry_points={
          'console_scripts': ['merge_sqlite=merge_sqlite.__main__:main']
      },
)
