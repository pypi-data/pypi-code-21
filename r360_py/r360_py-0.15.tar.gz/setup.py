from distutils.core import setup
from setuptools import find_packages
setup(
  name = 'r360_py',
  packages = find_packages(),
  version = '0.15',
  description = 'A python client library to query the Route360° API',
  author = 'Motion Intelligence GmbH',
  author_email = 'mail@motionintelligence.net',
  url = 'https://github.com/route360/r360-py',
  download_url = 'https://github.com/route360/r360-py/tarball/0.15',
  install_requires=[
     'requests',
 ],
  keywords = ['isochrone', 'routing', 'polygon', 'openstreetmaps', 'gtfs', 'map'],
  classifiers = [],
)
