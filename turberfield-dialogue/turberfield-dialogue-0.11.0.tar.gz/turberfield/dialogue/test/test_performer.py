#!/usr/bin/env python3
# encoding: UTF-8

# This file is part of turberfield.
#
# Turberfield is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Turberfield is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with turberfield.  If not, see <http://www.gnu.org/licenses/>.

import copy
import unittest

from turberfield.utils.misc import group_by_type

from turberfield.dialogue.performer import Performer
from turberfield.dialogue.sequences.battle.logic import ensemble, folder


class TestPerformer(unittest.TestCase):

    @classmethod
    def setUp(self):
        self.ensemble = ensemble()
        self.schedule = [copy.deepcopy(folder)]
        self.characters = {
            k.__name__: v for k, v in group_by_type(self.ensemble).items()
        }

    def test_stopped(self):
        performer = Performer(self.schedule, self.ensemble)
        self.assertFalse(performer.stopped)

    def test_play(self):
        performer = Performer(self.schedule, self.ensemble)
        self.assertEqual(10, len(list(performer.run())))
        self.assertEqual(1, len(performer.shots))
        self.assertEqual("action", performer.shots[-1].name)

    def test_run(self):
        performer = Performer(self.schedule, self.ensemble)
        while not performer.stopped:
            list(performer.run())
