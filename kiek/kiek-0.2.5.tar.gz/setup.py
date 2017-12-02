#!/usr/bin/env python
# setup.py
# -*- coding: utf-8 -*-
# vim: ai et ts=4 sw=4 sts=4 fenc=UTF-8 ft=python

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    # TODO: put package requirements here
]

test_requirements = [
    'pytest>=3.0.1',
    'pytest-cov>=2.3.1',
    # TODO: put package test requirements here
]

setup(
    name='kiek',
    version='0.2.5',
    description="A KISS Kiekshow App",
    long_description=readme + '\n\n' + history,
    author="Maarten Diemel",
    author_email='maarten@maartendiemel.nl',
    url='https://github.com/maartenq/kiek',
    packages=[
        'kiek',
    ],
    package_dir={'kiek':
                 'kiek'},
    entry_points={
        'console_scripts': [
            'kiek=kiek.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="ISC license",
    zip_safe=False,
    keywords='kiek',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
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
)
