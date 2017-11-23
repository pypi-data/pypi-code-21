import logging

logging.basicConfig(level=logging.DEBUG)

from dataclay.debug.test_classes.new_style_classes import GenericObject

g = GenericObject()

print g.func(4, 5)

