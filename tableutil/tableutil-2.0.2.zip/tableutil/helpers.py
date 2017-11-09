# encoding: utf-8

from .constants import (HEADING,
                        JUSTIFY,
                        TableSeparators,
                        Justify)


def table_format_string_to_table_format_dictionary(table_format_string):
    table_format_chars = [char for char in table_format_string.replace(u'\n', u'')]
    table_format_dictionary = {}
    for name in (TableSeparators.bottom_right,
                 TableSeparators.horizontal_up,
                 TableSeparators.horizontal,
                 TableSeparators.bottom_left,

                 TableSeparators.vertical_left,
                 TableSeparators.intersection,
                 TableSeparators.horizontal,
                 TableSeparators.vertical_right,

                 TableSeparators.vertical,
                 TableSeparators.vertical,
                 TableSeparators.space,
                 TableSeparators.vertical,

                 TableSeparators.top_right,
                 TableSeparators.horizontal_down,
                 TableSeparators.horizontal,
                 TableSeparators.top_left):

        try:
            table_char = table_format_chars.pop()

        except IndexError:
            raise ValueError(u'Bad Table Format String. Expected format:\n'
                             u'16 chars (newlines can be added) :\n'
                             u'    1:Top Left\n'
                             u'    2:Horizontal\n'
                             u'    3:Horizontal with Downstroke\n'
                             u'    4:Top Right\n'
                             u'    5:Vertical\n'
                             u'    6:Space\n'
                             u'    7:Vertical\n'
                             u'    8:Vertical\n'
                             u'    9:Vertical with Right stroke\n'
                             u'   10:Horizontal\n'
                             u'   11:Intersection\n'
                             u'   12:Vertical with Left stroke\n'
                             u'   13:Bottom Left\n'
                             u'   14:Horizontal\n'
                             u'   15:Horizontal with Up stroke\n'
                             u'   16:Bottom Right\n'
                             u"E.g.:"
                             u"┌─┬┐\\n\n"
                             u"│ ││\\n\n"
                             u"├─┼┤\\n\n"
                             u"└─┴┘\\n\n\n"
                             )

        table_format_dictionary[name] = table_char

    return table_format_dictionary


def make_index_headings(width,
                        justification=Justify.center):

    return [{HEADING: column, JUSTIFY: justification}
            for column in range(width)]


def escape_jira_markup(text):
    return u''.join([u'\\' + c if c in u'*_?-+^~{}#' else c for c in unicode(text)])


def is_a_table(object):
    return object.__class__.__name__ == u'Table'
