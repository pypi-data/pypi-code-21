# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2017 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Setup script for Tailbone
"""

from __future__ import unicode_literals, absolute_import

import os.path
from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))
exec(open(os.path.join(here, 'tailbone', '_version.py')).read())
README = open(os.path.join(here, 'README.rst')).read()


requires = [
    #
    # Version numbers within comments below have specific meanings.
    # Basically the 'low' value is a "soft low," and 'high' a "soft high."
    # In other words:
    #
    # If either a 'low' or 'high' value exists, the primary point to be
    # made about the value is that it represents the most current (stable)
    # version available for the package (assuming typical public access
    # methods) whenever this project was started and/or documented.
    # Therefore:
    #
    # If a 'low' version is present, you should know that attempts to use
    # versions of the package significantly older than the 'low' version
    # may not yield happy results.  (A "hard" high limit may or may not be
    # indicated by a true version requirement.)
    #
    # Similarly, if a 'high' version is present, and especially if this
    # project has laid dormant for a while, you may need to refactor a bit
    # when attempting to support a more recent version of the package.  (A
    # "hard" low limit should be indicated by a true version requirement
    # when a 'high' version is present.)
    #
    # In any case, developers and other users are encouraged to play
    # outside the lines with regard to these soft limits.  If bugs are
    # encountered then they should be filed as such.
    #
    # package                           # low                   high

    # For now, let's restrict FormEncode to 1.2 since the 1.3 release
    # introduces some deprecation warnings.  Once we're running 1.2 everywhere
    # in production, we can start looking at adding 1.3 support.
    # TODO: Remove this restriction.
    'FormEncode<=1.2.99',               # 1.2.4                 1.2.6

    # FormAlchemy 1.5 supports Python 3 but is being a little aggressive about
    # it, for our needs...We'll have to stick with 1.4 for now.
    u'FormAlchemy<=1.4.99',             #                       1.4.3

    # TODO: Pyramid 1.9 looks like it breaks us..? playing it safe for now..
    'pyramid<1.9',                      # 1.3b2                 1.8.3

    # apparently 2.0 removes the retry support, in which case we then need
    # pyramid_retry .. but that requires pyramid 1.9 ...
    'pyramid_tm<2.0',                   # 0.3                   1.1.1

    'ColanderAlchemy',                  # 0.3.3
    'deform',                           # 2.0.4
    'humanize',                         # 0.5.1
    'Mako',                             # 0.6.2
    'openpyxl',                         # 2.4.7
    'paginate',                         # 0.5.6
    'paginate_sqlalchemy',              # 0.2.0
    'pyramid_beaker>=0.6',              #                       0.6.1
    'pyramid_debugtoolbar',             # 1.0
    'pyramid_deform',                   # 0.2
    'pyramid_exclog',                   # 0.6
    'pyramid_mako',                     # 1.0.2
    'pyramid_simpleform',               # 0.6.1
    'rattail[db,auth,bouncer]',         # 0.5.0
    'six',                              # 1.10.0
    'transaction',                      # 1.2.0
    'waitress',                         # 0.8.1
    'WebHelpers2',                      # 2.0
    'webhelpers2_grid',                 # 0.1
    'WTForms',                          # 2.1
    'zope.sqlalchemy',                  # 0.7
]


extras = {

    'docs': [
        #
        # package                       # low                   high

        'Sphinx',                       # 1.2
        ],

    'tests': [
        #
        # package                       # low                   high

        'coverage',                     # 3.6
        'fixture',                      # 1.5
        'mock',                         # 1.0.1
        'nose',                         # 1.3.0
        ],
    }


setup(
    name = "Tailbone",
    version = __version__,
    author = "Lance Edgar",
    author_email = "lance@edbob.org",
    url = "http://rattailproject.org/",
    license = "GNU GPL v3",
    description = "Backoffice Web Application for Rattail",
    long_description = README,

    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Pyramid',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Office/Business',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],

    install_requires = requires,
    extras_require = extras,
    tests_require = ['Tailbone[tests]'],
    test_suite = 'nose.collector',

    packages = find_packages(exclude=['tests.*', 'tests']),
    include_package_data = True,
    zip_safe = False,

    entry_points = {

        'paste.app_factory': [
            'main = tailbone.app:main',
        ],

        'rattail.config.extensions': [
            'tailbone = tailbone.config:ConfigExtension',
        ],

        'pyramid.scaffold': [
            'rattail = tailbone.scaffolds:RattailTemplate',
        ],
    },
)
