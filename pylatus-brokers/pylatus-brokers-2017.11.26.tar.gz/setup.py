#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import setup

setup(
    name='pylatus-brokers',
    version='2017.11.26',
    packages=[
        'pylatus_brokers',
    ],
    url='https://hg.3lp.cx/pylatus-brokers',
    license='GPLv3',
    author='Vadim Dyadkin',
    author_email='diadkin@esrf.fr',
    description='Data brokers for Pylatus',
    install_requires=[
        'aioamqp',
        'cryio',
    ],
    entry_points={
        'console_scripts': [
            'dcu_broker=pylatus_brokers.dcu_broker:main',
            'ppu_broker=pylatus_brokers.ppu_broker:main',
        ],
    }
)
