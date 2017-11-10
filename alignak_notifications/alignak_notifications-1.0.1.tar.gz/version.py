#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2017:
#   Frederic Mohier, frederic.mohier@alignak.net
#   David Durieux. david.durieux@alignak.net
#

"""
    Alignak - Checks pack for mail, slack,... notifications
"""
# Package name
__pkg_name__ = u"alignak_notifications"

# Checks types for PyPI keywords
# Used for:
# - PyPI keywords
# - directory where to store files in the Alignak configuration (eg. arbiter/packs/checks_type)
__checks_type__ = u"notifications"

# Application manifest
__version__ = u"1.0.1"
__author__ = u"Frédéric MOHIER"
__author_email__ = u"frederic.mohier@alignak.net"
__copyright__ = u"(c) 2015-2017 - %s" % __author__
__license__ = u"GNU Affero General Public License, version 3"
__git_url__ = u"https://github.com/Alignak-monitoring-contrib/alignak-checks-wmi"
__doc_url__ = u"http://alignak-doc.readthedocs.io/en/latest"
__description__ = u"Alignak notifications script pack"

__classifiers__ = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
    'Natural Language :: English',
    'Programming Language :: Python',
    'Topic :: System :: Monitoring',
    'Topic :: System :: Systems Administration'
]
