#!/usr/bin/env python

import glob
from setuptools import setup, find_packages

setup(
    name="udoc",
    version="0.0.1",
    url='https://github.com/kislyuk/udoc',
    license='Apache Software License',
    author='Andrey Kislyuk',
    author_email='kislyuk@gmail.com',
    description='Lightweight documentation format processor for Markdown-reStructuredText conversion',
    long_description=open('README.rst').read(),
    install_requires=[
        'docutils',
        'mistune'
    ],
    extras_require={
        ':python_version == "2.7"': ['enum34 >= 1.1.6, < 2']
    },
    packages=find_packages(exclude=['test']),
    scripts=glob.glob('scripts/*'),
    platforms=['MacOS X', 'Posix'],
    zip_safe=False,
    test_suite='test',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
