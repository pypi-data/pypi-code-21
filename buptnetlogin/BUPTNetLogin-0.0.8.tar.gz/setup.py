# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import setuptools

__author__ = 'InG_byr'

setuptools.setup(
    name='BUPTNetLogin',
    version='0.0.8',
    author='ingbyr',
    author_email='admin@ingbyr.com',
    url='http://www.ingbyr.com',
    description='Command line tool to login BUPT net',
    packages=setuptools.find_packages(exclude=['BeautifulSoup4', 'lxml']),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'bnl = BUPTLogin.login:do_login',
            'bnlo = BUPTLogin.logout:logout'
        ]
    },
)
