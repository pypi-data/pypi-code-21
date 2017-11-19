#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
from setuptools import setup, find_packages


setup(
    name='ccpc',
    version='0.0.2',
    description='Chaotic Cable Pulling Chimp',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Intended Audience :: System Administrators',
        'Topic :: System :: Systems Administration',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS'
    ],
    keywords='ccpc open shift monkey chaos async OpenShift pod origin',
    url='https://github.com/panagiks/CCPC',
    download_url='https://github.com/panagiks/CCPC/archive/0.0.2.tar.gz',
    author='panagiks',
    license='MIT',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    namespace_packages=['ccpc'],
    install_requires=[
        'aiohttp',
        'click',
    ],
    entry_points={
        'console_scripts': [
            'ccpc=ccpc.chimp:main'
        ]
    }
)
