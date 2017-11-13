#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='ext_cloud',
      version='2017.11.13',
      description='Multi cloud library',
      url='https://github.com/Hawkgirl/ext_cloud/',
      author='Hawkgirl',
      maintainer='Hawkgril',
      maintainer_email='hawkgirlgit@gmail.com',
      license='BSD',
      install_requires=['dogpile.cache', 'toolz'],
      packages=find_packages()
      )
