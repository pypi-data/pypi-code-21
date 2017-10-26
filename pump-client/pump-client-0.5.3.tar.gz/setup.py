# -*- coding: utf-8 -*-

import re

from setuptools import setup, find_packages

with open('pypump/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

setup(
    name='pump-client',
    version=version,
    packages=find_packages(exclude=['docs', 'tests']),
    url='https://bitbucket.org/yimian/pump-client',
    author='Yangliang Li',
    author_email='liyangliang@yimian.com.cn',
    description='Python SDK for pump APIs',
    zip_safe=False,
    install_requires=[
        'marshmallow>=2.9.0',
        'requests>=2.10.0',
        'pandas',
        'python-dateutil',
        'six',
        'tornado'
    ]
)
