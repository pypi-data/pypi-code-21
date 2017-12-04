#!/usr/bin/env python

from setuptools import setup, find_packages

try:
    import pypandoc

    long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    long_description = ''

setup(
    name='tdx_wrapper',
    version='0.48',
    description='A Python wrapper of pytdx',
    long_description=long_description,
    author='Jie Wang',
    author_email='790930856@qq.com',
    url='https://github.com/JaysonAlbert/tdx',
    packages=find_packages(),
    install_requires=[
        'pytdx',
        'toolz'
    ],

    package_data = {'tdx': ['data/*','data/blocknew/*']},

)
