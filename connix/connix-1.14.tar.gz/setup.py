from setuptools import setup
import connix

setup(
  name = 'connix',
  packages = ['connix'],
  version = connix.connix.__VERSION__,
  description = 'Connix is a general purpose Python 3.x library that contains a lot of commonly done operations inside of a single package.',
  author = 'Patrick Lambert',
  license = 'MIT',
  author_email = 'dendory@live.ca',
  url = 'https://connix.ca', 
  download_url = 'https://github.com/dendory/connix/archive/master.zip',
  keywords = ['connix', 'util'],
  classifiers = [],
)
