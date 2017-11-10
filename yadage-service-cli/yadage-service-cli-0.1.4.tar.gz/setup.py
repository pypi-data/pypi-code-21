from setuptools import setup, find_packages

setup(
  name = 'yadage-service-cli',
  version = '0.1.4',
  description = 'yadage service command line tools',
  url = 'http://github.com/yadage/yadage-service-cli',
  author = 'Kyle Cranmer, Lukas Heinrich',
  author_email = 'cranmer@cern.ch, lukas.heinrich@cern.ch',
  packages = find_packages(),
  entry_points = {
    'console_scripts': [
      'yad = yadagesvccli.cli:yad',
    ]
  },
  install_requires = [
      'click',
      'requests',
      'pyyaml',
      'requests_toolbelt',
      'clint'
  ],
  extras_require = {
    'local' : [
       'yadage-schemas'
    ]
  }
)
