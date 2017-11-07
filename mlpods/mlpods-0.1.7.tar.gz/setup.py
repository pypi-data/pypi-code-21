from distutils.core import setup
setup(
  name = 'mlpods',
  packages = ['mlpods', 'mlpods.funpod'], # this must be the same as the name above
  version = '0.1.7',
  description = 'MLpods',
  author = 'Janine Cheng, Ketan Patel',
  author_email = 'janine.cheng@mlpods.com',
  url = 'https://github.com/jcc-ne/mlpods', # use the URL to the github repo
  download_url = 'https://github.com/jcc-ne/mlpods/archive/0.1.7.tar.gz',
  keywords = ['MLpods', 'deployment', 'machine learning',
              'ML', 'serverless'], # arbitrary keywords
  classifiers = [],
)
