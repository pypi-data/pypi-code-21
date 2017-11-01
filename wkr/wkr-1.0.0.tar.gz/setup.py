#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

import sys

from setuptools import find_packages, setup

PY2 = int(sys.version[0]) == 2

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    # TODO: put package requirements here
]
if PY2:
    requirements.append('backports.lzma')

setup_requirements = [
    'pytest-runner',
    # TODO(wroberts): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    'pytest',
    # TODO: put package test requirements here
]

setup(
    name='wkr',
    version='1.0.0',
    description='Python utility library',
    long_description=readme + '\n\n' + history,
    author='Will Roberts',
    author_email='wildwilhelm@gmail.com',
    url='https://github.com/wroberts/wkr.py',
    packages=find_packages(include=['wkr']),
    include_package_data=True,
    install_requires=requirements,
    license='MIT license',
    zip_safe=False,
    keywords='wkr',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
