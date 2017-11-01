#!/usr/bin/env python

import json
from io import open
from setuptools import setup
from pip.req import parse_requirements
from pip.download import PipSession

with open('README.md', encoding='utf-8') as readme_file:
    readme = readme_file.read()

# release.json contains name, description, version, etc
with open('pptgen/release.json', encoding='utf-8') as handle:
    release_args = json.load(handle)

# Add a matching line in MANIFEST.in
pptgen_files = [
    'colors.json',
    'fonts.json',
    'release.json'
]

setup(
    long_description=readme,
    packages=[
        'pptgen',
    ],
    # Read: http://stackoverflow.com/a/2969087/100904
    # package_data includes data files for binary & source distributions
    # include_package_data is only for source distributions, uses MANIFEST.in
    package_data={
        'pptgen': pptgen_files,
    },
    include_package_data=True,
    install_requires=[
        str(entry.req)          # noqa
        for entry in parse_requirements('requirements.txt', session=PipSession())
        if entry.match_markers()
    ],
    entry_points={
        'console_scripts': ['pptgen = pptgen:commandline']
    },
    test_suite='tests',
    tests_require=['PyYAML'],
    **release_args
)
