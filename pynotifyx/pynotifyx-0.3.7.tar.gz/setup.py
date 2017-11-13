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
    description='pynotifyx is a simple Python binding to the Linux inotify file system event monitoring API.',
    long_description='''
pynotifyx is a simple Python binding to the Linux inotify file system event
monitoring API.

Documentation is provided in the module.  To get help, start an interactive
Python session and type:

>>> import pynotifyx
>>> help(pynotifyx)

You can also test out pynotifyx easily.  The following command will print events
for /tmp:

  python -m pynotifyx /tmp

Tests can be run via setup.py:

  ./setup.py test

Note that the module must be built and installed for tests to run correctly.
In the future, this requirement will be lifted.

Visit https://github.com/joeisca/pynotifyx for more information.''',

    author='Joe Isca',
    author_email='joeisca@gmail.com',
    url='https://github.com/joeisca/pynotifyx/',
    packages=['pynotifyx'],
    entry_points={
        "console_scripts": [
            "pynotifyx=pynotifyx.__init__:main",
        ]
    },
    ext_modules=[
        Extension(
            'pynotifyx.binding',
            sources=[os.path.join('pynotifyx', 'binding.c')],
        ),
    ],
)
