#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division

from .magic_words import MagicWord
from .parser_functions import ParserFunction
from . import tools

import weakref


class SiteContext(object):
    """
    A SiteContext provide information about a wiki site
    """

    def page_context(self, title, *args, **kwargs):
        """
        :param title: page title

        :rtype: :class:`wikiexpand.expand.PageContext`
        """
        raise NotImplementedError()

    def page_exists(self, title):
        """
        Check whether the page is a blue or a red link.

        :rtype: :class:`bool` `True` if a page named as `title` is defined in the site.
        """
        raise NotImplementedError()

    def namespace_normalize(self, name_or_code):
        """
        :param name_or_code: namespace name or namespace numerical code.

        :rtype: :class:`str` canonical name of the namespace
        """
        raise NotImplementedError()

    def namespace_name(self, name, default=""):
        """
        :rtype: namespace name of the page
        """
        raise NotImplementedError()

    def articlespace(self, namespace):
        """
        :rtype: article namespace associated to the given namespace
        """
        raise NotImplementedError()

    def talkspace(self, namespace):
        """
        :rtype: talk namespace associated to the given namespace
        """
        raise NotImplementedError()

    def fullurl(self, title):
        """
        :rtype: full url of the page named as `title`
        """
        raise NotImplementedError()

    def namespace_code(self, title):
        """
        :rtype: namespace numerical code of the page
        """
        raise NotImplementedError()

    def canonical_title(self, title):
        """
        :rtype: canonical title of a page
        """
        ns, name = tools.title_parts(title)
        ns = self.namespace_name(ns)
        if ns:
            return ":".join((ns, name))
        else:
            return title

    def clean_title(self, title, **kwargs):
        """
        :rtype: page title without the namespace
        """
        ns, name = tools.title_parts(title)
        namespace = self.namespace_name(ns)
        if namespace:
            return name
        else:
            if ns:
                return ":".join((ns, name))
            else:
                return title

    def talkpagename(self, title):
        """
        :rtype: talk pagename associated to the page
        """
        clean_title = self.clean_title(title)
        ns, _ = tools.title_parts(title)
        talk_ns = self.talkspace(ns)
        return "%s:%s" % (talk_ns, clean_title)


class PageContext(object):
    """
    A PageContext provide information about a wiki site and a wiki page.
    """

    def __init__(self, *args, **kwargs):
        self._site = None
        self.parser_functions = ParserFunction(weakref.proxy(self))
        self.magic_words = MagicWord(weakref.proxy(self))

    def site_context(self):
        return self._site

    def title(self):
        return None

    def clean_title(self):
        return None
