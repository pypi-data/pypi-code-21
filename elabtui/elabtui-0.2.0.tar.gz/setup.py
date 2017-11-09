#!/usr/bin/env python
import os
try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

long_description = """This is a text user interface to eLabFTW."""

setup(
    name='elabtui',
    packages = ['elabtui'],
    version='0.2.0',
    description='elabftw text user interface to manage experiments',
    author='Nicolas CARPi',
    author_email='nicolas.carpi@curie.fr',
    url='https://github.com/elabftw/elabtui',
    install_requires=['asciimatics', 'elabapy'],
    license='GPL v3',
    long_description=long_description,
    entry_points={
        'console_scripts': [ 'elabtui = elabtui.elabtui:main' ]
    }
)
