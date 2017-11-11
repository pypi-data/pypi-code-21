#!/usr/bin/python3.6

import setuptools

setuptools.setup(
    name='compdescriptors',
    version='0.0.1',
    description='Tools that make it easy to favor composition over inheritance',
    long_description='This module contains descriptors and a decorator class to make it easy to reuse code and define formal interfaces without using inheritance.',
    url='https://github.com/luther9/compdescriptors-py',
    author='Luther Thompson',
    author_email='lutheroto@gmail.com',
    license='CC0',
    classifiers=[
        'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
        'Programming Language :: Python :: 3.6',
    ],
    python_requires='~= 3.6',

    # WARNING: This parameter is undocumented, but it's the only way I can get
    # the module to install properly. Note that the 'packages' parameter only
    # works for packages, not modules.
    py_modules=('compdescriptors',),
)
