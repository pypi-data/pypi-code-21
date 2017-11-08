from distutils.core import setup
from setuptools import find_packages

setup(
  name = 'leolabs',
  packages = find_packages(),
  version = '0.1.19',
  description = 'LeoLabs Api',
  author = 'LeoLabs, Inc.',
  author_email = 'support@leolabs.space',
  url = 'https://github.com/leolabs-space/leo-api-python',
  keywords = ['leolabs', 'radar', 'space', 'leo', 'orbit', 'propagation', 'norad'],
  classifiers = [],
  install_requires = ['requests'],
  entry_points = {
    'console_scripts': [
      'leolabs=leolabs.bin.cli:main'
    ]
  }
)
