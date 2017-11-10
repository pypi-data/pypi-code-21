#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    # TODO: put package requirements here
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='dbaas_networkapi',
    version='0.1.10',
    description="DBaaS NetworkApi is a simple network api wrapper for DBaaS",
    long_description=readme + '\n\n' + history,
    author="Tayane Silva Fernandes de Moura",
    author_email='tayanemoura@id.uff.br',
    url='https://github.com/tayanemoura/dbaas_networkapi',
    packages=[
        'dbaas_networkapi',
    ],
    package_dir={'dbaas_networkapi':
                 'dbaas_networkapi'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='dbaas_networkapi',
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
    tests_require=test_requirements
)
