# -*- coding: utf-8 -*-
# situation (c) Ian Dennis Miller

import string
import random
from flask_marshmallow.fields import fields
from flask_diamond import db, ma
from flask_diamond.mixins.crud import CRUDMixin
from flask_diamond.mixins.marshmallow import MarshmallowMixin

from slugify import slugify


# https://stackoverflow.com/questions/2257441/python-random-string-generation-with-upper-case-letters-and-digits
def id_generator(size=8, chars=None):
    """
    Create a random sequence of letters and numbers.

    :param size: the desired length of the sequence
    :type size: integer
    :param chars: the eligible character set to draw from when picking random characters
    :type chars: string
    :returns: a string with the random sequence
    """
    if chars is None:
        chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for x in range(size))


class ResourceSchema(ma.Schema):
    "Description"

    class Meta:
        additional = ("id", "unique", "name", "url", "publisher", "author", "description")


class Resource(db.Model, CRUDMixin, MarshmallowMixin):
    """
    A Resource is an authoritative reference from which information is drawn.

    :param id: the database object identifier
    :type id: integer
    """

    __schema__ = ResourceSchema
    id = db.Column(db.Integer, primary_key=True)
    unique = db.Column(db.String(255), unique=True, default=id_generator)
    name = db.Column(db.String(4096))
    url = db.Column(db.String(4096))
    publisher = db.Column(db.String(4096))
    author = db.Column(db.String(4096))
    description = db.Column(db.String(8**7))

    def __str__(self):
        return(self.url)


class ExcerptSchema(ma.Schema):
    "Description"

    class Meta:
        additional = ("id", "unique", "content", "resource_id", "xpath")


class Excerpt(db.Model, CRUDMixin, MarshmallowMixin):
    """
    Description.

    :param id: the database object identifier
    :type id: integer
    """

    __schema__ = ExcerptSchema
    id = db.Column(db.Integer, primary_key=True)
    unique = db.Column(db.String(255), unique=True, default=id_generator)
    content = db.Column(db.String(8**7))
    resource = db.relationship('Resource', backref='excerpts')
    resource_id = db.Column(db.Integer, db.ForeignKey('resource.id'), nullable=False)
    xpath = db.Column(db.String(4096))

    def __str__(self):
        return(self.content)


class AcquaintanceExcerpt(db.Model, CRUDMixin):
    "Excerpts."

    __tablename__ = 'acquaintance_excerpts'
    __table_args__ = (
        db.ForeignKeyConstraint(
            ['person_id', 'acquainted_id'],
            ['acquaintance.person_id', 'acquaintance.acquainted_id']
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    excerpt_id = db.Column(db.Integer, db.ForeignKey('excerpt.id'), nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    acquainted_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)

"Excerpts."
persons_excerpts = db.Table('persons_excerpts',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('person_id', db.Integer, db.ForeignKey('person.id')),
    db.Column('excerpt_id', db.Integer, db.ForeignKey('excerpt.id'))
)

"Excerpts."
places_excerpts = db.Table('places_excerpts',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('place_id', db.Integer, db.ForeignKey('place.id')),
    db.Column('excerpt_id', db.Integer, db.ForeignKey('excerpt.id'))
)

"Excerpts."
items_excerpts = db.Table('items_excerpts',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('item_id', db.Integer, db.ForeignKey('item.id')),
    db.Column('excerpt_id', db.Integer, db.ForeignKey('excerpt.id'))
)

"Excerpts."
events_excerpts = db.Table('events_excerpts',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id')),
    db.Column('excerpt_id', db.Integer, db.ForeignKey('excerpt.id'))
)

"Excerpts."
groups_excerpts = db.Table('groups_excerpts',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id')),
    db.Column('excerpt_id', db.Integer, db.ForeignKey('excerpt.id'))
)


class PersonSchema(ma.Schema):
    "Description"

    slug = fields.Method("get_slugify")
    excerpts = fields.Nested('ExcerptSchema', allow_none=True, many=True, only=["id"])
    events = fields.Nested('EventSchema', allow_none=True, many=True, only=["id"])
    places = fields.Nested('PlaceSchema', allow_none=True, many=True, only=["id"])
    possessions = fields.Nested('ItemSchema', allow_none=True, many=True, only=["id"])
    properties = fields.Nested('PlaceSchema', allow_none=True, many=True, only=["id"])
    groups = fields.Nested('GroupSchema', allow_none=True, many=True, only=["id"])
    acquaintances = fields.Nested('PersonSchema', allow_none=True, many=True, only=["id"])

    # TODO: this is a nested query
    # "encounters": [i.id for e in self.events for i in e.items],

    def get_slugify(self, obj):
        return(slugify(obj.name))

    class Meta:
        additional = ("id", "name", "alias", "unique")


class Person(db.Model, CRUDMixin, MarshmallowMixin):
    """
    Description.

    :param id: the database object identifier
    :type id: integer
    """

    __schema__ = PersonSchema
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    alias = db.Column(db.String(255))
    unique = db.Column(db.String(255), unique=True, default=id_generator)
    excerpts = db.relationship('Excerpt', secondary="persons_excerpts", lazy='dynamic')

    def isa(self, isa_type, of=None):
        e = Acquaintance(person=self, isa=isa_type, acquainted=of)
        result = e.save()
        return result

    def __str__(self):
        return(self.name)


class AcquaintanceSchema(ma.Schema):
    "Description"

    excerpts = fields.Nested('ExcerptSchema', allow_none=True, many=True, only=["id"])

    class Meta:
        additional = ("isa", "person", "acquainted")


class Acquaintance(db.Model, CRUDMixin, MarshmallowMixin):
    """
    Description.

    :param id: the database object identifier
    :type id: integer
    """

    __schema__ = AcquaintanceSchema
    isa = db.Column(db.String(64))
    excerpts = db.relationship('Excerpt', secondary="acquaintance_excerpts", lazy='dynamic')
    person_id = db.Column(db.Integer(), db.ForeignKey('person.id'), primary_key=True)
    person = db.relationship(Person, primaryjoin=person_id == Person.id, backref='acquaintances')
    acquainted_id = db.Column(db.Integer(), db.ForeignKey('person.id'), primary_key=True)
    acquainted = db.relationship(Person, primaryjoin=acquainted_id == Person.id)

    def add_excerpt(self, excerpt):
        annotation = AcquaintanceExcerpt.create(
            excerpt_id=excerpt.id,
            person_id=self.person_id,
            acquainted_id=self.acquainted_id
            )
        return annotation

    def __str__(self):
        return("%s isa %s of %s)" % (self.person, self.isa, self.acquainted))


class PlaceSchema(ma.Schema):
    "Description"

    slug = fields.Method("get_slugify")
    excerpts = fields.Nested('ExcerptSchema', allow_none=True, many=True, only=["id"])
    events = fields.Nested('EventSchema', allow_none=True, many=True, only=["id"])
    owners = fields.Nested('PersonSchema', allow_none=True, many=True, only=["id"])

    def get_slugify(self, obj):
        return(slugify(obj.name))

    class Meta:
        additional = ("id", "unique", "name", "description", "address", "lat", "lon")


class Place(db.Model, CRUDMixin, MarshmallowMixin):
    """
    Description.

    :param id: the database object identifier
    :type id: integer
    """

    __schema__ = PlaceSchema
    id = db.Column(db.Integer, primary_key=True)
    unique = db.Column(db.String(255), unique=True, default=id_generator)
    name = db.Column(db.String(255))
    description = db.Column(db.String(8**7))
    address = db.Column(db.String(4096))
    lat = db.Column(db.Float())
    lon = db.Column(db.Float())
    owners = db.relationship('Person', secondary="places_owners", lazy='dynamic',
        backref="properties")
    excerpts = db.relationship('Excerpt', secondary="places_excerpts", lazy='dynamic')

    def __str__(self):
        return(self.name)

places_owners = db.Table('places_owners',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('place_id', db.Integer, db.ForeignKey('place.id')),
    db.Column('owner_id', db.Integer, db.ForeignKey('person.id'))
)


class ItemSchema(ma.Schema):
    "Description"

    slug = fields.Method("get_slugify")
    excerpts = fields.Nested('ExcerptSchema', allow_none=True, many=True, only=["id"])
    owners = fields.Nested('PersonSchema', allow_none=True, many=True, only=["id"])

    def get_slugify(self, obj):
        return(slugify(obj.name))

    class Meta:
        additional = ("id", "unique", "name", "description")


class Item(db.Model, CRUDMixin, MarshmallowMixin):
    """
    Description.

    :param id: the database object identifier
    :type id: integer
    """

    __schema__ = ItemSchema
    id = db.Column(db.Integer, primary_key=True)
    unique = db.Column(db.String(255), unique=True, default=id_generator)
    name = db.Column(db.String(255))
    description = db.Column(db.String(8**7))
    owners = db.relationship('Person', secondary="items_owners", lazy='dynamic', backref="items")
    excerpts = db.relationship('Excerpt', secondary="items_excerpts", lazy='dynamic')

    def __str__(self):
        return(self.name)

items_owners = db.Table('items_owners',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('item_id', db.Integer, db.ForeignKey('item.id')),
    db.Column('owner_id', db.Integer, db.ForeignKey('person.id'))
)


class GroupSchema(ma.Schema):
    slug = fields.Method("get_slugify")
    excerpts = fields.Nested('ExcerptSchema', allow_none=True, many=True, only=["id"])
    members = fields.Nested('PersonSchema', allow_none=True, many=True, only=["id"])

    def get_slugify(self, obj):
        return(slugify(obj.name))

    class Meta:
        additional = ("id", "unique", "name")


class Group(db.Model, CRUDMixin, MarshmallowMixin):
    """
    Description.

    :param id: the database object identifier
    :type id: integer
    """

    __schema__ = GroupSchema
    id = db.Column(db.Integer, primary_key=True)
    unique = db.Column(db.String(255), unique=True, default=id_generator)
    name = db.Column(db.String(255))
    members = db.relationship('Person', secondary="groups_members", lazy='dynamic',
        backref="groups")
    excerpts = db.relationship('Excerpt', secondary="groups_excerpts", lazy='dynamic')

    def __str__(self):
        return self.name

groups_members = db.Table('groups_members',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id')),
    db.Column('member_id', db.Integer, db.ForeignKey('person.id'))
)


class EventSchema(ma.Schema):
    slug = fields.Method("get_slugify")
    timestamp = fields.Method("get_timestamp")
    excerpts = fields.Nested('ExcerptSchema', allow_none=True, many=True, only=["id"])
    items = fields.Nested('ItemSchema', allow_none=True, many=True, only=["id"])
    actors = fields.Nested('PersonSchema', allow_none=True, many=True, only=["id"])

    def get_slugify(self, obj):
        return(slugify(obj.name))

    def get_timestamp(self, obj):
        return(obj.timestamp.strftime('%Y-%m-%dT%H:%M:%S'))

    class Meta:
        additional = ("id", "unique", "name", "phone", "description", "place_id")


class Event(db.Model, CRUDMixin, MarshmallowMixin):
    """
    Description.

    :param id: the database object identifier
    :type id: integer
    """

    __schema__ = EventSchema
    id = db.Column(db.Integer, primary_key=True)
    unique = db.Column(db.String(255), unique=True, default=id_generator)
    name = db.Column(db.String(255))
    description = db.Column(db.String(8**7))
    place_id = db.Column(db.Integer, db.ForeignKey('place.id'))
    place = db.relationship("Place", backref="events")
    phone = db.Column(db.Boolean(), default=False)
    timestamp = db.Column(db.DateTime())
    actors = db.relationship('Person', secondary="events_actors", lazy='dynamic', backref="events")
    excerpts = db.relationship('Excerpt', secondary="events_excerpts", lazy='dynamic')
    items = db.relationship('Item', secondary="events_items", lazy='dynamic')

    def __str__(self):
        return self.name

events_actors = db.Table('events_actors',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id')),
    db.Column('actor_id', db.Integer, db.ForeignKey('person.id'))
)

events_items = db.Table('events_items',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id')),
    db.Column('item_id', db.Integer, db.ForeignKey('item.id'))
)
