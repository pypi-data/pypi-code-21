#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import OrderedDict
import logging
import inspect
from docutils.core import publish_parts

logger = logging.getLogger(__name__)


class MutaPropError(Exception):
    pass


class BiDict(OrderedDict):
    """
    Bidirectional dictionary for handling both getters and setters of
    MutaProperties with selects.
    Copied from http://stackoverflow.com/a/21894086 and adopted for Python3.
    """
    def __init__(self, *args, **kwargs):
        self.inverse = OrderedDict({})
        super().__init__(*args, **kwargs)
        # for key, value in self.items():
        #     self.inverse.setdefault(value,[]).append(key)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.inverse.setdefault(value,[]).append(key)

    def __delitem__(self, key):
        self.inverse.setdefault(self[key],[]).remove(key)
        if self[key] in self.inverse and not self.inverse[self[key]]:
            del self.inverse[self[key]]
        super().__delitem__(key)

    def get_map_list(self):
        return [(select, value) for select, value in self.items()]


def rest_to_html(docstring):
    """ Converts reSTructured text from docstrings to HTML.

    As it uses quite strange docutils implementations, it adds some unnecessary
    clutter to the HTML <div class="document"> etc.

    """
    if docstring:
        return publish_parts(inspect.cleandoc(docstring),
                             writer_name='html')['html_body']
    else:
        return None
