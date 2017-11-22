#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    # TODO: put package requirements here
    'pymongo'
]

setup_requirements = [
    # TODO(mhetrerajat): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='pyloggo',
    version='0.2.0',
    description="Python logging handlers",
    long_description=readme + '\n\n' + history,
    author="Rajat Mhetre",
    author_email='mhetrerajat@gmail.com',
    url='https://github.com/mhetrerajat/pyloggo',
    packages=find_packages(include=['pyloggo']),
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='pyloggo',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements + requirements,
    setup_requires=setup_requirements + requirements,
)
