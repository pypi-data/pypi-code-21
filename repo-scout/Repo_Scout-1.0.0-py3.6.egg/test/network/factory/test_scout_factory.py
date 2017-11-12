"""
Repo Scout
Copyright (C) 2017  JValck - Setarit

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

Setarit - parcks[at]setarit.com
"""
from __future__ import absolute_import

import unittest

from src.network.factory.scout_factory import ScoutFactory


class TestScoutFacotory(unittest.TestCase):
    def test_create_creates_githubscout_if_provider_equals_github(self):
        result = ScoutFactory.create("GitHub");
        self.assertEqual("GitHubScout", result.__class__.__name__)

    def test_create_raises_NameError_if_unknown_provider(self):
        with self.assertRaises(NameError):
            ScoutFactory.create("unknown")