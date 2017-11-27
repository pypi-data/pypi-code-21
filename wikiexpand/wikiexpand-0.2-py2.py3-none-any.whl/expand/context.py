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

    SUBPAGE_SEPARATOR = "/"

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

    def has_subpages(self, namespace):
        """
        :rtype: True if namespace allows subpages
        """
        raise NotImplementedError()

    def canonical_title(self, title):
        """
        :rtype: canonical title of a page

        Template:name -> Plantilla:name
        name -> name
        name:name -> name:name
        """
        namespace, name = self.split_title(title, normalize=True)
        if namespace:
            return tools.join_title(namespace, name)
        else:
            return name

    def clean_title(self, title, **kwargs):
        """
        :rtype: page title without the namespace

        Template:name -> name
        name -> name
        name:name -> name:name
        """
        namespace, name = self.split_title(title)
        return name

    def split_title(self, title, normalize=False):
        """
        :rtype: tuple (namespace, pagename)
        """
        title = tools.normalize_title(title)
        ns, name = tools.title_parts(title)
        namespace = self.namespace_name(ns)
        if namespace:
            if normalize:
                ns = namespace
            return ns, name
        else:
            return "", title

    def talkpagename(self, title):
        """
        :rtype: talk pagename associated to the page
        """
        ns, clean_title = self.split_title(title)
        talk_ns = self.talkspace(ns)
        return tools.join_title(talk_ns, clean_title)

    def articlepagename(self, title):
        """
        :rtype: article pagename associated to the page
        """
        ns, clean_title = self.split_title(title)
        article_ns = self.articlespace(ns)
        return tools.join_title(article_ns, clean_title)


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
