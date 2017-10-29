"""This module contains classes and functions for processing colors."""

from random import randint

class Color:
    """Represents a color.

    :param int r: The Red value (0-255).
    :param int g: The Green value (0-255).
    :param int b: The Blue value (0-255).
    :raises TypeError: if a non-int RGB value is given.
    :raises ValueError: if an RGB value outside 0-255 is given."""

    def __init__(self, r, g, b):
        for rgb in (r, g, b):
            if not isinstance(rgb, int):
                raise TypeError("RGB value {} is not int".format(rgb))
            if rgb < 0 or rgb > 255:
                raise ValueError("RGB value {} not within 0-255".format(rgb))
        self._r, self._g, self._b = r, g, b


    @staticmethod
    def from_hex(hexcolor):
        """An alternate constructor which creates a color from a hex string
        such as ``'#0B9586'``. The preceding ``#`` is optional.

        :param str hexcolor: The hex string representing the desired color.
        :raises TypeError: if a non-string is given.
        :raises ValueError: if the hex string is not valid.
        :rtype: ``Color``"""

        if not isinstance(hexcolor, str):
            raise TypeError("{} is not a string".format(hexcolor))
        if hexcolor and hexcolor[0] == "#":
            hexcolor = hexcolor[1:]
        try:
            if len(hexcolor) != 6: raise ValueError
            rgb = [int(hexcolor[i * 2:i * 2 + 2], 16) for i in range(3)]
            return Color(*rgb)
        except:
            raise ValueError("{} is not a valid hex color".format(hexcolor))


    @staticmethod
    def random():
        """An alternate constructor which creates a random color

        :rtype: ``Color``"""

        return Color(randint(0, 255), randint(0, 255), randint(0, 255))


    def __repr__(self):
        return "<Color ({}, {}, {})>".format(self._r, self._g, self._b)


    def rgb(self):
        """Returns the color's RGB values.

        :rtype: ``tuple``"""

        return (self._r, self._g, self._b)


    def hex(self):
        """Returns the color as a hex string (#RRGGBB)

        :rtype: ``str``"""

        return "#{:02X}{:02X}{:02X}".format(self._r, self._g, self._b)


    def mutate(self):
        """Creates a new :py:class:`.Color` that is a slight variation on this
        one, but with the RGB values randomised within 16 either in either
        direction.

        :rtype: ``Color``"""

        r = randint(self._r - 16, self._r + 16)
        g = randint(self._g - 16, self._g + 16)
        b = randint(self._b - 16, self._b + 16)
        r = (r if r >= 0 else 0) if r <= 255 else 255
        g = (g if g >= 0 else 0) if g <= 255 else 255
        b = (b if b >= 0 else 0) if b <= 255 else 255
        return Color(r, g, b)



Color.RED = Color(255, 40, 40)
Color.GREEN = Color(39, 174, 96)
Color.BLUE = Color(52, 152, 219)
Color.YELLOW = Color(241, 196, 15)
Color.ORANGE = Color(230, 126, 34)
Color.PURPLE = Color(142, 68, 173)
Color.BROWN = Color(124, 63, 0)
Color.GRAY = Color(204, 204, 204)
Color.WHITE = Color(255, 255, 255)
Color.BLACK = Color(17, 17, 17)
