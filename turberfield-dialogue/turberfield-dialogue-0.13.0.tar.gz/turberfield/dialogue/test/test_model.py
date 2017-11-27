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
import enum
import sys
import textwrap
import unittest

from turberfield.dialogue.directives import Entity
from turberfield.dialogue.types import EnumFactory
from turberfield.dialogue.types import Player
from turberfield.dialogue.model import Model
from turberfield.dialogue.model import SceneScript


class PropertyDirectiveTests(unittest.TestCase):

    personae = [
        Player(name="Prof William Fuzzer Q.A Testfixture"),
        Player(name="Ms Anna Conda"),
        Player(name="A Big Hammer")
    ]

    def test_property_getter(self):
        content = textwrap.dedent("""
            .. entity:: P

            Scene
            ~~~~~

            Shot
            ----

            [P]_

                Hi, I'm |P_FIRSTNAME|.

            .. |P_FIRSTNAME| property:: P.name.firstname
            """)
        script = SceneScript("inline", doc=SceneScript.read(content))
        script.cast(script.select([self.personae[0]]))
        model = script.run()
        shot, line = next(iter(model))
        self.assertEqual("scene", shot.scene)
        self.assertEqual("shot", shot.name)
        self.assertEqual("Hi, I'm  William .", line.text)

    def test_property_getter_fields(self):
        content = textwrap.dedent("""
            .. |VERSION| property:: turberfield.dialogue.__version__

            :copyright: 2017
            :version: |VERSION|

            """)
        script = SceneScript("inline", doc=SceneScript.read(content))
        script.cast(script.select([self.personae[0]]))
        model = script.run()
        metadata = dict(model.metadata)
        self.assertIn("copyright", metadata)
        self.assertIn("version", metadata)
        self.assertEqual(2, metadata["version"].count("."))

    def test_nickname_getter(self):
        content = textwrap.dedent(
            """
            .. entity:: P

            Scene
            ~~~~~

            Shot
            ----

            [P]_

                You can call me |P_NICKNAME|.

            .. |P_NICKNAME| property:: P.nickname
            """)
        script = SceneScript("inline", doc=SceneScript.read(content))
        script.cast(script.select([self.personae[0]]))
        model = script.run()
        shot, line = next(iter(model))
        self.assertEqual("scene", shot.scene)
        self.assertEqual("shot", shot.name)
        self.assertIn(line.text, (
            "You can call me  Fuzzer .",
            "You can call me  Q.A ."))

    def test_property_setter_enum(self):
        content = textwrap.dedent("""
            .. entity:: P

            Scene
            ~~~~~

            Shot
            ----

            .. property:: P.state turberfield.dialogue.test.test_model.SelectTests.Aggression.calm

            """)
        ensemble = copy.deepcopy(PropertyDirectiveTests.personae)
        script = SceneScript("inline", doc=SceneScript.read(content))
        script.cast(script.select([ensemble[0]]))
        model = script.run()
        p = next(l for s, l in model if isinstance(l, Model.Property))
        self.assertEqual("state", p.attr)
        self.assertEqual(str(SelectTests.Aggression.calm), str(p.val))
        setattr(p.object, p.attr, p.val)

    def test_property_setter_integer(self):
        content = textwrap.dedent("""
            .. entity:: P

            Scene
            ~~~~~

            Shot
            ----

            .. property:: P.state 3

            """)
        ensemble = copy.deepcopy(PropertyDirectiveTests.personae)
        script = SceneScript("inline", doc=SceneScript.read(content))
        script.cast(script.select([ensemble[0]]))
        model = script.run()
        p = next(l for s, l in model if isinstance(l, Model.Property))
        self.assertEqual("state", p.attr)
        self.assertEqual(3, p.val)

    def test_property_setter_bad_substitution(self):
        content = textwrap.dedent(
            """
            .. entity:: P

            Scene
            ~~~~~

            Shot
            ----

            .. property:: P.state |S_ID|

            """)
        ensemble = copy.deepcopy(PropertyDirectiveTests.personae)
        script = SceneScript("inline", doc=SceneScript.read(content))
        script.cast(script.select([ensemble[0]]))
        model = script.run()
        p = next(l for s, l in model if isinstance(l, Model.Property))
        self.assertEqual("state", p.attr)
        self.assertEqual(None, p.val)

    def test_property_setter_good_substitution(self):
        content = textwrap.dedent(
            """
            .. entity:: P
            .. entity:: S

            .. |S_ID| property:: S.id.int

            Scene
            ~~~~~

            Shot
            ----

            .. property:: P.state |S_ID|

            """)
        ensemble = copy.deepcopy(PropertyDirectiveTests.personae)
        script = SceneScript("inline", doc=SceneScript.read(content))
        script.cast(script.select(ensemble))
        model = script.run()
        p = [l for s, l in model if isinstance(l, Model.Property)][-1]
        self.assertEqual("state", p.attr)
        self.assertIsInstance(p.val, int)


class FXDirectiveTests(unittest.TestCase):

    def test_fx(self):
        content = textwrap.dedent(
            """
            Scene
            ~~~~~

            Shot
            ----

            .. fx:: turberfield.dialogue.sequences.battle_royal whack.wav
               :offset: 0
               :duration: 3000
               :loop: 1

            """)
        script = SceneScript("inline", doc=SceneScript.read(content))
        model = script.run()
        shot, cue = next(iter(model))
        self.assertEqual(
            "turberfield.dialogue.sequences.battle_royal",
            cue.package
        )
        self.assertEqual("whack.wav", cue.resource)
        self.assertEqual(0, cue.offset)
        self.assertEqual(3000, cue.duration)
        self.assertEqual(1, cue.loop)

    def test_fx_bad_substitution(self):
        content = textwrap.dedent(
            """

            Scene
            ~~~~~

            Shot
            ----

            .. fx:: turberfield.dialogue.sequences.battle_royal barks/|P_NONE|/surprise.wav
               :offset: 0
               :duration: 3000
               :loop: 1

            """)
        ensemble = copy.deepcopy(PropertyDirectiveTests.personae)
        script = SceneScript("inline", doc=SceneScript.read(content))
        script.cast(script.select([ensemble[0]]))
        model = script.run()
        shot, cue = next(iter(model))
        self.assertEqual(
            "turberfield.dialogue.sequences.battle_royal",
            cue.package
        )
        self.assertEqual("barks//surprise.wav", cue.resource)
        self.assertEqual(0, cue.offset)
        self.assertEqual(3000, cue.duration)
        self.assertEqual(1, cue.loop)

    def test_fx_good_substitution(self):
        content = textwrap.dedent(
            """
            .. entity:: P

            Scene
            ~~~~~

            Shot
            ----

            .. fx:: turberfield.dialogue.sequences.battle_royal barks/|P_NAME|/surprise.wav
               :offset: 0
               :duration: 3000
               :loop: 1

            .. |P_NAME| property:: P.name.firstname
            """)
        ensemble = copy.deepcopy(PropertyDirectiveTests.personae)
        script = SceneScript("inline", doc=SceneScript.read(content))
        script.cast(script.select([ensemble[0]]))
        model = script.run()
        shot, cue = next(iter(model))
        self.assertEqual(
            "turberfield.dialogue.sequences.battle_royal",
            cue.package
        )
        self.assertEqual("barks/William/surprise.wav", cue.resource)
        self.assertEqual(0, cue.offset)
        self.assertEqual(3000, cue.duration)
        self.assertEqual(1, cue.loop)

class SelectTests(unittest.TestCase):

    @enum.unique
    class Aggression(EnumFactory, enum.Enum):
        calm = 0
        angry = 1

    @enum.unique
    class Contentment(EnumFactory, enum.Enum):
        sad = 0
        happy = 1

    @enum.unique
    class Location(EnumFactory, enum.Enum):
        pub = 0
        pub_bar = 1
        pub_carpark = 2
        pub_snug = 3
        pub_toilets = 4

    def test_select_with_required_state(self):

        content = textwrap.dedent("""
            .. entity:: FIGHTER_1
               :states: turberfield.dialogue.test.test_model.SelectTests.Aggression.angry

            .. entity:: FIGHTER_2
               :states: turberfield.dialogue.test.test_model.SelectTests.Contentment.sad

            .. entity:: WEAPON

               A weapon which makes a noise in use. 
            """)
        ensemble = copy.deepcopy(PropertyDirectiveTests.personae)
        ensemble[0].set_state(SelectTests.Contentment.sad)
        self.assertEqual(
            SelectTests.Contentment.sad,
            ensemble[0].get_state(SelectTests.Contentment)
        )
        ensemble[1].set_state(SelectTests.Aggression.angry)
        self.assertEqual(
            SelectTests.Aggression.angry,
            ensemble[1].get_state(SelectTests.Aggression)
        )
        script = SceneScript("inline", doc=SceneScript.read(content))
        rv = list(script.select(ensemble).values())
        self.assertEqual(ensemble[0], rv[1])
        self.assertEqual(ensemble[1], rv[0])

    def test_select_with_hierarchical_state(self):

        content = textwrap.dedent("""
            .. entity:: FIGHTER_1
               :states: turberfield.dialogue.test.test_model.SelectTests.Location.pub

            .. entity:: FIGHTER_2
               :states: turberfield.dialogue.test.test_model.SelectTests.Location.pub

            .. entity:: WEAPON

               A weapon which makes a noise in use. 
            """)
        ensemble = copy.deepcopy(PropertyDirectiveTests.personae)
        ensemble[0].set_state(SelectTests.Location.pub_bar)
        self.assertEqual(
            SelectTests.Location.pub_bar,
            ensemble[0].get_state(SelectTests.Location)
        )
        ensemble[1].set_state(SelectTests.Location.pub_toilets)
        self.assertEqual(
            SelectTests.Location.pub_toilets,
            ensemble[1].get_state(SelectTests.Location)
        )
        script = SceneScript("inline", doc=SceneScript.read(content))
        rv = list(script.select(ensemble).values())
        self.assertEqual(ensemble[0], rv[0])
        self.assertEqual(ensemble[1], rv[1])

    def test_select_with_integer_state(self):

        content = textwrap.dedent("""
            .. entity:: FIGHTER_1
               :states: 1

            .. entity:: FIGHTER_2
               :states: 2

            .. entity:: WEAPON

               A weapon which makes a noise in use.
            """)
        ensemble = copy.deepcopy(PropertyDirectiveTests.personae)
        ensemble[0].set_state(2)
        self.assertEqual(2, ensemble[0].get_state())
        ensemble[1].set_state(1)
        self.assertEqual(1, ensemble[1].get_state())
        script = SceneScript("inline", doc=SceneScript.read(content))
        rv = list(script.select(ensemble).values())
        self.assertEqual(ensemble[0], rv[1])
        self.assertEqual(ensemble[1], rv[0])

    def test_select_with_herarchical_integer_state(self):

        content = textwrap.dedent("""
            .. entity:: FIGHTER_1
               :states: 3

            .. entity:: FIGHTER_2
               :states: 3

            .. entity:: WEAPON

               A weapon which makes a noise in use.
            """)
        ensemble = copy.deepcopy(PropertyDirectiveTests.personae)
        ensemble[0].set_state(31)
        self.assertEqual(31, ensemble[0].get_state())
        ensemble[1].set_state(32)
        self.assertEqual(32, ensemble[1].get_state())
        script = SceneScript("inline", doc=SceneScript.read(content))
        rv = list(script.select(ensemble).values())
        self.assertEqual(ensemble[0], rv[0])
        self.assertEqual(ensemble[1], rv[1])

    def test_select_with_unfulfilled_state(self):

        content = textwrap.dedent("""
            .. entity:: FIGHTER_1
               :states: turberfield.dialogue.test.test_model.SelectTests.Aggression.angry

            .. entity:: FIGHTER_2
               :states: turberfield.dialogue.test.test_model.SelectTests.Contentment.sad

            .. entity:: WEAPON

               A weapon which makes a noise in use. 
            """)
        ensemble = copy.deepcopy(PropertyDirectiveTests.personae)
        ensemble[0].set_state(SelectTests.Contentment.sad)
        self.assertEqual(
            SelectTests.Contentment.sad,
            ensemble[0].get_state(SelectTests.Contentment)
        )
        ensemble[1].set_state(SelectTests.Contentment.sad)
        self.assertEqual(
            SelectTests.Contentment.sad,
            ensemble[1].get_state(SelectTests.Contentment)
        )
        script = SceneScript("inline", doc=SceneScript.read(content))
        rv = list(script.select(ensemble).values())
        self.assertIsNone(rv[0])
        self.assertEqual(ensemble[0], rv[1])

    def test_select_with_two_roles(self):

        content = textwrap.dedent("""
            .. entity:: CHARACTER_1
               :roles: CHARACTER_2

            .. entity:: CHARACTER_2

            """)
        ensemble = copy.deepcopy(PropertyDirectiveTests.personae[0:1])
        script = SceneScript("inline", doc=SceneScript.read(content))
        rv = list(script.select(ensemble, roles=2).values())
        self.assertEqual(ensemble[0], rv[0])
        self.assertEqual(ensemble[0], rv[1])
