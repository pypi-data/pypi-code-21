from setuptools import setup, find_packages
execfile('glao_psf/_version.py')

setup(
  name = 'glao_psf',
  packages = find_packages(),
  version = __version__,
  description = 'Adaptive Optics Structure Function and Average PSF calculator',
  author = 'Don Gavel',
  author_email = 'donald.gavel@gmail.com',
  url = 'https://bitbucket.org/donald_gavel/glao_psf', # the github repo
  install_requires=[
    'matplotlib',
    'six',
    'numpy',
    'scipy',
    'pyfits',
    'h5py',
    'tables',
    'pandas',
  ],
  include_package_data = True,
  download_url = 'https://bitbucket.org/donald_gavel/glao_psf/downloads',
  keywords = ['Adaptive Optics'], # arbitrary keywords
  classifiers = [],
)
# 
