from mongoframes import *

__all__ = ['Dragon']


class Dragon(Frame):
    """
    A dragon.
    """

    _fields = {
        'name',
        'breed'
        }

    def __str__(self):
        return '{d.name} ({d.breed})'.format(d=self)