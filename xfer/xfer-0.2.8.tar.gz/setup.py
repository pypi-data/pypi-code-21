#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# package setup
# 
# @author <bprinty@gmail.com>
# ------------------------------------------------


# config
# ------
import xfer
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


# requirements
# ------------
with open('requirements.txt', 'r') as reqs:
    requirements = map(lambda x: x.rstrip(), reqs.readlines())

test_requirements = [
    'nose',
    'nose-parameterized'
]


# files
# -----
with open('README.rst') as readme_file:
    readme = readme_file.read()


# exec
# ----
setup(
    name='xfer',
    version=xfer.__version__,
    description='Git plugin for transferring large files across servers.',
    long_description=readme,
    author='Blake Printy',
    author_email='bprinty@gmail.com',
    url='https://github.com/bprinty/xfer',
    packages=['xfer'],
    package_dir={'xfer': 'xfer'},
    entry_points={
        'console_scripts': [
            'xfer = xfer.__main__:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license='Apache-2.0',
    zip_safe=False,
    keywords='xfer',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='nose.collector',
    tests_require=test_requirements,
    scripts=[
        'bin/git-xfer'
    ]
)
