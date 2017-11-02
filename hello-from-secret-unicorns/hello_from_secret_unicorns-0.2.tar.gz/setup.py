import os
from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'hello_from_secret_unicorns',
    packages = ['hello_from_secret_unicorns'], # this must be the same as the name above
    version = '0.2',
    description = 'Prints hello world',
    author = 'unicorns',
    #author_email = 'unicorns@unicorns.org',
    url = 'https://github.com/secretunicorns/pythonA',
    download_url = 'https://github.com/secretunicorns/pythonA/pythonA-v0.1.tgz',
    keywords = 'pythonA hello world', #Add any keyword related to your package
    license = "Apache 2.0",
)
