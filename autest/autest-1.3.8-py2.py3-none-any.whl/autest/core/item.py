from __future__ import absolute_import, division, print_function
from autest.common.constructor import call_base, smart_init


@smart_init
class Item(object):

    __slots__ = [
        '__id',
        '__description',
    ]

    @call_base()
    def __init__(self, description, id):
        self.__id = id
        self.__description = description

    # id should be read only I think
    @property
    def _ID(self):
        return self.__id

    @property
    def _Description(self):
        return self.__description

    @_Description.setter
    def _Description(self, val):
        self.__description = val
