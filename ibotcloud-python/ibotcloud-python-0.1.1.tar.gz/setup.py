#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
setuptools script
"""

import os.path
import sys

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

PACKAGE_NAME = 'ibotcloud-python'
PY_MAJOR_MINOR = '{0[0]}.{0[1]}'.format(sys.version_info)


def read(filename):
    """read text file
    """
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        return f.read()


INSTALL_REQUIRES = [
    'requests',
]

if PY_MAJOR_MINOR < '3.4':
    INSTALL_REQUIRES.append('enum34')

EXTRAS_REQUIRE = {
    'develop': ['setuptools', 'wheel', 'twine'],
    'docs': ['Sphinx', 'sphinx-autobuild'],
}

setup(
    name=PACKAGE_NAME,
    namespace_packages=[],
    packages=find_packages('src', exclude=['tests', 'docs']),
    package_dir={'': 'src'},  # tell distutils packages are under src
    url='https://github.org/',
    author='liu xue yan',
    author_email='liu_xue_yan@foxmail.com',
    description='xiaoi iBotCloud WebAPI Python SDK',
    long_description=read('README.rst'),
    # use setuptools_scm
    use_scm_version=True,
    setup_requires=['setuptools_scm', 'setuptools_scm_git_archive'],
    # Requires-Python version.
    python_requires='>=2.7',
    # Dependencies Declarations
    install_requires=INSTALL_REQUIRES,
    # List additional groups of dependencies here (e.g. development dependencies).
    extras_require=EXTRAS_REQUIRE,
    # Included data files
    package_data={},
)
