#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='trollius-fixers',
    version='0.1',
    packages=find_packages(),
    scripts=['scripts/trollius2asyncio'],
    author='Bruce Merry',
    description='Convert trollius code to asyncio',
    long_description='''
        A tool based on lib2to3 for converting code using trollius to use
        asyncio. After installation, run *trollius2asyncio*. It works in the
        same way as 2to3.
        ''',
    license='PSF',
    keywords='2to3 asyncio trollius',
    url='https://github.com/bmerry/trollius_fixers',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Python Software Foundation License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: System :: Networking'
    ]
)
