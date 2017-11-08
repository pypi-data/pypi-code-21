# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Invenio module adding invenio-files-rest integration to invenio-workflows.
"""

from setuptools import find_packages, setup

README = open('README.rst').read()

TESTS_REQUIRE = [
    'check-manifest>=0.25',
    'coverage>=4.0',
    'isort>=4.2.2',
    'pydocstyle>=1.0.0',
    'pytest-cache>=1.0',
    'pytest-cov>=1.8.0',
    'pytest-pep8>=1.0.6',
    'pytest>=2.8.0',
]

EXTRAS_REQUIRE = {
    'docs': [
        'Sphinx>=1.4.2',
    ],
    'tests': TESTS_REQUIRE,
}

EXTRAS_REQUIRE['all'] = []
for reqs in EXTRAS_REQUIRE.values():
    EXTRAS_REQUIRE['all'].extend(reqs)

SETUP_REQUIRES = [
    'autosemver~=0.2,>=0.2',
    'pytest-runner>=2.6.2',
]

INSTALL_REQUIRES = [
    'autosemver~=0.2,>=0.2',
    'pytest-runner>=2.6.2',
    'invenio-db[versioning]>=1.0.0a9',
    'invenio-files-rest>=1.0.0a3',
    'invenio-records-files>=1.0.0a5',
    'invenio-workflows~=7.0',
]

URL = 'https://github.com/inspirehep/invenio-workflows-files'


setup(
    name='invenio-workflows-files',
    description=__doc__,
    long_description=README,
    keywords='invenio TODO',
    license='GPLv2',
    author='CERN',
    author_email='admin@inspirehep.net',
    url=URL,
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'invenio_base.api_apps': [
            'invenio_workflows_files '
            '= invenio_workflows_files:InvenioWorkflowsFiles',
        ],
        'invenio_base.apps': [
            'invenio_workflows_files '
            '= invenio_workflows_files:InvenioWorkflowsFiles',
        ],
        'invenio_i18n.translations': [
            'messages = invenio_workflows_files',
        ],
        'invenio_db.models': [
            'invenio_workflows_files = invenio_workflows_files.models'
        ],
    },
    extras_require=EXTRAS_REQUIRE,
    install_requires=INSTALL_REQUIRES,
    setup_requires=SETUP_REQUIRES,
    tests_require=TESTS_REQUIRE,
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
        'Programming Language :: Python :: 3.5',
        'Development Status :: 1 - Planning',
    ],
    autosemver={
        'bugtracker_url': URL + '/issues/',
    }
)
