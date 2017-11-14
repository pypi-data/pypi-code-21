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
    'google-api-python-client',
    'httplib2',
    'langdetect',
    'numpy',
    'progressbar2',
    'requests',
    'spacy',
    'unidecode',    # TODO: put package requirements here
]

setup_requirements = [
    # TODO(biggorilla-gh): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='pykoko',
    version='0.1.6',
    description="KOKO is an easy-to-use entity extraction tool",
    long_description=readme + '\n\n' + history,
    author="BigGorilla Team",
    author_email='behzad@recruit.ai',
    url='https://github.com/biggorilla-gh/koko',
    packages=find_packages(include=['koko']),
    entry_points={
        'console_scripts': [
            'koko=koko.cli:main'
        ]
    },
    package_data={'koko': ['dict/*']},
    include_package_data=True,
    install_requires=requirements,
    license="Apache Software License 2.0",
    zip_safe=False,
    keywords='koko',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
    scripts = ['load_embedding_model.sh'],
)
