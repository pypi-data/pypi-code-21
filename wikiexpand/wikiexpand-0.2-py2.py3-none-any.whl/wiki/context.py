#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import

import weakref
from functools import partial

import pywikibot as pw
import mwparserfromhell as mw
from ..compat import p3_str
from ..expand import context
from ..expand import tools


BAD_PARSE = "<>'[]"


class Wiki(context.SiteContext):
    """
    SiteContext implementation using PyWikibot
    """

    def __init__(
            self,
            pw_site=None,
            encodings=("utf-8", "latin1"),
            *args, **kwargs):
        super(Wiki, self).__init__(*args, **kwargs)
        if not pw_site:
            pw_site = pw.Site()
        self.pw_site = pw_site
        self.encodings = encodings

        try:
            self._pw_lookup_name = pw_site.namespaces.lookup_name
        except AttributeError:
            self._pw_lookup_name = lambda x: pw.site.Namespace.lookup_name(
                x,
                self.pw_site.namespaces
            )

    def namespace_normalize(self, name_or_code):
        try:
            value = int(name_or_code)
            return self.pw_site.namespaces[value].custom_name
        except ValueError:
            return self._pw_lookup_name(name_or_code).custom_name
            #value = name_or_code
        #return self.pw_site.namespace(value)

    def namespace_name(self, namespace, default=""):
        try:
            ns = self.pw_site.namespace(namespace)
        except KeyError:
            ns = default
        return ns

    def has_subpages(self, namespace):
        try:
            ns = self._pw_lookup_name(namespace)
            return ns.subpages
        except KeyError:
            return False

    def namespace_code(self, title):
        if ":" in title:
            return 0
        ns = self._pw_lookup_name(title)
        return ns.id if ns else 0

    def page_context(self, title, *args, **kwargs):
        return WikiPage(weakref.proxy(self), title, *args, **kwargs)

    def page_exists(self, title):
        return self.pw_page(title).exists()

    def pw_page(self, title):
        return pw.Page(self.pw_site, title)

    def talkspace(self, namespace):
        ns = self._pw_lookup_name(namespace)
        if ns is None:
            ns = self._pw_lookup_name("")
        canon = ns.canonical_name
        if (canon == "Talk") or canon.endswith(" talk"):
            return ns.custom_name

        if canon == "":
            talk = "Talk"
        else:
            talk = canon + " talk"

        out = self._pw_lookup_name(talk)
        return out.custom_name

    def articlespace(self, namespace):
        ns = self._pw_lookup_name(namespace)
        canon = ns.canonical_name

        article = None

        if canon == "Talk":
            article = ""
        elif canon.endswith(" talk"):
            # "bla bla talk" 5 = len(" talk")
            article = canon[:-5]

        if article is None:
            return ns.custom_name

        out = self._pw_lookup_name(article)
        return out.custom_name

    def fullurl(self, title):
        return self.pw_page(title).full_url()

    def clean_text(self, text):
        """
        remove categories and language links
        """
        text = pw.textlib.removeDisabledParts(text)
        text = pw.textlib.removeCategoryLinks(text)
        text = pw.textlib.removeLanguageLinks(text)
        text = pw.textlib.removeHTMLParts(text)
        text = pw.textlib.replace_links(
            text,
            lambda *x, **y: False,
            site=self.pw_site
        )
        return text

    def headings(self, text, levels=None, clean_text=True):
        """
        generator of text headings (level, text)
        """
        gen = tools.headings(text, levels=levels)
        if clean_text:
            for lvl, text in gen:
                if any(c in text for c in BAD_PARSE):
                    text = self.clean_text(text)
                yield lvl, text
        else:
            for item in gen:
                yield item

    def clean_title(self, title, external=False, **kwargs):
        if external:
            # use pywikibot
            p = self.pw_page(title)
            try:
                return p.title(withNamespace=False)
            except pw.InvalidTitle:
                return super(Wiki, self).clean_title(
                    title,
                    external=external,
                    **kwargs
                )
        else:
            return super(Wiki, self).clean_title(
                title,
                external=external, **kwargs
            )

    def transcluded_templates(self, text):
        templates = []
        for node in mw.parse(text).ifilter_templates():
            title = p3_str(node.name.strip_code())
            if title and not title.startswith("#"):
                try:
                    page = pw.Page(self.pw_site, title, ns=10)
                    canonical_title = page.title()
                    if (canonical_title.count(":") <= 1) and \
                            (canonical_title not in templates):
                                templates.append(canonical_title)
                                yield canonical_title
                except pw.InvalidTitle:
                    pass


def _as_page_link(site, encodings, link):
    try:
        return link if not site.isInterwikiLink(link) else None
    except UnicodeDecodeError:
        link = pw.url2unicode(link, encodings=encodings)
        return link if not site.isInterwikiLink(link) else None


class WikiPage(context.PageContext):
    """
    PageContext implementation using PyWikibot
    """

    def __init__(self, site, title, *args, **kwargs):
        super(WikiPage, self).__init__(*args, **kwargs)
        self._site = site
        self._title = title
        self._as_page_link = partial(_as_page_link, site.pw_site, site.encodings)

    def title(self):
        return self._title

    def clean_title(self, external=False):
        return self.site_context().clean_title(self.title(), external=external)

    def headings(self, text, levels=None, clean_text=True):
        return self.site_context().headings(text, levels=levels, clean_text=clean_text)

    def wikilinks(self, text, clean_text=True):
        """
        generator of links
        """
        if clean_text:
            text = self.clean_text(text)

        results = set()

        pw_site = self.site_context().pw_site
        #encodings = self.site_context().encodings

        for link in tools.wikilinks(text):
            link = p3_str(link)
            if link[:1] == "#":
                # self reference
                link = self._title + link

            if not link or link in results:
                continue

            results.add(link)

            link = self._as_page_link(link)
            if link is not None:
                try:
                    pw_l = pw.Link(link, source=pw_site)
                    l_name = pw_l.title
                    try:
                        l_ns = pw_l.namespace.id
                    except AttributeError:
                        l_ns = pw_l.namespace

                    yield l_name, l_ns, pw_l.section
                except pw.InvalidTitle:
                    continue


class SetWiki(Wiki):
    """
    A PyWikibot SiteContext implementation using `set` to resolve page existence.
    """

    def __init__(self, pages, *args, **kwargs):
        super(SetWiki, self).__init__(*args, **kwargs)
        self._pages = pages

    def page_exists(self, title):
        return self.canonical_title(title) in self._pages
