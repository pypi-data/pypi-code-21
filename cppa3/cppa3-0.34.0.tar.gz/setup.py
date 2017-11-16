#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Setup file for cppa3.

"""

import sys
from setuptools import setup


import versioneer


with open('requirements.txt') as f:
    required_packages = f.read().splitlines()

def setup_package():
    needs_sphinx = {'build_sphinx', 'upload_docs'}.intersection(sys.argv)
    sphinx = ['sphinx'] if needs_sphinx else []
    setup(setup_requires=['six', 'pyscaffold>=2.5a0,<2.6a0'] + sphinx,
          use_pyscaffold=True,
          install_requires=required_packages,
          exclude_package_data={'':['tests']},
          version=versioneer.get_version(),
          cmdclass=versioneer.get_cmdclass())

if __name__ == "__main__":
    setup_package()
