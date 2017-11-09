# -*- coding: utf-8 -*-

import logging_helper
from dominate import tags
from conversionutil.convert import CONVERTER, convert
from fdutil.type_check import is_list_or_dictionary
from .constants import Justify
from .helpers import (escape_jira_markup,
                      is_a_table)

logging = logging_helper.setup_logging()


class Cell(object):

    def __init__(self,
                 value=u'',
                 href=None,
                 classes=None,
                 tooltip=None,
                 conversion=None):

        """
        A Cell is a container that is used by Row and Table in order to
        correctly format a value for display as HTML, text or for JIRA.

        The source value can be modified with a supplied conversion.

        :param value:       Contents of the cell. Can be a string,
                            a list, a Cell or a Table.
        :param href:        sets href for cell (makes whole cell clickable)
        :param tooltip:     Use instead of title attribute of an anchor.
                            This should have all the HTML required for the
                            toolip. If it's added inside an anchor, you
                            can set the class of the anchor (e.g. class="tooltip")
                            inside the tags parameter.
        :param conversion:  Conversion to apply to the value
        """

        if isinstance(value, Cell):
            if conversion is None:
                conversion = value.conversion

            value = value.raw_value

        if callable(conversion):
            conversion = {CONVERTER: conversion}

        self._value = value
        self._href = href
        self.classes = classes if classes is not None else []
        self.conversion = conversion
        self.tooltip = tooltip

    @property
    def value(self):
        try:
            value = (self.raw_value.text()
                     if getattr(self.raw_value, u'text', None) is not None
                     else self.raw_value)

            converted_value = (value
                               if not self.conversion
                               else convert(value=value,
                                            **self.conversion))

        except Exception as e:
            logging.warning(e)
            converted_value = self.raw_value

        return self._split_cell(converted_value)

    @value.setter
    def value(self,
              value):
        self.raw_value = value

    @property
    def raw_value(self):
        return self._value

    @raw_value.setter
    def raw_value(self,
                  value):
        self._value = value

    @property
    def href(self):
        return self._href

    @href.setter
    def href(self,
             value):
        self._href = value

    def __eq__(self, other):
        if isinstance(other, Cell):
            return self.value == other.value

        return self.value == other

    def __len__(self):
        return len(self.value)

    def __getitem__(self, item):
        try:
            return self.value[item]

        except IndexError:
            return u''

    @property
    def width(self):

        """ Get the Cell's text width (including padding) """

        return max([len(line) + 2 for line in self.value])

    @staticmethod
    def _split_cell(value,
                    level=1):

        """
        Takes cell and returns a list of strings.
        The cell source is strings or nested lists,
        A list of substrings is returned.

        e.g. cell is ['first\nsecond',['third','fourth',['fifth','sixth']]]

        is returned as ['first',
                        'second',
                        'third',
                        'fourth',
                        'fifth',
                        'sixth']

        :param value: a string or a list of strings
        :return: a list of strings
        """

        # the replace('\r','') below is because printing strings the have \r
        # can result in some odd behaviour that messes up tables:
        # >>> print 'abc\r123'
        # 123

        if is_a_table(value):
            return value

        elif is_list_or_dictionary(value):
            value = u'\n'.join([u'\n'.join(Cell._split_cell(part, level + 1))
                                for part in value])

        else:
            value = unicode(value).replace(u'\r', u'')

        return [part for part in value.split(u'\n')]

    @staticmethod
    def __jira_excluded_href(href):
        exclusions = (u'file://',)

        if href:
            if u'://' in href:
                for exclusion in exclusions:
                    if href.startswith(exclusion):
                        return True

                return False

        return True

    def html(self,
             **kwargs):

        """ Formats the value as an HTML element """

        if self.tooltip:
            _cell_div = tags.div(data_toggle="tooltip",
                                 data_placement="bottom",
                                 title=self.tooltip)

        else:
            _cell_div = tags.div()

        if self.classes:
            _cell_div[u'class'] = u' '.join(self.classes)

        # If an href is set wrap the div in the href to make the entire cell a link
        _cell = _cell_div if self.href is None else tags.a(_cell_div,
                                                           href=self.href)

        with _cell_div:
            if getattr(self.raw_value, u'html', False):
                # Class is probably Table, Row or Cell
                self.raw_value.html(**kwargs)

            elif isinstance(self.raw_value, tags.html_tag):
                # Class is a dominate tag
                _cell_div.add(self.raw_value)

            else:
                # cover everything else
                for line in self.value:
                    tags.div(line)

        return _cell

    def jira(self):

        # TODO: need to properly account for dominate tags
        if is_a_table(self.raw_value):
            value = u'{{panel:borderStyle=none}}{subtable}{{panel}}'.format(subtable=unicode(self.raw_value.jira()))

        else:
            value = u'\n'.join(self.text())

        # add href if it exists and it's not a file reference
        if not self.__jira_excluded_href(self.href):
            value = u'\n'.join([u'[{line}|{href}]'.format(line=escape_jira_markup(line),
                                                          href=self.href)
                                for line in value.splitlines()])

        return value

    def text(self,
             width=None,
             justification=Justify.left):

        # TODO: need to properly account for dominate tags
        if width is None:
            width = self.width

        # Remove width to allow for padding
        width = width - 2

        lines = []

        for line in self.value:
            lines.append(u'{pad}{string:'
                         u'{pad}{justification}{width}}{pad}'.format(string=line,
                                                                     pad=u' ',
                                                                     width=width,
                                                                     justification=justification))

        return lines

    def csv(self,
            delimiter=u','):

        field = u' '.join(self.text())

        if delimiter in field:
            field = u'"{field}"'.format(field=field.replace(u'"', u'""'))

        return field


def make_uri_cell(value):
    return Cell(value=value,
                href=value)
