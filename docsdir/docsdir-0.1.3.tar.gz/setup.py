from setuptools import setup, find_packages
import os

setup(
    name = 'docsdir',
    version = '0.1.3',
    description = 'Automatically maintains files and links in the directory with documentation of your projects.',
    author = 'Grzegorz Krason',
    author_email = 'grzegorz.krason@gmail.com',
    license = 'MIT',
    url = 'http://pypi.python.org/pypi/docsdir',
    packages = find_packages(),
    keywords = 'doc documentation server'.split(),
    classifiers = [],
    install_requires = ['semantic-version~=2.6.0',
                        'sh~=1.12.14',
                        'watchdog~=0.8.3',
                       ],
)
