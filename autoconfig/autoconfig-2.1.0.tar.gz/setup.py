#!/usr/bin/env python

# https://hynek.me/articles/testing-packaging

from distutils.core import setup

setup(
    name='autoconfig',
    description='Simple environment, logging, and sys.path setup from a config file',
    version='2.1.0',
    package_dir={'': 'src'},
    packages=['autoconfig'],
    author='Michael Kleehammer',
    author_email='michael@kleehammer.com',
    url='http://gitlab.com/mkleehammer/autoconfig',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development'
    ]
)
