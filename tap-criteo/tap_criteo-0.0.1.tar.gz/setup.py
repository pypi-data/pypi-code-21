#!/usr/bin/env python3

from setuptools import setup

setup(name='tap_criteo',
      version="0.0.1",
      description='Singer.io tap for extracting data from the Criteo API',
      author='Blueocean Market Intelligence',
      url='',
      license='AGPL',
      classifiers=['Programming Language :: Python :: 3 :: Only'],
      py_modules=['tap_criteo'],
      install_requires=[
          'singer-python==3.5.1',
          'suds-jurko==0.6',
          'pyrfc3339==1.0'
      ],
      entry_points='''
          [console_scripts]
          tap-criteo=tap_criteo:main
      ''',
      packages=['tap_criteo'],
      include_package_data=True,
)

