#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import

from .tools import strip

import mwparserfromhell as mw


def transclude(value):
    """
    Get the wikicode usable when transcluded in another page.
    """
    tree = mw.parse(value)
    alt = []

    for node in tree.filter_tags(tree.RECURSE_OTHERS):
        tag_name = strip(node.tag).lower()
        if tag_name == "noinclude":
            tree.remove(node)
        elif tag_name == "onlyinclude":
            alt.append(transclude(node.contents))
        else:
            transclude(node.contents)

    for node in tree.filter_comments(tree.RECURSE_OTHERS):
        tree.remove(node)

    if alt:
        return mw.wikicode.Wikicode(alt)
    return tree


class TemplateStore(object):
    """
    Interface for a template store. It provides to store and retrieve
    a template body.
    """

    def __init__(self, *args, **kwargs):
        self._callable_templates = {}

    def _set(self, key, value):
        raise NotImplementedError()

    def _get(self, key):
        raise NotImplementedError()

    def __setitem__(self, key, value):
        data = transclude(value)

        self._set(key, strip(data))

    def __getitem__(self, key):
        return self._get(key)

    @property
    def callable_templates(self):
        """
        Templates that are not stored as text, but rendered by a function.

        Useful for replacing Lua modules or troublesome templates.

        Arguments for a callable template:

        * template parameters (dict-like)
        * expander function: function which allows to expand wikicode in the
            running expansion context
        * page context
        * frame arguments (dict-like) -- arguments existing in the environment
            this function was called (see Lua modules doc for further info)
        """
        return self._callable_templates

    def parse(self, key, skip_style_tags=False):
        return mw.parse(self[key], skip_style_tags=skip_style_tags)


class TemplateDict(TemplateStore):
    """
    A simple template store implemented by using a dictionary
    """

    def __init__(self, *args, **kwargs):
        super(TemplateDict, self).__init__(*args, **kwargs)
        self._data = {}
        self._set = self._data.__setitem__
        self._get = self._data.__getitem__
