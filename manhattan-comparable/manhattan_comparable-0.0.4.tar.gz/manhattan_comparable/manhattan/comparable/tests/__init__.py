from mongoframes import *

from manhattan.comparable.frames import ComparableFrame

__all__ = [
    'Dragon',
    'Lair',
    'User'
    ]


class Lair(ComparableFrame):
    """
    A lair in which a dragon resides.
    """

    _fields = {
        'name'
        }

    def __str__(self):
        return self.name


class Dragon(ComparableFrame):
    """
    A dragon.
    """

    _fields = {
        'name',
        'breed',
        'hobbies',
        'lair',
        'secret_password'
        }

    _compared_refs = {'lair': Lair}

    _default_projection = {
        'lair': {'$ref': Lair}
        }

    def __str__(self):
        return self.name


class User(ComparableFrame):
    """
    A user, a keeper of records.
    """

    _fields = {'name'}

    def __str__(self):
        return self.name