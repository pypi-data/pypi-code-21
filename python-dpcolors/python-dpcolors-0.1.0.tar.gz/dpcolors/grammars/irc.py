import colorsys
import re

from dpcolors import ColorPart, ColorRGB
from . import BaseRegexParser, BaseParser

COLORS = [
    (255, 255, 255),
    (0, 0, 0),
    (0, 0, 127),
    (0, 147, 0),
    (255, 0, 0),
    (127, 0, 0),
    (156, 0, 156),
    (252, 127, 0),
    (255, 255, 0),
    (0, 252, 0),
    (0, 147, 147),
    (0, 255, 255),
    (0, 0, 252),
    (255, 0, 255),
    (127, 127, 127),
    (210, 210, 210)
]

COLORS_HSV = [colorsys.rgb_to_hsv(*[j / 255 for j in i]) for i in COLORS]


class BgFg(BaseRegexParser):
    regex = re.compile('\x03(\\d{1,2}),(\\d{1,2})')

    def process(self, match):
        fg = ColorRGB(*COLORS[int(match.group(1))], max_value=255)
        bg = ColorRGB(*COLORS[int(match.group(2))], max_value=255)
        return ColorPart('', fg, bg)


class Fg(BaseRegexParser):
    regex = re.compile('\x03(\\d{1,2})')

    def process(self, match):
        fg = ColorRGB(*COLORS[int(match.group(1))], max_value=255)
        return ColorPart('', fg)


class Reset(BaseRegexParser):
    regex = re.compile('\x03')

    def process(self, match):
        return ColorPart('')


class Ignore(BaseRegexParser):
    regex = re.compile('[\x02\x1D\x1F\x16\x0F]')

    def process(self, match):
        return ''


class IRCParser(BaseParser):
    markers = [BgFg(), Fg(), Reset()]
    special = [Ignore()]


def parse(text):
    parser = IRCParser()
    return parser.parse(text)
