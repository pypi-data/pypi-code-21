#!/usr/bin/env python3

from codecs import open
from os import path

from setuptools import setup

CURRENT_PATH = path.abspath(path.dirname(__file__))

with open(path.join(CURRENT_PATH, 'README.rst'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

setup(
    name='jutge_cli',
    version='2.1.7',

    description='CLI to automate tests for jutge.org problems',
    long_description=LONG_DESCRIPTION,

    url='http://github.com/Leixb/jutge_cli',

    author='Aleix Boné (Leix_b)',
    author_email='abone9999@gmail.com',

    license='GPL3',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Education',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Education',
        ],

    keywords='jutge jutge.org jutge_cli',

    packages=['jutge_cli', 'jutge_cli.commands'],

    install_requires=[
        'argparse',
        'beautifulsoup4',
        'pypandoc',
        'pyyaml',
        'requests',
        ],

    extras_require={
        'lxml' : ['lxml']
        },

    entry_points={
        'console_scripts': ['jutge=jutge_cli.jutge:main'],
        },

    zip_safe=True
)
