# -*- coding: utf-8 -*-
#
# This file is part of Inspire.
# Copyright (C) 2017 CERN.
#
# Inspire is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Inspire is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Inspire; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Project to set all the configurations necessary for the json-merger"""

from __future__ import absolute_import, division, print_function

from setuptools import find_packages, setup

readme = open('README.rst').read()
history = open('CHANGES.rst').read()

tests_require = [
    'coverage>=4.0',
    'decorator',
    'mock~=2.0,>=2.0.0',
    'pydocstyle>=1.0.0',
    'pytest-cache>=1.0',
    'pytest-cov>=1.8.0',
    'pytest-pep8>=1.0.6',
    'pytest>=2.8.0',
]

extras_require = {
    'docs': [
        'Sphinx>=1.5.1',
    ],
    'tests': tests_require,
}

extras_require['all'] = []
for reqs in extras_require.values():
    extras_require['all'].extend(reqs)

setup_requires = [
    'autosemver',
    'pytest-runner>=2.6.2',
]

install_requires = [
    'editdistance>=0.3.1',
    'inspire-utils>=0.0.10',
    'isort>=4.2.2',
    'json-merger~=0.3,>=0.3.2',
    'munkres>=1.0.7',
    'Unidecode>=0.4.19',
    'inspire-schemas~=51.0,>=51.0.0',
]

packages = find_packages()


setup(
    name='inspire-json-merger',
    description=__doc__,
    long_description=readme + '\n\n' + history,
    keywords='Inspire TODO',
    license='GPLv2',
    author='CERN',
    author_email='admin@inspirehep.net',
    url='https://github.com/inspirehep/inspire-json-merger',
    packages=packages,
    autosemver=True,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Development Status :: 1 - Planning',
    ],
)
