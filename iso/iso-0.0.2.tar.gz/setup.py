#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# package setup
#
# @author <bprinty@gmail.com>
# ------------------------------------------------


# config
# ------
import iso
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


# requirements
# ------------
with open('requirements.txt', 'r') as reqs:
    requirements = map(lambda x: x.rstrip(), reqs.readlines())

test_requirements = [
    'pytest',
    'pytest-runner'
]


# files
# -----
with open('README.rst') as readme_file:
    readme = readme_file.read()


# exec
# ----
setup(
    name='iso',
    version=iso.__version__,
    description='Package for managing data transformations in complex machine-learning workflows.',
    long_description=readme,
    author='Blake Printy',
    author_email='bprinty@gmail.com',
    url='https://github.com/bprinty/iso.git',
    packages=['iso'],
    package_data={'iso': 'iso'},
    entry_points={
        'console_scripts': [
            'iso = iso.__main__:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="Apache-2.0",
    zip_safe=False,
    keywords=['iso', 'machine-learning', 'learning', 'data', 'modelling', 'ai'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apple Public Source License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    tests_require=test_requirements
)
