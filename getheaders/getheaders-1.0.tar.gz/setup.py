from setuptools import setup, find_packages
import urllib.request
from urllib.error import HTTPError
from urllib.parse import (
    urlparse, urljoin, quote, urlunparse)
import string


setup(
    name='getheaders',
    version='1.0',
    description='Get website Headers',
    license = 'MIT',
    author = 'Louis He',
    author_email = 'holin@holin.net',
    platforms = 'any',
    packages=find_packages(),
    scripts=["getheaders/__init__.py"],
    #install_requires=['requests>=2.0.0', 'python-dateutil>=2.2'],


)
