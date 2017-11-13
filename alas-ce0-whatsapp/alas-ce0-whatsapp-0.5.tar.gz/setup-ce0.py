#!/usr/bin/env python
# coding=utf-8
from __future__ import print_function
from setuptools import setup, find_packages
import yowsup
import platform
import sys

deps = ['python-dateutil', 'argparse', 'python-axolotl>=0.1.39', 'six']

if sys.version_info < (2,7):
    deps += ['importlib']

if platform.system().lower() == "windows":
    deps.append('pyreadline')
else:
    try:
        import readline
    except ImportError:
        deps.append('readline')

setup(
    name='alas-ce0-whatsapp',
    version='0.5',
    url='https://github.com/pypa/alas-ce0-whatsapp',
    license='GPL-3+',
    author='Adonis Cesar Legón Campo',
    tests_require=[],
    install_requires = deps,
    scripts = ['yowsup-cli'],
    #cmdclass={'test': PyTest},
    author_email='alegon@alasxpress.com',
    description='A WhatsApp python library for ALAS-Ce0',
    #long_description=long_description,
    packages= find_packages(),
    include_package_data=True,
    data_files = [('yowsup/common', ['yowsup/common/mime.types'])],
    platforms='any',
    #test_suite='',
    classifiers = [
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        #'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules'
        ],
    #extras_require={
    #    'testing': ['pytest'],
    #}
)
