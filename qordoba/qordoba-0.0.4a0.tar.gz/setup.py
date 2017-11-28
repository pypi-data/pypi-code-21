#!/usr/bin/env python
# -*- coding: utf-8 -*-
from codecs import open
from setuptools import setup

#  Example version releases:
# 1.2.0.dev1  # Development release
# 1.2.0a1     # Alpha Release
# 1.2.0b1     # Beta Release
# 1.2.0rc1    # Release Candidate
# 1.2.0       # Final Release
# 1.2.0.post1 # Post Release
# 15.10       # Date based release
# 23          # Serial release

__version__ = '0.0.4a0'

packages = [
    'qordoba',
    'qordoba.commands'
]


def get_requirements(filename):
    with open(filename, 'r', encoding='UTF-8') as f:
        return f.read()

setup(
    name="qordoba",
    author="Qordoba",
    author_email="hello@qordoba.com",
    version=__version__,
    entry_points={'console_scripts': ['qor=qordoba.cli:main', 'qordoba=qordoba.cli:main']},
    description="Qordoba command line tool",
    url="https://www.qordoba.com",
    dependency_links=[],
    setup_requires=[],
    install_requires=get_requirements('requirements.txt').splitlines(),
    data_files=[],
    test_suite="tests",
    zip_safe=False,
    packages=packages,
    include_package_data=True,
    package_data={
         # 'qordoba': ['resources/*'],
    },
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)