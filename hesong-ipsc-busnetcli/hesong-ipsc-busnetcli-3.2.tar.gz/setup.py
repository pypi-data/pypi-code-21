#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
setuptools script
"""

from __future__ import with_statement

import io
import os.path
import sys

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

PY_MAJOR_MINOR = '{0[0]}.{0[1]}'.format(sys.version_info)


def read(*names, **kwargs):
    """
    read out a text file
    """
    with io.open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ) as stream:
        return stream.read()


INSTALL_REQUIRES = []
if PY_MAJOR_MINOR < '3.4':
    INSTALL_REQUIRES.append('enum34')
elif PY_MAJOR_MINOR < '3.2':
    INSTALL_REQUIRES.append('futures')

setup(
    name='hesong-ipsc-busnetcli',
    namespace_packages=['hesong', 'hesong.ipsc'],

    description='Python wrapper for Hesong IPSC CTI Service data bus client',
    long_description=read('README.rst'),

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages('src', exclude=['tests', 'docs']),
    package_dir={'': 'src'},  # tell distutils packages are under src
    # The project's main homepage.
    url='https://bitbucket.org/hesong-opensource/ipsc-bus-client-python',

    # Author details
    author='Liu Xue Yan',
    author_email='liu_xue_yan@foxmail.com',

    # Choose your license
    license='MIT',

    # requirements files see:
    # https://packaging.python.org/en/latest/technical.html#install-requires-vs-requirements-files
    python_requires='>=2.7,!=3.0.*,!=3.1.*',
    # use setuptools_scm
    use_scm_version={
        # guess-next-dev:	automatically guesses the next development version (default)
        # post-release:	generates post release versions (adds postN)
        'version_scheme': 'guess-next-dev',
        'write_to': 'src/hesong/ipsc/busnetcli/_scm_version.py',
    },
    setup_requires=['setuptools_scm', 'setuptools_scm_git_archive'],

    install_requires=INSTALL_REQUIRES,
    extras_require={
        'develop': [
            'setuptools',
            'wheel',
            'twine',
            'Sphinx',
            'recommonmark',
            'sphinx-rtd-theme',
            'sphinx-autobuild',
            'sphinx-pypi-upload',
            'coverage'
        ],
        'test': ['coverage']
    },
    # Included data files
    package_data={
        '': ['data/library/*/*/*'],
    },

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        # 'Topic :: Software Development :: Client',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
