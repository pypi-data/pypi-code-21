#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup


setup(
    name='cryoproxy',
    version='2017.11.1',
    packages=[
        'cryoproxy'
    ],
    url='https://hg.3lp.cx/cryoproxy',
    license='GPL',
    author='Vadim Dyadkin',
    author_email='diadkin@esrf.fr',
    description='Cryostream asynchronous serial port proxy daemon based on asyncio',
    install_requires=[
        'pyserial',
    ],
    entry_points={
        'console_scripts': [
            'cryoproxy=cryoproxy.cryoproxy:main',
        ],
    },
)
