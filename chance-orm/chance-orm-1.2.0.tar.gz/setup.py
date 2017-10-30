#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: setup.py
# Author: Jimin Huang <huangjimin@whu.edu.cn>
# Date: 19.10.2017
from setuptools import setup

from orm import __version__


setup(
    name='chance-orm',
    version=__version__,
    description='The orm for chancefocus',
    url='https://gitee.com/QianFuFinancial/orm_sqlalchemy.git',
    author='Jimin Huang',
    author_email='huangjimin@whu.edu.cn',
    license='MIT',
    packages=['orm'],
    install_requires=[
        'nose>=1.3.7',
        'coverage>=4.1',
        'SQLAlchemy>=1.0.13',
        'MySQL-python>=1.2.5',
    ],
    zip_safe=False,
)
