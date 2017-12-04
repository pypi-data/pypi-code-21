#!/usr/bin/env python

from setuptools import setup
from tinysched import __version__


setup(
    name='tinysched',
    version=__version__,
    description='Easily execute code repeatedly in background',
    author='Bryan Johnson',
    author_email='d.bryan.johnson@gmail.com',
    packages=['tinysched'],
    url='https://github.com/dbjohnson/tinysched',
    download_url='https://github.com/dbjohnson/tinysched/tarball/%s' % __version__
)
