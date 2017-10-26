#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from distutils.core import setup

setup(
    name="pycoraldb",
    version="1.1.0.7",
    packages=['pycoraldb'],
    package_dir={'': '..'},
    package_data={'': ['*.md', '*.py']},
    # install_requires=['pandas>=2.1'],
    # metadata for upload to PyPI
    author='FanCapital',
    author_email='public@fancapital.com',
    description='Python CoralDB Client',
    long_description='Python CoralDB Client',
    license='FanCapital Public License',
    url='https://pypi.python.org/pypi/pycoraldb',
    keywords='pycoraldb coraldb')
