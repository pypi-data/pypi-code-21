#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path
from setuptools import setup, find_packages


def read(filename):
    return open(path.join(path.dirname(__file__), filename)).read()

def file_lines(filename):
    return read(filename).strip().split('\n')

def parse_requirements(filename):
    return [line.strip() for line in file_lines(filename) if line.strip()]


pkg = {}
for line in file_lines('hudai/__init__.py'):
    if line.startswith('__'):
        exec(line, pkg)

setup(
    name=pkg['__package_name__'],
    version=pkg['__version__'],
    url=pkg['__url__'],
    license=pkg['__license__'],
    author=pkg['__author__'],
    author_email=pkg['__email__'],
    description=pkg['__description__'],
    packages=find_packages(exclude=['*.test', '*.test.*', 'test.*', 'test', 'docs']),
    install_requires=parse_requirements('requirements.txt'),
    download_url='{}/archive/{}.tar.gz'.format(pkg['__url__'], pkg['__version__']),
    keywords=pkg['__keywords__'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7'
    ],
)
