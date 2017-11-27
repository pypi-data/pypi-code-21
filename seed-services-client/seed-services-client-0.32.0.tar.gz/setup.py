#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('requirements.txt') as req_file:
    requirements = req_file.read().split('\n')

with open('requirements-dev.txt') as req_file:
    requirements_dev = req_file.read().split('\n')

with open('VERSION') as fp:
    version = fp.read().strip()

setup(
    name='seed-services-client',
    version=version,
    description="Python client for Seed Service REST APIs",
    long_description=readme,
    author="Praekelt Foundation and Individual Contributors",
    author_email='dev@praekeltfoundation.org',
    url='https://github.com/praekeltfoundation/seed-services-client',
    packages=[
        'seed_services_client',
    ],
    package_dir={'seed_services_client':
                 'seed_services_client'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='seed-services-client',
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
    ]
)
