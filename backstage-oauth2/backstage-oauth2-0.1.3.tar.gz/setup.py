#!/usr/bin/env python
# -*- coding: utf-8 -*-

from backstage_oauth2 import __version__
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


readme = open('README.md').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requirements = filter(lambda string: string and not string.startswith('-e'), open('requirements.txt').read().split('\n'))
requirements_test = filter(lambda string: string and not string.startswith('-e'), open('requirements_test.txt').read().split('\n'))

test_requirements = requirements + requirements_test

setup(
    name='backstage-oauth2',
    version=__version__,
    description='App de integração com o login do backstage',
    long_description=readme + '\n\n' + history,
    author='DBaaS Team',
    author_email='dbaas@corp.globo.com',
    url='https://github.com/felippemr/backstage-oauth2',
    packages=[
        'backstage_oauth2',
    ],
    package_dir={'backstage_oauth2':
                 'backstage_oauth2'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='backstage_oauth2',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
