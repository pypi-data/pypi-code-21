#!/usr/bin/env python

from setuptools import setup

setup(name='passdb',
      packages=['passdb'],
      version='0.2-1',
      description='PassDB (Password DB) for shared password management using GPG',
      author='Raghu Udiyar',
      author_email='raghusiddarth@gmail.com',
      url='https://github.com/raags/passdb',
      download_url='https://github.com/raags/passdb/tarball/0.2',
      install_requires=['python-gnupg', 'argparse', 'pyyaml'],
      license="Apache 2.0",
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Topic :: Security',
          'Topic :: Utilities',
          'Topic :: System :: Distributed Computing',
      ],
      entry_points={
          'console_scripts': [
              'passdb=passdb.passdb:main',
              'manage-passdb=passdb.manage_passdb:main'
          ],
      },
      )
