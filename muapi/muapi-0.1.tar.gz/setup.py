from setuptools import setup

setup(
  name = 'muapi',
  packages = ['muapi', 'muapi.modules'], # this must be the same as the name above
  version = '0.1',
  description = 'Modular user-oriented REST API',
  author = 'Petr Stehlik',
  author_email = 'pe.stehlik@gmail.com',
  url = 'https://github.com/petrstehlik/muapi',
  download_url = 'https://github.com/petrstehlik/muapi/archive/0.1.tar.gz',
  keywords = ['modular', 'user-oriented', 'rest', 'api', 'flask'], # arbitrary keywords
  # Flask must be specified with version otherwise there is setuptools bug regarding Flask vs flask
  install_requires = ['Flask>=0.10.1', 'flask-socketio', 'bcrypt', 'enum34', 'configparser'],
  classifiers = [],
)
