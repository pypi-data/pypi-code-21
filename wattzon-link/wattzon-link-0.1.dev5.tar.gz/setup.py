# -*- coding: utf-8 -*-
from setuptools import setup


setup(
    name='wattzon-link',
    packages=['link'],
    version='0.1.dev5',
    description='WattzOn Link API client',
    url='https://github.com/WattzOn/link-python-client',
    keywords='wattzon link',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3'
    ],
    install_requires=['requests'],
    python_requires='>=3'
)

