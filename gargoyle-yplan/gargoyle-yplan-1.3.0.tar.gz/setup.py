#!/usr/bin/env python
from __future__ import absolute_import, division, print_function

import codecs
import os
import re

from setuptools import find_packages, setup


def get_version(filename):
    with codecs.open(filename, 'r', 'utf-8') as fp:
        contents = fp.read()
    return re.search(r"__version__ = ['\"]([^'\"]+)['\"]", contents).group(1)


version = get_version(os.path.join('gargoyle', '__init__.py'))

with codecs.open('README.rst', 'r', encoding='utf-8') as readme_file:
    readme = readme_file.read()

with codecs.open('HISTORY.rst', 'r', encoding='utf-8') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

setup(
    name='gargoyle-yplan',
    version=version,
    author='DISQUS',
    author_email='opensource@disqus.com',
    maintainer='YPlan',
    maintainer_email='adam@yplanapp.com',
    url='https://github.com/YPlan/gargoyle',
    description=(
        'Gargoyle is a platform built on top of Django which allows you to switch functionality of your application '
        'on and off based on conditions.'
    ),
    long_description=readme + '\n\n' + history,
    packages=find_packages(exclude=['tests', 'tests.*']),
    zip_safe=False,
    install_requires=[
        'django-modeldict-yplan>=1.5.0',
        'nexus-yplan>=1.6.0',
        'django-jsonfield>=0.9.2,!=0.9.13,!=1.0.0',
    ],
    extras_require={
        ':python_version=="2.7"': [
            'contextdecorator',
        ]
    },
    license='Apache License 2.0',
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python',
        'Topic :: Software Development'
    ],
)
