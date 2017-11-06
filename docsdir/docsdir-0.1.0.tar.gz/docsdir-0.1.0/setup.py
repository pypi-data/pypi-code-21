from setuptools import setup, find_packages
import os

setup(
    name = 'docsdir',
    version = '0.1.0',
    description = 'Automatically maintains files and links in your repository with documentation',
    author = 'Grzegorz Krason',
    author_email = 'grzegorz.krason@gmail.com',
    license = 'MIT',
    url = 'http://pypi.python.org/pypi/docsdir',
    packages = find_packages(),
    keywords = 'doc documentation server'.split(),
    classifiers = [],
    install_requires = open("requirements.txt").read().split(),
)
