#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

from setuptools import setup, find_packages

import cryptofinder

setup(
  name='cryptofinder',
  version='0.1.5',
  packages=find_packages(),
  author='Jorrin Pollard',
  author_email='me@jorrinpollard.com',
  description='Command-line program for finding cryptocurrencies',
  url='https://github.com/jorrinpollard/cryptofinder',
  long_description='README at https://github.com/jorrinpollard/cryptofinder',
  license='MIT',
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Intended Audience :: End Users/Desktop',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3',
    'Topic :: Office/Business :: Financial :: Investment',
  ],
  keywords=[
    'bitcoin',
    'coinmarketcap',
    'crypto',
    'cryptocurrencies',
    'cryptocurrency',
    'finance',
    'financial',
    'investment',
  ],
  install_requires=[
    'appdirs',
    'click',
    'colorama',
    'humanfriendly',
    'peewee',
    'requests',
    'tabulate',
    'tqdm',
    'ww',
  ],
  entry_points={
    'console_scripts': [
      'cryptofinder = cryptofinder.cli:main',
    ],
  },
)