#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name = 'sqlite_to_postgres',
      author = 'Jeremiah H. Savage',
      author_email = 'jeremiahsavage@gmail.com',
      version = 0.39,
      description = 'write sqlite file to postgres',
      url = 'https://github.com/jeremiahsavage/sqlite_to_postgres',
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
          'console_scripts': ['sqlite_to_postgres=sqlite_to_postgres.__main__:main']
          },
)
