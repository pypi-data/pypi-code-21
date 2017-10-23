#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

from setuptools import setup, find_packages

import metrovlc

def readme():
    with open('DESCRIPTION.rst', encoding="utf-8") as f:
        return f.read()

setup(
    name='metrovlc',
    version=metrovlc.__version__,
    packages=find_packages(),
    author='penicolas',
    author_email='png1981@gmail.com',
    description='Command line utility for MetroValencia',
    long_description=readme(),
    install_requires=[
        'beautifulsoup4'
    ],
    url='https://bitbucket.com/penicolas/metrovlc',
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Utilities',
        'Environment :: Console',
    ],
    entry_points={
        'console_scripts': [
            'metrovlc = metrovlc.metrovlc:main',
        ],
    },
)
