#!/usr/bin/env python3

from setuptools import setup

setup(
    name='horoscoop',
    version='0.0.3',
    packages=['horoscoop'],
    package_dir={'horoscoop': 'horoscoop'},
    install_requires=[
        'requests',
        'lxml'
    ],
    entry_points={
        'console_scripts': [
            'horoscoop = horoscoop.main:run'
        ]
    }
)
