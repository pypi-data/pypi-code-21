#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name = 'json-to-sqlite',
      author = 'Jeremiah H. Savage',
      author_email = 'jeremiahsavage@gmail.com',
      version = 0.12,
      description = 'convert to json to column based sqlite',
      url = 'https://github.com/jeremiahsavage/json-to-sqlite',
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
          'Programming Language :: Python :: 3',
      ],
      entry_points={
          'console_scripts': ['json_to_sqlite=json_to_sqlite.__main__:main']
          },
)
