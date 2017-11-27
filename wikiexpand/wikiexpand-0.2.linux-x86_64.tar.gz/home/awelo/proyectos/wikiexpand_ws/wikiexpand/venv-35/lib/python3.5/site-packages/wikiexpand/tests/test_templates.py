#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import unicode_literals
from __future__ import print_function

from wikiexpand.expand.templates import TemplateDict


def check_set(text, ref):
    T = TemplateDict()
    T["a"] = text

    assert ref == T["a"]


def test_set():
    DATA = [
        ("hola", "hola"),
        ("{{{1|x}}}<noinclude>{{a|1={{{2}}}}}</noinclude>al{{{3|g}}}",
         "{{{1|x}}}al{{{3|g}}}"),
        ("{{{1|x}}}<NOINCLUDE>{{a|1={{{2}}}}}</noinclude>al{{{3|g}}}",
         "{{{1|x}}}al{{{3|g}}}"),
        ("bla bla {{a|ea ea}} <includeonly>[[Categoría:Cosas]]</includeonly>",
         "bla bla {{a|ea ea}} <includeonly>[[Categoría:Cosas]]</includeonly>"),
        ("<onlyinclude>bla bla {{a|ea ea}} </onlyinclude>[[Categoría:Cosas]]",
         "bla bla {{a|ea ea}}"),
        ("<onlyinclude>esto</onlyinclude> esto no <onlyinclude>, esto también</onlyinclude>",
         "esto, esto también"),
    ]

    for txt, ref in DATA:
        yield check_set, txt, ref
