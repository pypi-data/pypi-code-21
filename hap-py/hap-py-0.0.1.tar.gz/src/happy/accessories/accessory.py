import enum

from ..constants import Categories, States, Discoverable


class Attribute(object):
    def __init__(self, value, doc=None):
        if not isinstance(value, (str, enum.Enum)):
            raise TypeError("Accessory attributes must be strings!")
        if doc is None:
            doc = value
        self.value = value
        self.docstring = doc

    def __get__(self, obj, cls):
        return self.value

    def __getattribute__(self, value):
        if value == "__doc__":
            attr = object.__getattribute__(self, "docstring")
        else:
            attr = object.__getattribute__(self, value)
        return attr


class Accessory(object):
    name = Attribute('Happy Bridge', 'The accessory name.')
    id = Attribute('AA:BB:CC:DD:EE:FA', 'A mac-like ID for uniquely id-ing accessories')
    category = Attribute(Categories.BRIDGE, 'The accessory category.')
    state = Attribute(States.ON, 'The accessory state.')
    paired = Attribute(Discoverable.TRUE, 'Whether or not the accessory is discoverable.')
    config = Attribute('1', ' Increasing this "version number" signals iOS devices to re-fetch /accessories data.')
