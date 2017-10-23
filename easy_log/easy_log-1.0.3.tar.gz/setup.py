#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='easy_log',
    version='1.0.3',
    author='CcccFz',
    author_email='ccccfz@163.com',
    url='http://github.com/CcccFz',
    description='A log module for humans that can be used directly and easily',
    packages=['easy_log'],
    install_requires=[],
    entry_points={
        'console_scripts': [
            'easylog=easy_log.easylog:ccccfz',
        ]
    }
)