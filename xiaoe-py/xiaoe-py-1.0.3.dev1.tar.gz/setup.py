#!/usr/bin/env python3
from setuptools import setup

setup(
    name='xiaoe-py',
    version='1.0.3.dev1',
    description='python package for xiaoe',
    author='ttm1234',
    author_email='',
    license='MIT',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='xiaoe',
    packages=['xiaoe', 'xiaoe.api', 'xiaoe.post', 'xiaoe.type'],
)
