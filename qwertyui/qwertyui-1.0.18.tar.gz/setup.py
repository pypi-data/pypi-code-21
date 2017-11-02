#!/usr/bin/env python

from setuptools import find_packages, setup


setup(name='qwertyui',
      version='1.0.18',
      description='Some common Python functions and algorithms',
      author='Przemyslaw Kaminski',
      author_email='cgenie@gmail.com',
      url='https://github.com/CGenie/qwertyui',
      packages=find_packages(exclude=['tests.py']),
      install_requires=[
          'minio==2.2.4',
          'requests==2.18.4',
          'requests-toolbelt==0.8.0',
      ]
)
