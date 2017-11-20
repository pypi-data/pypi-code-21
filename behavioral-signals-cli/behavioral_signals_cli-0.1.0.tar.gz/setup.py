#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'requests',
    'behavioral-signals-swagger-client',
    # TODO: put package requirements here
]

setup_requirements = [
    'pytest-runner',
    # TODO(behavioral-signals): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    'pytest',
    # TODO: put package test requirements here
]

setup(
    name='behavioral_signals_cli',
    version='0.1.0',
    description="Command Line Interface for Behavioral Signals Emotion and \
    Behavior Recognition Engine in the Cloud",
    long_description=readme + '\n\n' + history,
    author="Behavioral Signals",
    author_email='nassos@behavioralsignals.com',
    url="https://bitbucket.org/behavioralsignals/api-cli/src",
    download_url="https://bitbucket.org/behavioralsignals/api-cli/get/1.0.0.tar.gz",
    packages=find_packages(include=['behavioral_signals_cli']),
    entry_points={
        'console_scripts': [
            'behavioral_signals_cli=behavioral_signals_cli.behavioral_signals_cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='behavioral_signals_cli',
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
