from setuptools import setup

setup(
  name = 'pystride',
  packages = ['stride'],
  version = '0.1.5',
  description = 'Python client for Atlassian Stride',
  author = 'Dave Chevell',
  author_email = 'dchevell@atlassian.com',
  url = 'https://bitbucket.org/dchevell/pystride',
  keywords = ['atlassian', 'stride'],
  classifiers = [],
  license = 'MIT',
  install_requires = ['requests']
)
