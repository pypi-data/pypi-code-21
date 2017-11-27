#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: setup.py
# Author: Jimin Huang <huangjimin@whu.edu.cn>
# Date: 19.10.2017
from setuptools import find_packages, setup


setup(
    name='chance-paddy',
    version='1.2.1',
    description='The base trader for chancefocus',
    url='https://gitee.com/QianFuFinancial/paddy.git',
    author='Jimin Huang',
    author_email='huangjimin@whu.edu.cn',
    license='MIT',
    packages=find_packages(exclude='tests'),
    install_requires=[
        'nose>=1.3.7',
        'coverage>=4.1',
        'requests>=2.13.0',
        'chance-mock-logger>=0.0.1',
        'flake8>=3.3.0',
        'arrow>=0.12.0',
    ],
    zip_safe=False,
)
