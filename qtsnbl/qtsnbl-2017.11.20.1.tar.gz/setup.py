#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup


install_requires = [
    'numpy',
    'pyqtgraph',
    'requests',
]
try:
    if '-gentoo' not in os.uname().release:
        install_requires.append('PyQt5')
except AttributeError:  # windows?
    install_requires.append('PyQt5')


setup(
    name='qtsnbl',
    version='2017.11.20.1',
    description='PyQt widgets for SNBL programs',
    author='Vadim Dyadkin',
    author_email='dyadkin@gmail.com',
    url='https://hg.3lp.cx/qtsnbl',
    license='GPLv3',
    install_requires=install_requires,
    packages=[
        'qtsnbl',
    ],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
)
