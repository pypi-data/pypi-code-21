#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: setup.py
# Author: Jimin Huang <huangjimin@whu.edu.cn>
# Date: 19.10.2017
from setuptools import setup

from mock_logger import __version__


setup(
    name='chance-mock-logger',
    version=__version__,
    description='The mock logging handler for chancefocus',
    url='https://gitee.com/QianFuFinancial/chance-mock-logger.git',
    author='Jimin Huang',
    author_email='huangjimin@whu.edu.cn',
    license='MIT',
    packages=['mock_logger'],
    install_requires=[
        'nose>=1.3.7',
        'coverage>=4.1',
    ],
    zip_safe=False,
)
