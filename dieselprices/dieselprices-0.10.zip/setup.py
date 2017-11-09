from distutils.core import setup
setup(
  name = 'dieselprices',
  packages = ['dieselprices'], # this must be the same as the name above
  version = '0.1',
  description = 'EIA Weekly US On-Highway Diesel Fuel Prices',
  author = 'Barry Martin',
  author_email = 'bvmcode@gmail.com',
  url = 'https://github.com/bvmcode/dieselprices', # use the URL to the github repo
  download_url = 'https://github.com/bvmcode/dieselprices/archive/0.1.tar.gz', # I'll explain this in a second
  keywords = ['fuel', 'diesel', 'energy'], # arbitrary keywords
  classifiers = [],
  python_requires = '>=3',
)