#!/usr/bin/env python
# coding: utf-8

from setuptools import setup

setup(
    name='jujube',
    version='0.0.1',
    author='yuejing08',
    author_email='568623642@qq.com',
	url = 'https://github.com/yuejing08/hello',
    description="我了个去",
    packages=['jujube'],
    install_requires=[],
    entry_points={
        'console_scripts': [
            'jujube=jujube_pill:jujube',
            'pill=jujube_pill:pill'
        ]
    }
)
