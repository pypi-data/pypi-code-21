#!/usr/bin/python
# -*- coding: utf-8 -*-

from setuptools import setup


setup(
    name='auxygen',
    version='2017.10.25',
    packages=[
        'auxygen',
        'auxygen.devices',
        'auxygen.gui',
        'auxygen.gui.ui',
        'auxygen.scripo',
    ],
    url='https://hg.3lp.cx/auxygen',
    license='GPL',
    author='Vadim Dyadkin',
    author_email='diadkin@esrf.fr',
    description='Drivers and scripting for Pylatus auxiliary equipment',
    entry_points={
        'gui_scripts': [
            'blower=auxygen.executables:blower',
            'cryostream=auxygen.executables:cryostream',
            'lakeshore=auxygen.executables:lakeshore',
        ],
    },
    install_requires=[
        'pyqtgraph',
        'pyserial',
        'aspic',
    ]
)
