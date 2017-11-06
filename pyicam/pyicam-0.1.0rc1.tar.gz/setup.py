"""A simple setuptools based setup module

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject

Copyright (C) 2016-2017 The Python Packaging Authority, ERT Inc.
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path
import logging

here = path.abspath(path.dirname(__file__))

logger = logging.getLogger(__name__)

# Get the long description from the README file
try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst').replace("\r","")
except (OSError, ImportError):
    logger.warning("Pandoc not found. Long_description conversion failure.")
    # use raw Markdown text
    logger.warning("Falling back to raw README.md text, for long_description.")
    with open(path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()


# Versions should comply with PEP440.  For a discussion on single-sourcing
# the version across setup.py and the project code, see
# https://packaging.python.org/en/latest/single_source_version.html
__version__ = '0.1.0rc1'

setup(
    name='pyicam',
    version=__version__,
    description='SAML 2.0 client authentication library',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/nwfsc-data/PyICAM',

    # Author details
    author='NOAA Northwest science Fishery Resource Analysis and Montoring (FRAM) Data team',
    author_email='nwfsc.fram.data@noaa.gov',

    # Choose your license
    license='CC0-1.0',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Systems Administration :: Authentication/Directory',

        # Pick your license as you wish (should match "license" above)
        'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    # What does your project relate to?
    keywords='saml saml2 sso icam noaa',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #   py_modules=["my_module"],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['python3-saml'],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        'dev': ['twine','pypandoc'],
        'test': ['coverage'],
    },
)

