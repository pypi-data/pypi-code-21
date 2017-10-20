#!/usr/bin/env python

import os
from setuptools import find_packages, setup

requirements=[
    'Click',
    'requests',
    'progressbar2',
    'termcolor',
    'cookiecutter',
    'colorama',
    'watchdog',
    'mcommons',
    'dnspython'
]

if os.name == 'posix':
    requirements.append('sh')

buildNumber = os.getenv('CIRCLE_BUILD_NUM')

# 52 is replaced by CI.
if buildNumber is None:
    buildNumber = "52"

# 52 wasn't replaced with proper build number (for instance, installation from git)
if buildNumber.startswith("{{BUILD_"):
    buildNumber = "dev"

setup(
    name='papertrail-cli',
    version='1.1.' + buildNumber,
    install_requires=requirements,
    author='Egis Software',
    url='https://github.com/egis/papertrail-python-cli',
    description='Papertrail Command Line Utils',
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "pt = pt.pt:main",
        ]
    }
)
