#!/usr/bin/env python
# -*- coding: utf-8 -*-
from codecs import open
from setuptools import setup, find_packages

#  Example version releases:
# 1.2.0.dev1  # Development release
# 1.2.0a1     # Alpha Release
# 1.2.0b1     # Beta Release
# 1.2.0rc1    # Release Candidate
# 1.2.0       # Final Release
# 1.2.0.post1 # Post Release
# 15.10       # Date based release
# 23          # Serial release

# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

def get_requirements(filename):
    with open(filename, 'r', encoding='UTF-8') as f:
        return f.read()

__version__ = '0.0.4a1'

# packages = [
#     'qordoba',
#     'qordoba.commands',
#     'qordoba.resources'
# ]

setup(
    name="qordoba",
    author="Qordoba",
    author_email="hello@qordoba.com",
    version=__version__,
    packages=find_packages(exclude=['tests']),
    license="Qordoba",
    entry_points={'console_scripts': ['qor=qordoba.cli:main', 'qordoba=qordoba.cli:main']},
    description="Qordoba command line tool",
    long_description=long_description,
    url="https://github.com/Qordobacode/qordoba-cli",
    dependency_links=[],
    setup_requires=[],
    install_requires=get_requirements('requirements.txt').splitlines(),
    data_files=[],
    test_suite="tests",
    zip_safe=False,
    include_package_data=True,
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        'qordoba': ['resources/*.yml', 'resources/*.csv', 'resources/*.csv', 'string-extractor/*.scala', 'string-extractor/*.sh'],
    },
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='Localization - because the world is diverse',
)
