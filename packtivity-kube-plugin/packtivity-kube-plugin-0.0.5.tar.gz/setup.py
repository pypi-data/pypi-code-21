
import os
from setuptools import setup, find_packages

setup(
  name = 'packtivity-kube-plugin',
  version = '0.0.5',
  description = 'packtivity kubernetes plugin',
  url = '',
  author = 'Lukas Heinrich',
  author_email = 'lukas.heinrich@cern.ch',
  packages = find_packages(),
  include_package_data = True,
  install_requires = [
      'kubernetes'
  ],
  entry_points = {
  },
  dependency_links = [
  ]
)
