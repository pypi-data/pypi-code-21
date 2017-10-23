#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='giusas',
    version='2017.10.23',
    description='GISAXS and GIWAXS calculator',
    author='Vadim Dyadkin',
    author_email='dyadkin@gmail.com',
    url='https://soft.snbl.eu/giusas.html',
    license='GPLv3',
    install_requires=[
        'numpy>=1.9',
        'scipy>=0.10.0',
        'pyqtgraph>=0.10.0',
        'cryio>=2016.10.1',
        'decor>=2016.12.1',
    ],
    entry_points={
        'gui_scripts': [
            'giusas=giusas.__init__:main',
        ],
    },
    packages=[
        'giusas',
        'giusas.gui',
        'giusas.gui.ui',
    ],
)
