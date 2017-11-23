#!/usr/bin/env python3
from setuptools import setup


setup(
    name='sq',
    version='1.0alpha1',
    description='Sovereign Quantum Framework Application Library',
    author='Cochise Ruhulessin',
    author_email='cochiseruhulessin@gmail.com',
    url='https://www.wizardsofindustry.net',
    project_name='Inversion of Control',
    install_requires=[
        'flask',
        'marshmallow',
        'pytz'
    ],
    packages=[
        'sq',
        'sq.datastructures',
        'sq.ddd',
        'sq.interfaces',
        'sq.interfaces.wsgi',
        'sq.schema',
    ]
)
