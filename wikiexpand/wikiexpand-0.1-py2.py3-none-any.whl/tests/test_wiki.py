#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import unicode_literals
from __future__ import print_function

import pywikibot as pw
from wikiexpand.wiki import context

from nose.tools import assert_list_equal


class TestWiki(object):

    def setUp(self):
        pw_site = pw.Site(code="es", fam="wiktionary")
        self.w = context.Wiki(pw_site)

    def test_namespace_normalize(self):
        data = [
            (0, ""),
            ("", ""),
            (10, "Plantilla"),
            ("Plantilla", "Plantilla"),
            ("Template", "Plantilla")
        ]
        for k, v in data:
            yield self.check_namespace_normalize, k, v

    def check_namespace_normalize(self, k, expected):
        res = self.w.namespace_normalize(k)
        assert expected == res

    def test_namespace_code(self):
        data = [
            ("Plantilla", 10),
            ("Template", 10),
            ("hola", 0),
            ("algo:asi", 0),
        ]
        for k, v, in data:
            yield self.check_namespace_code, k, v

    def check_namespace_code(self, k, expected):
        res = self.w.namespace_code(k)
        assert expected == res


class TestWikiPage(object):

    def setUp(self):
        pw_site = pw.Site(code="es", fam="wiktionary")
        self.w = context.Wiki(pw_site)

    def test_title(self):
        data = [
            "hola",
            "adios",
            "Plantilla:algo",
            "Template:algo"
        ]

        for k in data:
            yield self.check_title, k

    def check_title(self, k):
        p = self.w.page_context(k)
        res = p.title()
        assert k == res

    def test_clean_title(self):
        data = [
            ("hola", "hola"),
            ("adios", "adios"),
            ("Plantilla:algo", "algo"),
            ("Template:algo", "algo"),
            ("Template:algo/doc", "algo/doc")
        ]

        for k, v in data:
            yield self.check_clean_title, k, v

    def test_clean_title_external(self):
        data = [
            ("hola", "hola"),
            ("adios", "adios"),
            ("Plantilla:algo", "algo"),
            ("Template:algo", "algo"),
            ("Template:algo/doc", "algo/doc")
        ]

        for k, v in data:
            yield self.check_clean_title, k, v, True

    def check_clean_title(self, k, expected, external=False):
        p = self.w.page_context(k, external=external)
        res = p.clean_title()
        assert expected == res

    def test_transcluded_templates(self):
        txt = """{{ uno }} {{dos}} {{uno}} {{#if:1|2|3}} {{tres<!--c-->}}
                {{ seis<!--c--> | {{siete}}<!--c--> }}
                {{NAMESPACE:blas}} {{Plantilla:cuatro}} {{Template:cinco}}"""

        ref = ["Plantilla:uno",
               "Plantilla:dos",
               "Plantilla:tres",
               "Plantilla:seis",
               "Plantilla:siete",
               "Plantilla:cuatro",
               "Plantilla:cinco"]

        out = list(self.w.transcluded_templates(txt))

        assert_list_equal(ref, out)
