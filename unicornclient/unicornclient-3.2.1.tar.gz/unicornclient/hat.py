# pylint: disable=W0403,C0412,C0103
import logging

try:
    import unicornhat as unicorn
except ImportError:
    logging.warning("No unicornhat module")
    from .mock import unicornhat as unicorn

try:
    import microdotphat as microdot
except ImportError:
    logging.warning("No microdotphat module")
    from .mock import microdotphat as microdot

class Unicorn(object):
    def __init__(self):
        logging.info("Unicorn hat initialization")
        unicorn.set_layout(unicorn.AUTO)
        unicorn.rotation(0)
        unicorn.brightness(0.5)

        width, height = unicorn.get_shape()
        self.width = width
        self.height = height

    def brightness(self, brightness=0.5):
        unicorn.brightness(brightness)

    def clear(self):
        unicorn.clear()

    def set_pixel(self, x=0, y=0, r=255, g=255, b=255):
        unicorn.set_pixel(x, y, r, g, b)

    def show(self):
        unicorn.show()

    def set_all_pixel(self, r=255, g=255, b=255):
        for x in range(0, self.width):
            for y in range(0, self.height):
                self.set_pixel(x, y, r, g, b)

    def set_line_pixel(self, y=0, r=255, g=255, b=255):
        for x in range(0, self.width):
            self.set_pixel(x, y, r, g, b)

    def set_column_pixel(self, x=0, r=255, g=255, b=255):
        for y in range(0, self.height):
            self.set_pixel(x, y, r, g, b)

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

class Microdot(object):
    def __init__(self):
        logging.info("Microdot phat initialization")

    def clear(self):
        microdot.clear()

    def write_string(self, value):
        microdot.write_string(value, kerning=False)

    def show(self):
        microdot.show()
