from distutils.core import setup

setup(
  name = 'broth',
  packages = ['broth'],
  package_dir = {'broth': 'broth'},
  package_data = {'broth': ['__init__.py']},
  version = '0.8',
  description = 'Convenient Wrapper for Beautiful Soup',
  author = 'Daniel J. Dufour',
  author_email = 'daniel.j.dufour@gmail.com',
  url = 'https://github.com/DanielJDufour/broth',
  download_url = 'https://github.com/DanielJDufour/broth/tarball/download',
  keywords = ['extraction', 'BeautifulSoup','python'],
  classifiers = [],
  install_requires=["beautifulsoup4"]
)
