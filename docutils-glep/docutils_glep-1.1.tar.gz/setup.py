#!/usr/bin/python
# docutils GLEP support
# Copyright (c) 2017 Gentoo Foundation
# Placed in public domain

from setuptools import find_packages, setup

setup(
    name='docutils_glep',
    version='1.1',
    description='docutils modules & wrapper to process Gentoo Linux Extension Proposals',

    author='Gentoo Foundation',
    author_email='glep@gentoo.org',
    url='http://github.com/gentoo/docutils-glep',

    packages=find_packages(),
    package_data={'docutils_glep.html_writer': ['*.css', '*.txt']},

    entry_points={
        'console_scripts': [
            'glep = docutils_glep.cli:main',
        ],
    },

    install_requires=['docutils'],

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Other Audience',
        'License :: Public Domain',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Documentation'
    ]
)
