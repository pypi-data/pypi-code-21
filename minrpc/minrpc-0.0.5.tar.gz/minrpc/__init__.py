# encoding: utf-8
from __future__ import unicode_literals

__title__ = 'minrpc'
__version__ = '0.0.5'

__summary__ = 'Minimalistic RPC utility (DO NOT USE!)'
__uri__ = 'https://github.com/hibtc/minrpc'

__author__ = 'Thomas Gläßle'
__author_email__ = 't_glaessle@gmx.de'

__support__ = __author_email__

__license__ = 'GPLv3+'
__copyright__ = 'Copyright 2016 HIT Betriebs GmbH'

__credits__ = """
Author and current maintainer:

    - Thomas Gläßle <t_glaessle@gmx.de>
"""

__classifiers__ = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Topic :: Software Development :: Libraries',
]


def get_copyright_notice():
    from pkg_resources import resource_string
    return resource_string('minrpc', 'COPYING.txt')
