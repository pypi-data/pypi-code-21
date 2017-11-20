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
setup script for rattail-tempmon
"""

from __future__ import unicode_literals, absolute_import

import os
from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))
exec(open(os.path.join(here, 'rattail_tempmon', '_version.py')).read())
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

    'rattail[db]',                      # 0.7.46
    'six',                              # 1.10.0
    'sqlsoup',                          # 0.9.1
]


setup(
    name = "rattail-tempmon",
    version = __version__,
    author = "Lance Edgar",
    author_email = "lance@edbob.org",
    url = "https://rattailproject.org/",
    license = "GNU GPL v3",
    description = "Retail Software Framework - Temperature monitoring add-on",
    long_description = README,

    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Office/Business',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    install_requires = requires,
    packages = find_packages(),
    include_package_data = True,

    entry_points = {
        'rattail.commands': [
            'export-hotcooler = rattail_tempmon.commands:ExportHotCooler',
            'purge-tempmon = rattail_tempmon.commands:PurgeTempmon',
            'tempmon-client = rattail_tempmon.commands:TempmonClient',
            'tempmon-problems = rattail_tempmon.commands:TempmonProblems',
            'tempmon-server = rattail_tempmon.commands:TempmonServer',
        ],
        'rattail.config.extensions': [
            'tempmon = rattail_tempmon.config:TempmonConfigExtension',
        ],
    },
)
