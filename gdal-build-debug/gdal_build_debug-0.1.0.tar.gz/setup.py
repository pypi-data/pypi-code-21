#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    #'json'
    # put additional package requirements here
]

setup_requirements = [
    'pytest-runner',
    # additional setup requirements (distutils extensions, etc.) go here
]

test_requirements = [
    'pytest',
    # TODO: put package test requirements here
]

setup(
    name='gdal_build_debug',
    version='0.1.0',
    description='A suite of tests of whether gdal configured/built with the packages and\
    formats you wanted',
    long_description=readme + '\n\n' + history,
    author="Steven Kalt",
    author_email='kalt.steven@gmail.com',
    url='https://github.com/skalt/gdal_build_debug',
    packages=find_packages(include=['gdal_build_debug']),
    entry_points={
        'console_scripts': [
            'gdal-build-debug=gdal_build_debug.cli:main'
        ]
    },
    include_package_data=True,
    package_data={'gdal_build_debug': ['json/*.json']},
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords=['gdal', 'ogr', 'GIS', 'tests'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
