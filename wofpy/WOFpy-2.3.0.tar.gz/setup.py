"""
WOFpy
-------

WOFpy is a python library for serving CUAHSI's WaterOneflow  web services

CUAHSI is the Consortium of Universities for the
Advancement of Hydrologic Science, Inc.

"""
from __future__ import (absolute_import, division, print_function)

import codecs
import os
import re

from setuptools import find_packages, setup

import versioneer


here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    return codecs.open(os.path.join(here, *parts), 'r').read()


# Dependencies.
with open('requirements.txt') as f:
    requirements = f.readlines()
install_requires = [t.strip() for t in requirements]

setup(
    name='WOFpy',
    version=versioneer.get_version(),
    license='BSD',
    author='James Seppi',
    author_email='james.seppi@gmail.com',
    # note: maintainer gets listed as author in PKG-INFO, so leaving
    # this commented out for now
    maintainer='Emilio Mayorga',
    maintainer_email='emiliom@uw.edu',
    description='a python library for serving WaterOneFlow web services',
    long_description=__doc__,
    keywords='cuahsi his wofpy water waterml cuahsi wateroneflow odm2',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=install_requires,
    extras_require={
        'odm1': ['sqlalchemy', 'pyodbc'],
        'odm2': ['sqlalchemy', 'odm2api'],
        'sqlite': ['sqlalchemy'],
        'server': ['uwsgi'],
    },
    tests_require=['suds-jurko', 'requests'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    entry_points=dict(console_scripts=[
        'wofpy_config = wof.wofpy_config:main'
        ]
    ),
    cmdclass=versioneer.get_cmdclass(),
)
