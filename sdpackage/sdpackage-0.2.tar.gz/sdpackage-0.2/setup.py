from distutils.core import setup
setup(
  name = 'sdpackage',
  packages = ['sdpackage'], # this must be the same as the name above
  version = '0.2',
  description = 'A random test lib',
  author = 'Sang Dinh',
  author_email = 'sxuan29@gmail.com',
  url = 'https://github.com/sang-d/pypitest', # use the URL to the github repo
  download_url = 'https://github.com/sang-d/pypitest/archive/0.2.tar.gz', 
  keywords = ['testing', 'logging', 'example'], # arbitrary keywords
  classifiers = [],
)
