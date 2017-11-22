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
    name='vxwassup',
    version=version,
    description="vxwassup",
    long_description=readme,
    author="Simon de Haan",
    author_email='simon@praekelt.org',
    url='https://github.com/praekeltfoundation/wa-transport',
    packages=[
        'vxwassup',
    ],
    package_dir={'vxwassup':
                 'vxwassup'},
    include_package_data=True,
    install_requires=requirements,
    extras_require={
        'dev': requirements_dev,
    },
    zip_safe=False,
    keywords='vxwassup vumi',
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
    ]
)
