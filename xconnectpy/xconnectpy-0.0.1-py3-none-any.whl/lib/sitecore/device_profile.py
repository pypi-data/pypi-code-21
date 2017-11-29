#!/usr/bin/python

from xconnectpy.lib.base import Entity
from xconnectpy.lib.util import Guid


class DeviceProfile(Entity):

    def __init__(self, id: Guid):
        self.id = id
