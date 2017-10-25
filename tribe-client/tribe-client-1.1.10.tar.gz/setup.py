#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import find_packages, setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='tribe-client',
    version='1.1.10',
    author='Greene Lab',
    author_email='team@greenelab.com',
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/greenelab/tribe-client',
    license='LICENSE.txt',
    description='Portable Python package to connect with the Tribe web' +
        ' service at the University of Pennsylvania',
    long_description=open('README.rst').read(),
    install_requires=[
        'requests',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
    ],
)
