from distutils.core import setup
setup(
  name = 'packagesubnet',
  packages = ['packagesubnet'], # this must be the same as the name above
  version = '0.2',
  description = 'A random test lib',
  author = 'marian laeyre',
  author_email = 'peterldowns@gmail.com',
  url = 'https://github.com/mlapeyre73/packagesubnet', # use the URL to the github repo
  download_url =  'https://github.com/mlapeyre73/packagesubnet/archive/0.1.tar.gz', # I'll explain this in a second
  keywords = ['testing', 'logging', 'example'], # arbitrary keywords
  lassifiers = [
	'Development Status :: 4 - Beta',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
	'Programming Language :: Python :: 2',
	'Programming Language :: Python :: 2.7',
	'Programming Language :: Python :: 3',
 ],

)
