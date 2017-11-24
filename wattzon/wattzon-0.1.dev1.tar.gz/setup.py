# -*- coding: utf-8 -*-
from setuptools import setup


setup(
    name='wattzon',
    packages=['wattzon'],
    version='0.1.dev1',
    description='WattzOn API clients',
    url='https://github.com/WattzOn/wattzon-python',
    keywords='wattzon link snapshot',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3'
    ],
    install_requires=['requests'],
    python_requires='>=3'
)

