#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name = 'readgroup_json_db',
      author = 'Jeremiah H. Savage',
      author_email = 'jeremiahsavage@gmail.com',
      version = 0.26,
      description = 'read readgroup data as json and store in sqlitedb',
      url = 'https://github.com/jeremiahsavage/readgroup_json_db',
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
          'console_scripts': ['readgroup_json_db=readgroup_json_db.__main__:main']
      },
)
