#!/usr/bin/env python

# Author: Forest Bond
# This file is in the public domain.


import os

from pynotifyx import __version__ as version
from setuplib import setup
from setuptools import Extension


setup(
    name='pynotifyx',
    version='.'.join(map(str, version)),
    description='Simple Linux inotify bindings',
    author='Joe Isca',
    author_email='joeisca@gmail.com',
    url='https://github.com/joeisca/pynotifyx/',
    packages=['pynotifyx'],
    entry_points={
        "console_scripts": [
            "pynotifyx=pynotifyx.__main__:main",
        ]
    },
    ext_modules=[
        Extension(
            'pynotifyx.binding',
            sources=[os.path.join('pynotifyx', 'binding.c')],
        ),
    ],
)
