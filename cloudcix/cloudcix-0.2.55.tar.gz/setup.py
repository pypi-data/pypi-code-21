#!/usr/bin/env python

from setuptools import setup
import cloudcix

with open('README.txt', 'r') as f:
    readme = f.read()

with open('requirements.txt', 'r') as f:
    requires = f.read().split('\n')

setup(
    name='cloudcix',
    version='0.2.55',
    description='Python bindings and utils for CloudCIX API.',
    long_description=readme,
    author='CloudCIX',
    author_email='support@cloudcix.com',
    url='https://github.com/CloudCIX/cloudcix-python',
    packages=[
        'cloudcix'
    ],
    keywords=['cix', 'cloudcix', 'bindings', 'client'],
    install_requires=requires,
    package_data={'': ['LICENSE', 'README.md']},
    package_dir={'cloudcix': 'cloudcix'},
    include_package_data=True,
    license='Apache 2.0',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ])
