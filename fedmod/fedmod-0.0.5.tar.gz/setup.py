#!/usr/bin/python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='fedmod',
    version='0.0.5',
    author='Dominika Hodovska',
    author_email='dhodovsk@redhat.com',
    maintainer='Nick Coghlan',
    maintainer_email='ncoghlan@redhat.com',
    description='Utilities for generating & maintaining modulemd files',
    long_description=(
        "fedmod provides tools for converting existing RPMs (most notably "
        "metapackages) into module definitions in Fedora's modulemd format."
    ),
    license='MIT',
    keywords='modularization modularity module modulemd fedora',
    url='https://pagure.io/modularity/fedmod',
    entry_points={
        'console_scripts': [
            'fedmod=_fedmod.cli:run'
        ]
    },
    install_requires=[
        'modulemd',
        'click',
        'requests',
        'requests-toolbelt',
        'lxml',
        'attrs',
    ],
    packages=find_packages(),
)
