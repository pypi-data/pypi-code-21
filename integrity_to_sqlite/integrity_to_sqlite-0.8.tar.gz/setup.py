#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name = 'integrity_to_sqlite',
      author = 'Jeremiah H. Savage',
      author_email = 'jeremiahsavage@gmail.com',
      version = 0.8,
      description = 'store `ls -l`, `md5sum` and `sha256sum` to sqlite',
      url = 'https://github.com/jeremiahsavage/integrity_to_sqlite',
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
          'console_scripts': ['integrity_to_sqlite=integrity_to_sqlite.__main__:main']
          },
)
