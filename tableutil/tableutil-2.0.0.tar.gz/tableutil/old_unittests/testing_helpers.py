# -*- coding: utf-8 -*-

import difflib

import logging_helper

from conversionutil.convert import convert_to_full_width_characters

logging = logging_helper.setup_logging(logger_name = __name__)

DIFFER = difflib.Differ()


def compare_strings(actual,
                    expected):

    actual = actual if isinstance(actual, list) else actual.splitlines()
    expected = expected if isinstance(expected, list) else expected.splitlines()

    diffs = [line for line in DIFFER.compare(expected,
                                             actual)]

    spacer = u'\n' + u' ' * len(u'Differences : ')

    if len(diffs) == len(expected):
        return u'No differences found...\n\n'\
               u'Expected :    {expected}\n\n'\
               .format(expected = spacer.join(expected))

    diff_spacer = spacer
    spacer += u'  '
    return convert_to_full_width_characters(
        u'Differences found...\n\n'
        u'Actual :        {actual}\n\n'
        u'Expected :      {expected}\n\n'
        u'Differences : {diffs}\n\n'
        .format(actual=spacer.join(actual),
                expected=spacer.join(expected),
                diffs=diff_spacer.join(diffs)))


def assert_unicode(actual,
                   expected):
    if actual != expected:
        diffs = compare_strings(actual=actual,
                                expected=expected)
        logging.error(diffs)
    assert actual == expected, u'See logged error for differences'


def assert_table_against_unicode(table,
                                 expected):
    assert_unicode(actual = unicode(table),
                   expected = expected)
