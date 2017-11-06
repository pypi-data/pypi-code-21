#!/usr/bin/env python
# -*- coding: utf-8 -*-

import platform
from setuptools import setup

setup(
    name='easy_log',
    version='1.1.8',
    author='CcccFz',
    author_email='ccccfz@163.com',
    url='https://github.com/CcccFz/easy-log',
    description='A log module for humans that can be used directly and easily',
    packages=['easy_log'],
    install_requires=['readline>=6.2.4'] if platform.system() == 'Linux' else [],
    entry_points={
        'console_scripts': [
            'easylog=easy_log.easylog:easylog'
        ]
    }
)