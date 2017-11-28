#!/usr/bin/env python
import os
import re
from setuptools import setup, find_packages

setup(
    name='kraem',
    author='Bjarne Oeverli',
    version='0.0.2',
    url='https://github.com/bjarneo/kraem',
    description='Image compression and manipulation CLI with cloud storage upload',
    long_description='https://github.com/bjarneo/kraem',
    packages=find_packages('.'),
    package_data={'kraem': ['bin/darwin/cjpeg', 'bin/linux/cjpeg']},
    keywords='image-processing images compression compress mozjpeg gcs gcp gcp-storage',
    include_package_data=True,
    install_requires=[
        'progressbar2==3.34.3',
        'google-cloud-storage==1.6.0',
    ],
    entry_points={
        'console_scripts': [
            'kraem=kraem.cli:main'
        ]
    },
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python',
    ]
)
