#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import

from ..compat import p3_str, p3_chr

import re
import mwparserfromhell as mw
from collections import defaultdict


BLANK_CHAR = " \n\r\t"
NBSP = p3_chr(160)
R_URL_ENCODING = re.compile(r'(%)(?=[0-9A-F]{2})')
R_MULTI_SPACE = re.compile(r'\s+')


try:
    from html import unescape as _unescape

    def html_unescape(x):
        return _unescape(x)
except ImportError:
    from HTMLParser import HTMLParser
    __HTML_PARSER = HTMLParser()

    def html_unescape(x):
        return __HTML_PARSER.unescape(x)


try:
    from urllib.parse import quote
except ImportError:
    from urllib2 import quote as _quote

    def quote(x):
        return _quote(x.encode("utf-8"))


def parse(*args):
    """
    Convert arguments to Wikicode
    """
    #return mw.parse(*args, skip_style_tags=True)
    return mw.parse(*args, skip_style_tags=False)


def query_encode(x):
    """
    Encode the text using MediaWiki url encoding
    """
    return quote(x).replace("%20", "+")


def title_encode(x):
    """
    Encode a title using MediaWiki title encoding
    """
    return quote(x).replace("%20", "_").replace("%3A", ":")


def anchor_encode(x):
    return R_URL_ENCODING.sub(".", title_encode(x))


def normalize_title(x):
    x = html_unescape(x.strip())
    return R_MULTI_SPACE.sub(" ", x.replace("_", " "))


def as_wikicode(node):
    """
    wrap a node into a wikicode object
    """
    return mw.wikicode.Wikicode(mw.smart_list.SmartList([node]))


def reindex_params(params, delta):
    """
    Add delta to the unnamed parameters
    """
    for prm in params:
        if not prm.showkey:
            #try:
                #index = int(p3_str(prm.name))
                #prm.name = str2wikicode(index + delta)
            #except ValueError:
                #pass
            key = p3_str(prm.name)
            index = int(key) if p3_str.isdigit(key) else None
            if index:
                prm.name = str2wikicode(index + delta)
    return params


def strip(x):
    """
    strip and return a string
    """
    return p3_str(x).strip(BLANK_CHAR)


def lstrip_code(tree):
    """
    lstrip x and return as wikicode. Previous wikicode nodes are preserved.
    """
    # left trim
    for node in list(tree.nodes):
        if isinstance(node, mw.nodes.Text):
            node.value = node.value.lstrip(BLANK_CHAR)

            if not node.value:
                tree.nodes.pop(0)
                continue
        break

    return tree


def rstrip_code(tree):
    """
    rstrip x and return as wikicode. Previous wikicode nodes are preserved.
    """
    # right trim
    for node in reversed(list(tree.nodes)):
        if isinstance(node, mw.nodes.Text):
            node.value = node.value.rstrip(BLANK_CHAR)

            if not node.value:
                tree.nodes.pop()
                continue
        break

    return tree


def strip_code(x):
    """
    Strip blanks from string or wikicode
    and return wikicode
    """
    return rstrip_code(lstrip_code(x))


def str2wikicode(x):
    """
    convert str x into Wikicode, without parsing
    """
    return as_wikicode(mw.nodes.Text(p3_str(x)))


def title_parts(title):
    """
    split a mediawiki title into (namespace, clean title)
    """
    parts = title.split(":", 1)
    if len(parts) > 1:
        return tuple(parts)
    return "", title


def join_title(namespace, title):
    """
    prefix a namespace to a page title
    """
    if namespace:
        return "%s:%s" % (namespace, title)
    return title


def clean_title(title):
    """
    get a mediawiki title with no namespace prefix
    """
    return title_parts(title)[1]


def redirect_target(text):
    """
    get a redirect target from wikicode
    """
    tree = parse(text)

    link = next(tree.ifilter_wikilinks(text))

    return strip(link.title)


def clean_text_from_wikicode(wikicode):
    """
    """
    tree = mw.parse(wikicode)

    for link in tree.filter_wikilinks(tree.RECURSE_OTHERS):
        if link.text:
            tree.replace(link, strip_code(link.text))
        else:
            tree.remove(link)

    return strip(tree.strip_code()).replace(NBSP, " ")


def headings(text, levels=None):
    """
    get the headings from text
    """
    count = defaultdict(lambda: 0)

    tree = mw.parse(text)

    for heading in tree.ifilter_headings(tree.RECURSE_OTHERS):
        if not levels or heading.level in levels:
            h = clean_text_from_wikicode(heading.title)
            count[h] += 1
            suffix = count[h]
            if suffix > 1:
                h += " %d" % suffix
            yield heading.level, h


def wikilinks(text):
    """
    Return a generator providing the wikilinks found in the text
    """
    tree = parse(text)

    for link in tree.ifilter_wikilinks(tree.RECURSE_OTHERS):
        yield strip(link.title)


class DefaultList(object):

    def __init__(self, a_list, default="", transform=None):
        """
        """
        self.entity = a_list
        self.default = default
        self.transform_f = transform

    def __getitem__(self, index):
        return self.get(index, self.default)

    def get(self, index, default):
        """
        get item at index, or default value if no item is found
        """
        try:
            return self.entity[index]
        except IndexError:
            return default

    def transform(self, index, transform=None):
        transform = transform or self.transform_f
        value = self[index]
        if transform:
            return transform(value)
        return value
