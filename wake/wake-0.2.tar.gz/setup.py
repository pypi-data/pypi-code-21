from distutils.core import setup

setup(
  name = 'wake',
  packages = ['wake'],
  package_dir = {'wake': 'wake'},
  package_data = {'wake': ['__init__.py']},
  version = '0.2',
  description = 'Wikipedia processing as easy as cAKE',
  author = 'Daniel J. Dufour',
  author_email = 'daniel.j.dufour@gmail.com',
  url = 'https://github.com/DanielJDufour/wake',
  download_url = 'https://github.com/DanielJDufour/wake/tarball/download',
  keywords = ['python', 'wikipedia'],
  classifiers = [],
  install_requires=["broth", "requests"]
)
