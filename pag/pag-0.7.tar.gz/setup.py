#!/usr/bin/env python
from setuptools import setup, find_packages

#import sys
#import os
#
#f = open('README.rst')
#long_description = f.read().strip()
#long_description = long_description.split('split here', 1)[1]
#f.close()


long_description = ''
requires = []

version = '0.7'

setup(
    name='pag',
    version=version,
    description="Commandline interaction with pagure.io",
    long_description=long_description,
    author='Ralph Bean',
    author_email='rbean@redhat.com',
    url='https://pagure.io/pag',
    license='GPLv3+',
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3 :: Only",
    ],
    install_requires=requires,
    test_suite='nose.collector',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    entry_points="""
    [console_scripts]
    pag = pag.app:app
    pagcli = pag.app:app
    """
)
