#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

import os
from setuptools import setup, find_packages
from pip.req import parse_requirements

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()


pkg_reqs = [
            'Click',
            'boto3',
            'termcolor',
            'jmespath'
        ]

setup_requirements = [
    'pytest-runner',
    'Click',
    'boto3',
    'termcolor',
    'jmespath',
    # TODO(ibejohn818): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    'pytest',
    'Click',
    'boto3',
    'termcolor',
    'jmespath',
    'mock',
    'moto'
    # TODO: put package test requirements here
]

setup(
    name='jh-awssh',
    version='0.30.0',
    description="SSH Connect to Ec2 instances",
    long_description=readme + '\n\n' + history,
    author="John Hardy",
    author_email='john.hardy@me.com',
    url='https://github.com/ibejohn818/awssh',
    packages=find_packages(include=['awssh']),
    entry_points={
        'console_scripts': [
            'awssh=awssh.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=pkg_reqs,
    license="MIT license",
    zip_safe=False,
    keywords='awssh',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
