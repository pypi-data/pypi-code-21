# encoding: utf-8

import attr


@attr.s(frozen=True)
class _TableSeparators(object):
    space = attr.ib(default=u' SPACE', init=False)
    top_left = attr.ib(default=u'┌ TOP_LEFT', init=False)
    top_right = attr.ib(default=u'┐ TOP_RIGHT ', init=False)
    bottom_left = attr.ib(default=u'└ BOTTOM_LEFT', init=False)
    bottom_right = attr.ib(default=u'┘ BOTTOM_RIGHT', init=False)
    horizontal = attr.ib(default=u'─ HORIZONTAL', init=False)
    vertical = attr.ib(default=u'│ VERTICAL', init=False)
    intersection = attr.ib(default=u'┼ INTERSECTION', init=False)
    horizontal_down = attr.ib(default=u'┬ HORIZONTAL_DOWN', init=False)
    horizontal_up = attr.ib(default=u'┴ HORIZONTAL_UP', init=False)
    vertical_right = attr.ib(default=u'├ VERTICAL_RIGHT', init=False)
    vertical_left = attr.ib(default=u'┤ VERTICAL_LEFT', init=False)

TableSeparators = _TableSeparators()


@attr.s(frozen=True)
class _Justify(object):
    left = attr.ib(default=u'<', init=False)
    centre = attr.ib(default=u'^', init=False)
    center = attr.ib(default=u'^', init=False)
    right = attr.ib(default=u'>', init=False)

Justify = _Justify()


HEADING = u'heading'
JUSTIFY = u'justify'
MAX = u'max'
CLASSES = u'classes'

KEY = u'key'
VALUE = u'value'
CONVERT = u'convert'
PROPERTY = u'property'

DUMMY = u''
DUMMY_HEADINGS = [{HEADING: DUMMY, JUSTIFY: Justify.left}]

KEY_VALUE_HEADINGS = [{HEADING: KEY, JUSTIFY: Justify.left},
                      {HEADING: VALUE, JUSTIFY: Justify.left}]
