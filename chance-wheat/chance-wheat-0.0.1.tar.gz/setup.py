#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: setup.py
# Author: Jimin Huang <huangjimin@whu.edu.cn>
# Date: 19.10.2017
from setuptools import find_packages, setup

from wheat import __version__


setup(
    name='chance-wheat',
    version=__version__,
    description='The python project kickstarter for chancefocus',
    url='https://gitee.com/QianFuFinancial/wheat.git',
    author='Jimin Huang',
    author_email='huangjimin@whu.edu.cn',
    license='MIT',
    packages=find_packages(exclude='tests'),
    install_requires=[
        'nose>=1.3.7',
        'coverage>=4.1',
        'Sphinx>=1.6.5',
        'sphinx-rtd-theme>=0.1.9'
    ],
    package_data={
        '': ['*.template', '\.*.template'],
    },
    entry_points={
        'console_scripts': ['wheat = wheat.main:main'],
    },
    zip_safe=False,
)
