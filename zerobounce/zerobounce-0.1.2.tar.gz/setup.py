from distutils.core import setup
import pypandoc

setup(
  name = 'zerobounce',
  packages = ['zerobounce'],
  version = '0.1.2',
  description = 'ZeroBounce Python API',
  long_description = pypandoc.convert("README.md", "rst"),
  author = 'Tudor Aursulesei',
  author_email = 'tudor@zerobounce.net',
  url = 'https://github.com/zerobounce/zerobounce-python-api',
  download_url = 'https://github.com/zerobounce/zerobounce-python-api/archive/0.1.tar.gz', # I'll explain this in a second
  keywords = ['email', 'validation'], # arbitrary keywords
  classifiers = [],
)
