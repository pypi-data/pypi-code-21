# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.txt'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='gzutils',
    version='0.0.11.dev',
    description='Gizur misc utils',
    long_description=long_description,
    url='https://github.com/gizur/gzutils.py',
    author='Jonas Colmsjö',
    author_email='jonas.colmsjo@gizur.com',
    license='MIT',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    keywords='utils logging cvs dotdict',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
)
