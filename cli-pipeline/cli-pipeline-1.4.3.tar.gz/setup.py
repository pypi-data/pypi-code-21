#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""setup.py: setuptools control."""

import warnings
import re
from setuptools import setup, find_packages
import urllib3
urllib3.disable_warnings()

import sys
with warnings.catch_warnings():
    if not sys.version_info[0] == 3:
    #    sys.exit("\n \
        print('*********************************************************************') 
        print('* The CLI is primarly tested for Python 3 but Python 2 should work. *')
        print('* If you see issues with Python 2, Please email help@pipeline.ai    *')
        print('*********************************************************************')

with warnings.catch_warnings():
    version = re.search(
            '^__version__\s*=\s*"(.*)"',
            open('cli_pipeline/__init__.py').read(),
            re.M
        ).group(1)


# Get the long description from the relevant file
with warnings.catch_warnings():
    with open('README.rst') as f:
        long_description = f.read()

with warnings.catch_warnings():
    with open('requirements.txt') as f:
        requirements = [line.rstrip() for line in f.readlines()]

with warnings.catch_warnings():
    setup(
        include_package_data=True,
        name = "cli-pipeline",
        packages = ["cli_pipeline"],
        entry_points = {
            "console_scripts": ['pipeline = cli_pipeline.__init__:main']
        },
        version = version,
        description = "PipelineAI CLI",
        long_description = "%s\n\nRequirements:\n%s" % (long_description, requirements),
        author = "Chris Fregly",
        author_email = "github@pipeline.ai",
        url = "https://github.com/PipelineAI/",
        install_requires=requirements,
        dependency_links=[],
        package=find_packages(exclude=['concurrent', 'concurrent.*', '*.concurrent.*']),
    )
