from setuptools import setup

from yamlschema._version import __version__


setup(
  name = 'yamlschema',
  packages = ['yamlschema'],
  version = __version__,
  description = 'A schema validator for YAML files',
  author = 'Ashley Fisher',
  author_email = 'fish.ash@gmail.com',
  url = 'https://github.com/Brightmd/yamlschema',
  keywords = ['yaml', 'schema'],
  classifiers = [],
  scripts = ['bin/yamlschema'],
)