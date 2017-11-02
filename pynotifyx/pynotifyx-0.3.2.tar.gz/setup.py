#!/usr/bin/env python

# Author: Forest Bond
# This file is in the public domain.


import os
import subprocess
import sys

from setuptools import Extension

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from setuplib import setup


def get_version(release_file):
    try:
        f = open(release_file, 'r')
        try:
            return f.read().strip()
        finally:
            f.close()
    except (IOError, OSError):
        try:
            output = subprocess.check_output(['bzr', 'revno'])
            return 'bzr' + output.strip()
        except Exception:
            pass
    return 'unknown'


version = get_version('release')

setup(
    name='pynotifyx',
    distinfo_module='pynotifyx.distinfo',
    version=version,
    description='Simple Linux inotify bindings',
    author='Joe Isca',
    author_email='joeisca@gmail.com',
    url='https://github.com/joeisca/pynotifyx/',
    packages=['pynotifyx'],
    entry_points={
        "console_scripts": [
            "pynotifyx=pynotifyx:main",
        ]
    },
    ext_modules=[
        Extension(
            'pynotifyx.binding',
            sources=[os.path.join('pynotifyx', 'binding.c')],
        ),
    ],
)
