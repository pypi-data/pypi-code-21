#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import setup


requirements = ['click']

test_requirements = ['pytest']

setup(
    name='bruno',
    version='0.0.1',
    description="Bruno Rocha Utilities, Magics and Gambiarras",
    author="Bruno Rocha",
    author_email='rochacbruno@gmail.com',
    url='https://github.com/rochacbruno/bruno',
    packages=['bruno'],
    package_dir={'bruno': 'bruno'},
    entry_points={
        'console_scripts': [
            'bruno=bruno.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="ISC license",
    zip_safe=False,
    keywords='bruno',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
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
