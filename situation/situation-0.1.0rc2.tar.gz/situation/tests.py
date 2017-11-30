# -*- coding: utf-8 -*-
# situation (c) Ian Dennis Miller

from nose.plugins.attrib import attr
from flask_testing import TestCase
from flask_diamond import db
from .debug_app import create_app
from datetime import datetime
from . import Resource, Event, Person, Excerpt, Place, Item, Group


def simple_situation():
    person1 = Person.create(name="Rob")
    person2 = Person.create(name="Scott")

    group1 = Group.create(name="Friends")
    group1.members.extend([person1, person2])

    resource1 = Resource.create(
        name="Headline news for November 23",
        publisher="Big Paper Post",
        author="John Doe",
        url="http://example.com/1",
        )

    place1 = Place.create(
        name="Rob's House",
        address="200 Road St",
        lat=43,
        lon=-79,
        )

    excerpt1 = Excerpt.create(
        content="Snippet 1",
        resource=resource1,
        )

    Event.create(name="Incident",
        place=place1,
        timestamp=datetime(2012, 1, 11, 7, 30, 0),
        actors=[person1, person2],
        excerpts=[excerpt1],
        description="The Incident"
    )

    item1 = Item.create(name="Video",
        owners=[person1]
    )
    assert item1


class BasicTestCase(TestCase):

    def create_app(self):
        return(create_app())

    def setUp(self):
        db.drop_all()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_basic(self):
        "ensure the minimum test works"
        simple_situation()

    @attr("single")
    def test_marshall(self):
        simple_situation()
        resource1 = Resource.find(name="Headline news for November 23")
        place1 = Place.find(name="Rob's House")
        person1 = Person.find(name="Rob")
        event1 = Event.find(name="Incident")
        excerpt1 = Excerpt.find(content="Snippet 1")
        item1 = Item.find(name="Video")
        group1 = Group.find(name="Friends")

        print("resource", resource1.dump(), "\n---")
        print("excerpt", excerpt1.dump(), "\n---")
        print("person", person1.dump(), "\n---")
        print("place", place1.dump(), "\n---")
        print("event", event1.dump(), "\n---")
        print("item", item1.dump(), "\n---")
        print("group", group1.dump(), "\n---")

        # print(item1.as_hash())

        # assert False

    @attr("skip")
    def test_skip(self):
        "this always fails, except when it is skipped"
        self.assertTrue(False)
