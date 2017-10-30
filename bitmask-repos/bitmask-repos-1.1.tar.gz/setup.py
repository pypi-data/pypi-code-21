#!/usr/bin/env python

from setuptools import setup

setup(
    name='bitmask-repos',
    version='1.1',
    description='setup bitmask debian repositories',
    author='Kali Kaneko',
    author_email='kali@leap.se',
    url='https://bitmask.net',
    py_modules=['bitmask_repos'],
    entry_points={
        'console_scripts': ['bitmask-repos=bitmask_repos:main']}
)
