#!/usr/bin/python
# -*- coding: utf-8 -*-

import codecs
from collections import OrderedDict

__author__ = u'Hywel Thomas'
__copyright__ = u'Copyright (C) 2016 Hywel Thomas'


class BadTextTable(Exception):
    pass


def get_headings_for_text_table(text_table,
                                field_delimiter = u'|'):
    try:
        headings = codecs.open(text_table, u'r', encoding = u'utf8').read()
    except IOError:
        headings = text_table.splitlines()[0]
    return [heading.strip() for heading in headings.split(field_delimiter)]


def is_description(line):
    try:
        return line[0] == u'@'
    except IndexError:
        return False


def trim_description(line):
    line = line[1:] # Throw away the '@'
    try:
       # Only trim the first space.
       if line[0] == u' ':
           line = line[1:] # throw away first space
    except IndexError:
        pass
    return line


def is_comment(line):
    try:
        return line[0] == u'#'
    except IndexError:
        return False


def detect_list(field,
                detect_lists,
                delimiter):
    if detect_lists:
        field = [element.strip() for element in field.strip().split(delimiter)]
        if len(field) == 1:
            field = field[0]
    return field.strip()


def extract_keys(line,
                 field_delimiter):
    return [field.strip() for field in line.split(field_delimiter)]


def check_separator_line(separator,
                         keys,
                         separator_line,
                         separator_delimiter):
    separator = separator.strip()
    separator_parts = separator.split(separator_delimiter)
    if len(separator_parts) != len(keys):
        raise ValueError(u"Badly formed separator line. "\
                         u"Doesn't match number of fields detected")

    if len([c for c in u''.join(separator_parts) if c != separator_line]) != 0:
        raise ValueError(u'Badly formed separator line. \n{separator}\n"\
                         u"Use {l}{d}{l}{d}{l} etc'.format(d = separator_delimiter,
                                                           l = separator_line*4,
                                                           separator = separator))


def text_table_to_list(text_table,
                       field_delimiter = u'|',
                       separator_line = u'-',
                       separator_delimiter = u'+',
                       detect_lists   = False,
                       list_delimiter = u','):
    """
    Creates a Python list from a text based table.
    e.g.
    a string or file containing:

        Name    | Device_ID | Bouquet | Sub-Bouquet
        --------+-----------+---------+------------
        @ Description 1.
        # Comment 1
        htx     | 34939046  |   4101  |      1
        kd1     | 34939007  |   4101  |      1
        @ Description 2.

    yields list like this:

        {u'Description': [u'Description 1. Description 2.],
         u'Headings': [u'u'Bouquet',
                       u'Device_ID',
                       u'Name',
                       u'Sub-Bouquet'],
         u'Data' : [{u'Bouquet'    : u'4101',
                     u'Device_ID'  : u'34939046',
                     u'Name'       : u'htx',
                     u'Sub-Bouquet': u'1'},
                    {u'Bouquet'    : u'4101',
                    u'Device_ID'  : u'34939007',
                    u'Name'       : u'kd1',
                    u'Sub-Bouquet': u'1'}]}

    :param text_table:
    :return: DICT
    """

    def extract_list(lines):

        lines = iter(lines)

        try:
            keys = extract_keys(line = next(lines),
                                field_delimiter = field_delimiter)
        except IndexError:
            raise BadTextTable(u'No header row detected')

        try:
            check_separator_line(separator = next(lines),
                                 keys      = keys,
                                 separator_line = separator_line,
                                 separator_delimiter = separator_delimiter)
        except StopIteration:
            # A bit cheeky...
            # Couldn't find a second line to check as a separator.
            # Make an assumption that the the original single line
            # was a filename, and raising an IOError
            if len(keys) == 1:
                filename = keys[0]
                if u'.' in filename or u'\\' in filename or u'/' in filename:
                    raise IOError(u'No file found or only header row supplied for text table')

            raise ValueError(u'Separator line not found\n"\
                             u"Use {l}{d}{l}{d}{l} etc'.format(d = separator_delimiter,
                                                               l = separator_line*4))

        rows = []
        descriptions = []

        while True:
            try:
                line = next(lines).strip()
            except StopIteration:
                break

            if is_comment(line):
                 pass # throw away
            elif is_description(line):
                 descriptions.append(trim_description(line))
            elif line:
                 values = [detect_list(field        = value,
                                       detect_lists = detect_lists,
                                       delimiter    = list_delimiter)
                           for value in line.split(field_delimiter)]

                 rows.append(OrderedDict(zip(keys, values)))


        return {u'Headings'    : keys,
                u'Description' : descriptions if descriptions else [u''],
                u'Data'        : rows}

    try:
        return extract_list(codecs.open(text_table, u'r', encoding = u'utf8'))
    except IOError:
        pass
    return extract_list(text_table.splitlines())


def text_table_to_dictionary(text_table,
                             field_delimiter = u'|',
                             separator_line = u'-',
                             separator_delimiter = u'+',
                             detect_lists   = False,
                             list_delimiter = u','):
    """
    Creates a Python dictionary from a text based table.
    e.g.
    a file or string containing:

        Name    | Device_ID | Bouquet | Sub-Bouquet
        --------+-----------+---------+------------
        @ Description 1.
        # Comment 1
        htx     | 34939046  |   4101  |      1
        kd1     | 34939007  |   4101  |      1
        @ Description 2.

    yields dictionary like this:

        {u'Description': [u'Description 1. Description 2.],
         u'Headings': [u'u'Bouquet',
                       u'Device_ID',
                       u'Name',
                       u'Sub-Bouquet'],
         u'Data' : {u'htx': {u'Bouquet'    : u'4101',
                             u'Device_ID'  : u'34939046',
                             u'Name'       : u'htx',
                             u'Sub-Bouquet': u'1'},
                    u'kd1': {u'Bouquet'    : u'4101',
                             u'Device_ID'  : u'34939007',
                             u'Name'       : u'kd1',
                             u'Sub-Bouquet': u'1'}}}

    if the source is just two columns,
    assume key:value pairs.  The column header names
    are not considered significant in this case.

        Key | Value
        ----+----------
        ABC | 34939046
        DEF | 34939007

    yields dictionary like this:

        {u'ABC': u'34939046',
         u'DEF': u'34939007',
        }

    :param text_table:
    :return: DICT
    """

    as_list = text_table_to_list(text_table          = text_table,
                                 field_delimiter     = field_delimiter     ,
                                 separator_line      = separator_line      ,
                                 separator_delimiter = separator_delimiter ,
                                 detect_lists        = detect_lists        ,
                                 list_delimiter      = list_delimiter      )

    descriptions = as_list[u'Description']
    keys = as_list[u'Headings']
    data = as_list[u'Data']
    key_field = keys[0]
    value_field = keys[1] if len(keys) > 1 else None

    lookup = OrderedDict()

    for datum in data:
        # use key value pairs of a dictionary containing a list of key value pairs
        # otherwise use key + all data
        lookup[datum[key_field]] = datum[value_field] if len(keys) == 2 else datum

    return {u'Headings'    : keys,
            u'Description' : descriptions,
            u'Data'        : lookup}


def dictionary_to_list(dictionary):
    return [dictionary[key] for key in dictionary if key != u'Description']
