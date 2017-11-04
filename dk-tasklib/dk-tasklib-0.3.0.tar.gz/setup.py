#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""dk-tasklib - short description
"""
import os
import sys
from setuptools import setup

classifiers = """\
Development Status :: 3 - Alpha
Intended Audience :: Developers
Programming Language :: Python
Programming Language :: Python :: 2
Programming Language :: Python :: 2.7
Topic :: Software Development :: Libraries
"""

version = '0.3.0'
DIRNAME = os.path.dirname(__file__)

needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
pytest_runner = ['pytest-runner'] if needs_pytest else []


setup(
    name='dk-tasklib',
    version=version,
    setup_requires=[] + pytest_runner,
    tests_require=[
        'pytest>=3.2.1'
    ],
    requires=[
        
    ],
    install_requires=[],
    author='Bjorn Pettersen',
    author_email='bp@datakortet.no',
    url='https://github.com/datakortet/dk-tasklib',
    description=__doc__.strip(),
    classifiers=[line for line in classifiers.split('\n') if line],
    long_description=open('README.rst').read(),
    packages=['dktasklib'],
    entry_points={
        'console_scripts': """
            dk-tasklib = dktasklib.entry_points.dktasklibcmd:main
        """
    },
    zip_safe=False,
)
