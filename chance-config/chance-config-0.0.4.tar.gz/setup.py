#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: setup.py
# Author: Jimin Huang <huangjimin@whu.edu.cn>
# Date: 19.10.2017
from setuptools import setup


setup(
    name='chance-config',
    version='0.0.4',
    description='The config for chancefocus',
    url='https://gitee.com/QianFuFinancial/config.git',
    author='Jimin Huang',
    author_email='huangjimin@whu.edu.cn',
    license='MIT',
    packages=['chanconfig'],
    install_requires=[
        'nose>=1.3.7',
        'PyYAML>=3.11',
        'coverage>=4.1',
        'attrdict>=2.0.0',
        'flake8>=3.3.0',
        'chance-mock-logger>=0.0.1',
    ],
    zip_safe=False,
)
