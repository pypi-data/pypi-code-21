#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Django subcommand
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages


install_requires = ['django']
extras_require = {}
extras_require['test'] = [
    "pytest",
    "pytest-mock",
    "pytest-django",
    "pytest-coverage",
    "coverage",
    "codecov",
    "flake8"]

setup(
    name='dj.subcommand',
    version='0.0.3',
    description='Django subcommand',
    long_description='Django subcommand',
    url='https://github.com/phlax/dj.subcommand',
    author='Ryan Northey',
    author_email='ryan@synca.io',
    license='GPL3',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        ('License :: OSI Approved :: '
         'GNU General Public License v3 or later (GPLv3+)'),
        'Programming Language :: Python :: 2.7',
    ],
    keywords='django subcommand',
    install_requires=install_requires,
    extras_require=extras_require,
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    namespace_packages=['dj'],
    include_package_data=True)
