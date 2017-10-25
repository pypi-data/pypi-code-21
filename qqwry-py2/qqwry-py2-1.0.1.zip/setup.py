#!/usr/bin/env python
# coding=utf-8
import os
from distutils.core import setup

def read_file(path):
    with open(os.path.join(os.path.dirname(__file__), path)) as fp:
        return fp.read().decode('utf-8-sig')

setup(
    name='qqwry-py2',
    version='1.0.1',
    description='Lookup location of IP in qqwry.dat, for Python 2.7',
    long_description=read_file('qqwry.txt'),
    author='animalize',
    author_email='animalize81@hotmail.com',
    url='https://github.com/animalize/qqwry-python3',
    license='BSD',
    keywords = 'qqwry cz88 纯真 ip归属地',
    platforms=['any'],
    packages=['qqwry'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2 :: Only',
        'Topic :: Utilities'
    ]
)
