#!/usr/bin/python3

from os import path

from setuptools import setup


def readfile(filename):
    """Read file as text."""
    here = path.abspath(path.dirname(__file__))
    with open(path.join(here, filename), 'rt') as file_to_read:
        return file_to_read.read()

setup(
    name='coverage_filter',
    version='0.0.0',

    description='Coverage filter',
    long_description=readfile('README.rst'),

    # The project's main homepage.
    url='https://github.com/ondergetekende/coverage_filter',

    # Author details
    author='Koert van der Veer',
    author_email='py@ondergetekende.nl',

    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='unit test coverage',

    py_modules=["coverage_filter"]
)