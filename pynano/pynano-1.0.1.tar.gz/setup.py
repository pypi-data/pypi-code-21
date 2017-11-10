"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

import sys
from codecs import open  # To use a consistent encoding
from os import path
from setuptools import find_packages, setup  # Prefer setuptools over distutils

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# Our package dependencies
deps = [
    'requests>=2.9.1',
    'xmltodict>=0.9.2',
]
if sys.version_info < (3, 0, 0):
    # The future package is a compatibility layer between our Py3 code and Py2
    deps += ['future>=0.15.2']

setup(
    name='pynano',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='1.0.1',

    description='A simple Python library for the NaNoWriMo API',
    long_description=long_description,

    # The project's main homepage.
    url='https://pynano.readthedocs.org/',

    # Author details
    author='Travis Veazey',
    author_email='travisvz@gmail.com',

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',

        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    # What does your project relate to?
    keywords='nanowrimo wordcount api',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=deps,

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
            'test': [
                # Some of these don't work from tests_require for some reason;
                # putting all of them here for consistency.
                'coverage>=4.0.3',
                'docutils>=0.12',
                'flake8>=2.5.1',
                'flake8-import-order>=0.6.1',
                'pep8-naming>=0.3.3',
                'responses>=0.5.0',
                ]
    },

    # Integrate `setup.py test` with pytest
    setup_requires=[
            'pytest-runner',
            ],
    tests_require=[
            'pytest',
            ],

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    package_data={
    },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    data_files=[],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
    },
)
