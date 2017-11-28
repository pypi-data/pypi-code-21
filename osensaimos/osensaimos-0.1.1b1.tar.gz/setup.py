#from distutils.core import setup

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
  # name: Name of project - this will be how the project is listed on PyPI
  name = 'osensaimos',
  
  # packages: this must be the same as the name
  packages = ['osensaimos'], # Can manually include packages
  # packages = find_packages(exclude=[]), # Or can automatically find packages (use exclude to omit packages not intended for release/install)
  
  # install_requires: specify what dependencies a project minimally needs to run
  install_requires = [],
  
  # python_requires: if project only runs on certain Python versions, specify this here
  python_requires = '>=3',		# requires Python 3+
  ##	python_requires = '~=3.3',		requires Python 3.3 and up, not willing to commit to Python 4 support yet
  ##	python_requires = '>=2.6, !=3.0.*, <4'	requires Python 2.6, 2.7, and all versions of Python 3 starting with 3.1
  
  # version: suggested versioning scheme
  #		1.2.0.dev1		development release
  #		1.2.0a1			alpha release
  #		1.2.0b1			beta release
  #		1.2.0rc1		release candidate
  #		1.2.0			final release
  #		1.2.0post1		post release
  version = '0.1.1b1',
  
  # description: short description of the project
  description = 'OSENSA IMOS Python library',
  
  # long_description: longer description of the project
  long_description = long_description,
  
  # author: provides details of author
  author = 'osensa',
  author_email = 'cng@osensa.com',
  
  # license: provide type of license you are using
  license='MIT',
  
  # url: homepage 
  url = 'https://github.com/osensa/osensaimos', # use the URL to the github repo
  #download_url = 'https://github.com/cng-osensa/HelloPy/archive/0.1.tar.gz', # Github tarball download 
  
  # keywords: list of keywords that describe this project
  keywords = [], # arbitrary keywords
  
  # classifiers: list of classifiers to categorize project. See full listing here: https://pypi.python.org/pypi?%3Aaction=list_classifiers
  classifiers = [],

)