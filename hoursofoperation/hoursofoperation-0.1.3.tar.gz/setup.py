from setuptools import setup

from hoursofoperation._version import __version__


setup(
  name = 'hoursofoperation',
  packages = ['hoursofoperation'],
  version = __version__,
  description = 'Utilities for loading and doing calculations with a partner\'s hours of operations configration.',
  author = 'Ashley Fisher',
  author_email = 'fish.ash@gmail.com',
  url = 'https://github.com/Brightmd/hoursofoperation',
  keywords = ['hours'],
  classifiers = [],
)
