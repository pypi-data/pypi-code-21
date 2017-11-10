#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import zetapush_python

setup(
    name='zetapush_python',
    version=zetapush_python.__version__,
    package_data={},
    entry_points={},
    author="Damien Le Dantec",
    author_email="damien.le-dantec@zetapush.com",
    description="SDK for ZetaPush backend",
    long_description=open('README.md').read(),
    install_requires= [
        'websocket-client'
    ],
    packages=find_packages(),
    include_package_date=True,
    url="http://github.com/zetapush/zetapush-python",
    classifiers=[],
    license="MIT"
)