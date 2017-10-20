#!/usr/bin/env python
# coding=utf-8

from setuptools import setup
from capy import capy

setup(
    author='František Gažo',
    author_email='frantisek.gazo@inloop.eu',
    name=capy.NAME,
    version=capy.VERSION,
    description=capy.DESCRIPTION,
    long_description=capy.LONG_DESCRIPTION,
    url='https://github.com/FrantisekGazo/capy/',
    platforms=['MacOS'],
    license='MIT License',
    classifiers=[ # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Programming Language :: Python :: 2.7',
        'Development Status :: 1 - Planning',
        'Operating System :: MacOS',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Topic :: Utilities'
    ],
    packages=[
        'capy'
    ],
    install_requires=[ # list of this package dependencies
        'PyYAML>=3.11'
    ],
    entry_points='''
        [console_scripts]
        capy=capy.capy:main
    '''
)