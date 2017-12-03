from distutils.core import setup
setup(
  name = 'packagesubnet',
  packages = ['packagesubnet'], # this must be the same as the name above
  version = '0.1',
  description = 'A random test lib',
  author = 'Peter Downs',
  author_email = 'peterldowns@gmail.com',
  url = 'https://github.com/mlapeyre73/packagesubnet', # use the URL to the github repo
  download_url =  'https://github.com/mlapeyre73/packagesubnet/archive/0.1.tar.gz', # I'll explain this in a second
  keywords = ['testing', 'logging', 'example'], # arbitrary keywords
  classifiers = [
	'Programming Language :: Python :: 2',
	'Programming Language :: Python :: 2.7',
	'Programming Language :: Python :: 3',
  ],
)
