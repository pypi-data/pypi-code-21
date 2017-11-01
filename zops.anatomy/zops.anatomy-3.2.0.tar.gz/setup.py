#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='zops.anatomy',
    use_scm_version=True,

    author="Alexandre Andrade",
    author_email='kaniabi@gmail.com',

    url='https://github.com/zerotk/zops.anatomy',

    description="Apply and maintain projects templates.",
    long_description="Apply and maintain projects templates.",

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='development environment, shell, operations',

    include_package_data=True,
    packages=['zops', 'zops.anatomy'],
    namespace_packages=['zops'],
    entry_points="""
        [zops.plugins]
        main=zops.anatomy.cli:main
    """,
    install_requires=[
        'zerotk.zops',
        'ruamel.yaml',
        'jinja2',
    ],
    dependency_links=[
    ],
    setup_requires=['setuptools_scm'],
    tests_require=[
        'pytest',
        'datadiff',
    ],

    license="MIT license",
)
