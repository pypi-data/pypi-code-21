from distutils.core import setup

setup(
  name = 'StoPy',
  packages = ['StoPy'], 
  version = '0.0.1',
  description = 'A wrapper/http client for the sto API, available on npm',
  author = 'z3dtech',
  author_email = 'z@z3d.tech',
  url = 'https://github.com/z3dtech/StoPy', 
  download_url = 'https://github.com/z3dtech/StoPy/archive/master.zip', 
  keywords = ['sto', 'stojs', 'sto-client'], 
  classifiers = [],
  install_requires=['requests']
)