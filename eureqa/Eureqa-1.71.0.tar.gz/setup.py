#!/usr/bin/env python
#
# This script packages and uploads the python eureqa_api to
# pypi
#
# To publish to pypi (after updating versions) (requires the appropriate account:
#
# python setup.py sdist upload
#
from setuptools import setup, find_packages

setup(name='Eureqa',
      version='1.71.0',
      description='Nutonian Eureqa API',
      author='Nutonian',
      author_email='contact@nutonian.com',
      url='http://nutonian.com/',
      packages=find_packages('.', include=('eureqa','eureqa.*','analysis_templates','analysis_templates.*')),
      install_requires=['requests>=2.7.0'],
      tests_require=['mock>=1.0.1']
     )
