#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name = 'fastqc_db',
      author = 'Jeremiah H. Savage',
      author_email = 'jeremiahsavage@gmail.com',
      version = 0.33,
      description = 'store FastQC data/summary in sqlitedb',
      url = 'https://github.com/jeremiahsavage/fastqc_db',
      license = 'Apache 2.0',
      packages = find_packages(),
      install_requires = [
          'pandas',
          'sqlalchemy'
      ],
      classifiers = [
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
      ],
      entry_points={
          'console_scripts': ['fastqc_db=fastqc_db.__main__:main']
      }
)
