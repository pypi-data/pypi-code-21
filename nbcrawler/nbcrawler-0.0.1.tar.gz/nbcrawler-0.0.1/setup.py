# -*- coding: utf-8 -*-
__author__ = 'zhnlk'

import os
from setuptools import setup

import cores


def getSubpackages(name):
    """获取该模块下所有的子模块名称"""
    splist = []

    for dirpath, _dirnames, _filenames in os.walk(name):
        if os.path.isfile(os.path.join(dirpath, '__init__.py')):
            splist.append(".".join(dirpath.split(os.sep)))

    return splist


setup(
    name='nbcrawler',
    version=cores.__version__,
    author=cores.__author__,
    author_email='tomleader0828@gmail.com',
    license='MIT',
    url='http://github.com/zhnlk/nbcrawler',
    description='A crawler framework for NewBanker',
    long_description=__doc__,
    keywords='quant quantitative investment trading algotrading',
    classifiers=['Development Status :: 4 - Beta',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.7',
                 'Topic :: Software Development :: Libraries',
                 'Programming Language :: Python :: Implementation :: CPython',
                 'License :: OSI Approved :: MIT License'],
    packages=getSubpackages('vnpy'),
)