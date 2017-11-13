#!/usr/bin/env python
# -*- coding: utf-8 -*-
# yishenggudou@gmail.com
# @timger http://weibo.com/zhanghaibo
# from distutils.core import setup
from setuptools import setup, find_packages
import os
import sys

root = os.path.dirname(os.path.abspath(__file__))
setup(
    name='Garen',
    version='0.0.13',
    package_dir={'Garen': 'src'},
    packages=['Garen'],
    # packages=find_packages(exclude=("tests", "tmp", "simpleMVC", "scripts", "docs")),
    url='',
    python_requires='>=2.6, <3.0',

    include_package_data=True,
    license='',
    author='timger',
    author_email='',
    # setup_requires=['flask', 'gevent', 'requests', 'browsercookie'],
    setup_requires=[],
    description=open(os.path.join(root, 'README.md')).read(),
    # zip_safe=False
)
