# -*- coding: utf-8 -*-

"""
Asynchronous Connect API Wrapper
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A basic wrapper for the Monstercat Connect API.

:copyright: (c) 2017 GiovanniMCMXCIX
:license: MIT, see LICENSE for more details.
"""

__title__ = 'async_connect'
__author__ = 'GiovanniMCMXCIX'
__license__ = 'MIT'
__copyright__ = 'Copyright 2017 GiovanniMCMXCIX'
__version__ = '0.2.1'

from collections import namedtuple

from . import utils
from .artist import Artist
from .client import Client
from .errors import *
from .playlist import Playlist
from .release import Release
from .track import Track, BrowseEntry

VersionInfo = namedtuple('VersionInfo', 'major minor micro releaselevel serial')

version_info = VersionInfo(major=0, minor=2, micro=1, releaselevel='final', serial=0)
