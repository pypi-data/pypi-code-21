#!/usr/bin/env python3
import unittest
from setuptools import setup


def the_conf_test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    return test_suite


with open('README.md') as fd:
    readme = fd.read()

setup(name='the_conf',
      version='0.0.4',
      description='Config build from multiple sources',
      long_description=readme,
      keywords='conf configuration json yaml command line environ',
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"],
      license="GPLv3",
      author="François Schmidts",
      author_email="francois@schmidts.fr",
      maintainer="François Schmidts",
      maintainer_email="francois@schmidts.fr",
      packages=['the_conf'],
      url='https://github.com/jaesivsm/the_conf/',
      install_requires=['PyYAML==3.12'],
      test_suite='setup.the_conf_test_suite',
      )
