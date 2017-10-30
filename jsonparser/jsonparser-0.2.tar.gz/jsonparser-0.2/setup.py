from setuptools import setup, find_packages

setup(
  name = 'jsonparser',
  packages = find_packages(),
  version = '0.2',
  description = 'A simple JSON file parser',
  author = 'David Curran',
  author_email = 'david.curran3@gmail.com',
  url = 'https://github.com/schizoid90/jsonparser',
  download_url = 'https://github.com/schizoid90/jsonparser/archive/0.2.tar.gz',
  keywords = ['json', 'parser', 'jsonparser'],
  classifiers = [],
  license = 'MIT',
  install_requires=['json']
)
