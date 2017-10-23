#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, Extension

setup(
    name='cryio',
    version='2017.8.23',
    description='Crystallographic IO routines',
    author='Vadim Dyadkin',
    author_email='dyadkin@gmail.com',
    url='https://hg.3lp.cx/cryio',
    license='GPLv3',
    install_requires=[
        'numpy',
        'jinja2',
    ],
    packages=[
        'cryio',
        'cryio.templates',
    ],
    ext_modules=[
        Extension(
            'cryio._cryio', [
                'src/cryiomodule.c',
                'src/agi_bitfield.c',
                'src/byteoffset.c',
                'src/mar345.c',
            ],
            extra_compile_args=['-O3'],
        )
    ],
    include_package_data=True,
)
