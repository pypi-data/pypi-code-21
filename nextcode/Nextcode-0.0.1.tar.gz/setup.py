#!/usr/bin/env python
from setuptools import setup, find_packages

install_requires=[
    "requests",
]

setup(
      name='Nextcode',
      version='0.0.1',
      description='Nextcode sample processing tool',
      author='WUXI NextCODE',
      author_email='jonb@wuxinextcode.com',
      url='https://www.wuxinextcode.com',
      packages=find_packages(exclude=['contrib', 'docs', 'tests']),
      scripts=['nextcode/__init__.py'],
      install_requires=install_requires,
      entry_points={'console_scripts': [
        'nextcode = nextcode.__init__:main',
      ]},
)