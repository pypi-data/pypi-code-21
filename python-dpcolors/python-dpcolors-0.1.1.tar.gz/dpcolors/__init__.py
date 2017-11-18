import colorsys
import re

from colors import color as ansicolor


ESC = '\x1b'


class Color8Bit:
    """
    Helper class for dealing with 8-bit colors
    """
    BLACK = 0
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    MAGENTA = 5
    CYAN = 6
    WHITE = 7

    def __init__(self, color, bright):
        self.color = color
        self.bright = bright

    def is_color(self) -> bool:
        return self.color not in (self.BLACK, self.WHITE)

    def to_irc(self) -> int:
        """
        Convert to mIRC color Code
        :return: IRC color code
        """
        d = {
            (self.BLACK, True): 14,
            (self.BLACK, False): 1,
            (self.RED, True): 4,
            (self.RED, False): 5,
            (self.GREEN, True): 9,
            (self.GREEN, False): 3,
            (self.YELLOW, True): 8,
            (self.YELLOW, False): 7,
            (self.BLUE, True): 12,
            (self.BLUE, False): 2,
            (self.MAGENTA, True): 13,
            (self.MAGENTA, False): 6,
            (self.CYAN, True): 11,
            (self.CYAN, False): 10,
            (self.WHITE, True): 0,
            (self.WHITE, False): 15
        }
        return d[(self.color, self.bright)]

    def to_name(self) -> str:
        """
        Convert to ANSI color name
        :return: ANSI color name
        """
        return {
            self.BLACK: 'black',
            self.RED: 'red',
            self.GREEN: 'green',
            self.YELLOW: 'yellow',
            self.BLUE: 'blue',
            self.MAGENTA: 'magenta',
            self.CYAN: 'cyan',
            self.WHITE: 'white'
        }[self.color]


class ColorBase:
    pass


class ColorRGB(ColorBase):
    """
    Class representing an RGB color
    """
    def __init__(self, r, g, b, max_value=1):
        self.r = r
        self.g = g
        self.b = b
        self.max = max_value

    def __iter__(self):
        yield self.r
        yield self.g
        yield self.b

    def scale(self, new_max_value=1):
        """
        Scale R, G and B parameters
        :param new_max_value: how much to scale
        :return: a new ColorRGB instance
        """
        f = new_max_value / self.max
        return ColorRGB(self.r * f,
                        self.g * f,
                        self.b * f,
                        max_value=new_max_value)

    def to_dp(self) -> str:
        """
        Convert to a DP color marker
        :return: DP color marker
        """
        return '^x{:x}{:x}{:x}'.format(*[round(i) for i in self.scale(15)])

    def to_8bit(self):
        """
        Convert to 8-bit color
        :return: Color8Bit instance
        """
        h, s, v = colorsys.rgb_to_hsv(*self.scale(1))
        # Check if the color is a shade of grey
        if s * v < 0.3:
            if v < 0.3:
                return Color8Bit(Color8Bit.BLACK, False)
            elif v < 0.66:
                return Color8Bit(Color8Bit.BLACK, True)
            elif v < 0.91:
                return Color8Bit(Color8Bit.WHITE, False)
            else:
                return Color8Bit(Color8Bit.WHITE, True)
        # not grey? What color is it then?
        if h < 0.041 or h > 0.92:
            res = Color8Bit.RED
        elif h < 0.11:
            # orange = dark yellow
            return Color8Bit(Color8Bit.YELLOW, False)
        elif h < 0.2:
            res = Color8Bit.YELLOW
        elif h < 0.45:
            res = Color8Bit.GREEN
        elif h < 0.6:
            res = Color8Bit.CYAN
        elif h < 0.74:
            res = Color8Bit.BLUE
        else:
            res = Color8Bit.MAGENTA
        return Color8Bit(res, v > 0.6)

    def __repr__(self):
        return 'Color(%s, %s, %s)' % (self.r / self.max,
                                      self.g / self.max,
                                      self.b / self.max)


class NoColor(ColorBase):
    def __bool__(self):
        return False

    def __repr__(self):
        return 'NoColor()'

    def to_dp(self):
        return '^7'

    def to_8bit(self):
        return Color8Bit(Color8Bit.BLACK, False)


class ColorPart:
    """
    Class representing a part of single-colored part of a colored string
    """
    def __init__(self, text, fg_color=None, bg_color=None):
        if fg_color:
            self.color = fg_color
        else:
            self.color = NoColor()
        if bg_color:
            self.bg_color = bg_color
        else:
            self.bg_color = NoColor()
        self.text = text

    def __repr__(self):
        if self.bg_color:
            return 'ColorPart(%r, %r, %r)' % (self.text, self.color, self.bg_color)
        elif self.color:
            return 'ColorPart(%r, %r)' % (self.text, self.color)
        else:
            return 'ColorPart(%r)' % self.text

    def to_dp(self):
        """
        Convert to darkplaces color format
        :return:
        """
        text = self.text.replace('^', '^^')
        return '%s%s' % (self.color.to_dp(), text)

    def to_irc(self):
        """
        Convert to mIRC color format
        :return:
        """
        ignore_re = re.compile('[\x03\x02\x1D\x1F\x16\x0F]')
        text = ignore_re.sub('', self.text)
        if self.color and self.bg_color:
            return '\x03%02d,%02d%s' % (self.color.to_8bit().to_irc(),
                                        self.bg_color.to_8bit().to_irc(),
                                        text)
        elif self.color:
            c = self.color.to_8bit()
            if c.is_color():
                return '\x03%02d%s' % (c.to_irc(), text)
            else:
                return '\x03\x0f' + text
        elif self.bg_color:
            return '\x0301,%02d%s' % (self.bg_color.to_8bit().to_irc(), text)
        else:
            return '\x03\x0f' + text

    def to_ansi_8bit(self):
        """
        Convert to ANSI 8-bit color format
        :return:
        """
        text = self.text.replace('\x1b', '')
        if self.color and self.bg_color:
            c = self.color.to_8bit()
            return ansicolor(text,
                             fg=c.to_name(),
                             bg=self.bg_color.to_8bit().to_name(),
                             style=c.bright and 'bold' or None)
        elif self.color:
            c = self.color.to_8bit()
            return ansicolor(text,
                             fg=c.is_color() and c.to_name(),
                             style=c.bright and 'bold' or None)
        elif self.bg_color:
            return ansicolor(text,
                             bg=self.bg_color.to_8bit().to_name())
        else:
            return text

    def to_ansi_24bit(self):
        """
        Convert to ANSI 24-bit color format
        :return:
        """
        text = self.text.replace('\x1b', '')
        if self.color and self.bg_color:
            c = self.color.scale(255)
            bg_c = self.bg_color.scale(255)
            return ansicolor(text,
                             fg=(c.r, c.g, c.b),
                             bg=(bg_c.r, bg_c.g, bg_c.b))
        elif self.color:
            c = self.color.scale(255)
            return ansicolor(text,
                             fg=(c.r, c.g, c.b))
        elif self.bg_color:
            bg_c = self.bg_color.scale(255)
            return ansicolor(text,
                             bg=(bg_c.r, bg_c.g, bg_c.b))
        else:
            return text

    def __str__(self):
        return self.text


class ColorString:
    """
    Class representing a colored string
    """
    def __init__(self, parts):
        self.parts = parts
        self.original_type = None
        self.original_bytes = None

    @classmethod
    def from_dp(cls, text, use_unicode_for_glyphs=True):
        """
        Create a new instance of ColorString from a darkplaces-formatted text
        :param text: darkplaces text string (either str or bytes)
        :param use_unicode_for_glyphs: convert unicode glyphs to ascii
        :return: ColorString instance
        """
        from .grammars.dp import parse as parse_dp
        if isinstance(text, bytes):
            original_bytes = text
            text = text.decode('utf8')
        else:
            original_bytes = text.encode('utf8')
        instance = parse_dp(text, use_unicode_for_glyphs=use_unicode_for_glyphs)
        instance.original_type = 'dp'
        instance.original_bytes = original_bytes
        return instance

    def to_dp(self, preserve_original=True):
        """
        Convert to darkplaces color format
        :param preserve_original: if the current ColorString instance was created from a darkplaces text,
               then just return the original string
        :return:
        """
        if preserve_original and self.original_type == 'dp':
            return self.original_bytes
        res = []
        for i in self.parts:
            res.append(i.to_dp())
        s = ''.join(res) + '^7'
        return s.encode('utf8')

    @classmethod
    def from_irc(cls, text):
        """
        Create a new instance of ColorString from a mIRC-formatted text
        :param text: mIRC-formatted text
        :return:
        """
        from .grammars.irc import parse as parse_irc
        if isinstance(text, bytes):
            original_bytes = text
            text = text.decode('utf8')
        else:
            original_bytes = text.encode('utf8')
        instance = parse_irc(text)
        instance.original_type = 'irc'
        instance.original_bytes = original_bytes
        return instance

    def to_irc(self, preserve_original=True):
        """
        Convert to mIRC format
        :param preserve_original: if the current ColorString instance was created from mIRC text,
               then just return the original string
        :return:
        """
        if preserve_original and self.original_type == 'irc':
            return self.original_bytes
        res = []
        for i in self.parts:
            res.append(i.to_irc())
        s = ''.join(res) + '\x03\x0f'
        return s.encode('utf8')

    def to_ansi_8bit(self):
        """
        Convert to ANSI 8-bit
        :return:
        """
        res = []
        for i in self.parts:
            res.append(i.to_ansi_8bit())
        return ''.join(res).encode('utf8')

    def to_ansi_24bit(self):
        """
        Convert to ANSI 24-bit
        :return:
        """
        res = []
        for i in self.parts:
            res.append(i.to_ansi_24bit())
        return ''.join(res).encode('utf8')

    def __str__(self):
        return ''.join([str(i) for i in self.parts])

    def __repr__(self):
        parts = [repr(i) for i in self.parts]
        return 'ColorString([%s])' % ', '.join(parts)
