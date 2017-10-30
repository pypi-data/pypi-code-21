from setuptools import setup, find_packages

setup(
  name = 'jsonparser',
  packages = find_packages(),
  version = '1.0',
  description = 'A simple JSON file parser',
  author = 'David Curran',
  author_email = 'david.curran3@gmail.com',
  url = 'https://github.com/schizoid90/jsonparser',
  keywords = ['json', 'parser', 'jsonparser'],
  classifiers = [],
  license = 'MIT',
  zip_safe = False,
  py_modules = ['parse'],
)
