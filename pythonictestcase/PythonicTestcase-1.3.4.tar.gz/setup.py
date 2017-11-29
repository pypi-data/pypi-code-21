#!/usr/bin/env python

import os

from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name = 'PythonicTestcase',
    version = '1.3.4',
    description = 'standalone pythonic assertions',
    long_description=(read('Changelog.txt')),

    author='Felix Schwarz',
    author_email='felix.schwarz@oss.schwarz.eu',
    license='MIT',
    url='https://bitbucket.org/felixschwarz/pythonic-testcase/',

    py_modules=['pythonic_testcase'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

)
