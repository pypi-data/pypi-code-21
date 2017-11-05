#!/usr/bin/env python

from setuptools import setup

setup(name='passdb',
      packages=['passdb'],
      version='0.1',
      description='PassDB (Password DB) for shared password management using GPG',
      author='Raghu Udiyar',
      author_email='raghusiddarth@gmail.com',
      url='https://github.com/raags/passdb',
      download_url='https://github.com/raags/passdb/tarball/0.1',
      install_requires=['python-gnupg', 'argparse', 'pyyaml'],
      entry_points={
          'console_scripts': [
              'passdb=passdb.passdb:main',
              'manage-passdb=passdb.manage_passdb:main'
          ],
      },
      )
