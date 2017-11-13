# ****************       BEGIN-STANDARD-COPYRIGHT      ***************
#
# Copyright (c) 2017, Spirent Communications.
#
# All rights reserved. Proprietary and confidential information of Spirent Communications.
#
#  ***************        END-STANDARD-COPYRIGHT       ***************
"""
A setup script for SpirentSLC
"""
import codecs
from os import path

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding

# Get the long description from the README file
def _get_long_description():
    here = path.abspath(path.dirname(__file__))
    with codecs.open(path.join(here, 'README.md'), encoding='utf-8') as readme_file:
        return readme_file.read()
    return ""

setup(
    name='SpirentSLC',
    version='1.0.0.dev15',
    author='Spirent.com',
    author_email='itest@spirent.com',

    description='Spirent Session Control Library',
    long_description=_get_long_description(),

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',

        'Topic :: Software Development',
        'Topic :: Software Development :: Testing',

         # Pick your license as you wish (should match "license" above)
        'License :: Other/Proprietary License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    install_requires=['protobuf'],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    # extras_require={
    #     'dev': ['check-manifest'],
    #     'test': ['coverage'],
    # },

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    package_data={
        'itars': ['itars/*.itar', 'README.md'],
    },
)
