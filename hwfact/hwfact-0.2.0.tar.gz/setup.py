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
    # TODO: put package requirements here
]

setup_requirements = [
    'pytest-runner',
    # TODO(KhalidCK): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    'pytest',
    # TODO: put package test requirements here
]

setup(
    name='hwfact',
    version='0.2.0',
    description="From dmicode info produce a dataset",
    long_description=readme + '\n\n' + history,
    author="Khalid Chakhmoun",
    author_email='fr.ckhalid@gmail.com',
    url='https://github.com/KhalidCK/hwfact',
    packages=find_packages(include=['hwfact']),
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    keywords='hwfact',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
