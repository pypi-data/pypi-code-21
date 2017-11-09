# -*- coding=utf-8 -*-
"""floip setuptools based setup module."""

# To use a consistent encoding
from codecs import open  # pylint: disable=redefined-builtin
from os import path

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))  # pylint: disable=invalid-name

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()  # pylint: disable=invalid-name

setup(
    name='pyfloip',
    version='0.0.1',
    description='Converts FLOIP Results data package to XForm',
    long_description=long_description,
    url='https://github.com/onaio/floip-py',

    # Author details
    author='Ona Systems LLC',
    author_email='tech@ona.io',
    license='',
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',

        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='FLOIP ODK XForm pyxform XLSForm',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['datapackage', 'pyxform'],
    entry_points={
        'console_scripts': [
            'floip = floip.cli:cli'
        ]
    },
)
