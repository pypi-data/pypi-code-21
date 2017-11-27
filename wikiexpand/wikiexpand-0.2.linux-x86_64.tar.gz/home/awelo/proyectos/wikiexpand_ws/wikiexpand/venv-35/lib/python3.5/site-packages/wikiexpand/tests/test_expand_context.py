#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import unicode_literals
from __future__ import print_function

#from nose.plugins.skip import SkipTest

from datetime import datetime

#import mwparserfromhell as mw

from wikiexpand.expand import ExpansionContext
from wikiexpand.expand.templates import TemplateDict
from wikiexpand.compat import p3_str
from wikiexpand.expand import tools
from wikiexpand.wiki.context import SetWiki
import pywikibot as pw

TEMPLATES = TemplateDict()
TEMPLATES["hola"] = "[[{{{1|{{PAGENAME}}}}}#{{TALKSPACE}}]]"
TEMPLATES["adios"] = "== {{{1|X}}} =="
TEMPLATES["kaixo"] = "{{#if:{{{1|}}}|{{{2}}}|{{{3}}} }}"
TEMPLATES["hej"] = '<span class="{{{2|A}}}">{{{1|{{PAGENAME}}}}}</span>'
TEMPLATES["privet"] = "{{adios|1={{{1|{{PAGENAME}}}}}}}"

PAGES = set([
    "hola",
    "adios",
    "eo",
    "ay",
    "Plantilla:sección"])

CONTEXT = SetWiki(pages=PAGES, pw_site=pw.Site(code="es", fam="wiktionary"))


def check_expand(txt, ref, page="API"):
    p_context = CONTEXT.page_context(page)
    sc = ExpansionContext(templates=TEMPLATES, page_context=p_context)

    expanded = p3_str(sc.expand(txt))

    print("TXT: '%s'" % txt)
    print("REF: '%s'" % ref)
    print("EXP: '%s'" % expanded)

    assert(expanded == ref)


def test_pf_ns():
    DATA = [
        ("{{ns:0}}", ""),
        ("{{ns: 0 }}", ""),
        ("{{ns:}}", ""),
        ("{{ns:Template}}", "Plantilla"),
        ("{{ns: Template }}", "Plantilla"),
        ("{{ns:template}}", "Plantilla"),
        ("{{ns:10}}", "Plantilla"),
    ]

    for txt, ref in DATA:
        yield check_expand, txt, ref


def test_pf_sharp_rel2abs():
    DATA = [
        ("{{#rel2abs: ./quok}}", "API/quok"),
        ("{{#rel2abs: /quok}}", "API/quok"),
        ("{{#rel2abs: quok}}", "quok"),
    ]

    for txt, ref in DATA:
        yield check_expand, txt, ref


def test_prefixed_template():
    DATA = [
        ("{{adios}}", "== X =="),
        ("{{Template:adios}}", "== X =="),
        ("{{Plantilla:adios}}", "== X =="),
    ]

    for txt, ref in DATA:
        yield check_expand, txt, ref


def test_pf_sharp_ifexist():
    DATA = [
        ("{{#ifexist:hola|yes|no}}", "yes"),
        ("{{#ifexist: hola | yes | no }}", "yes"),
        ("{{#ifexist: zzzz | yes | no }}", "no"),
        ("{{#ifexist: Plantilla:sección | yes | no }}", "yes"),
        ("{{#ifexist: Template:sección | yes | no }}", "yes"),
        ("{{#ifexist: 10:sección | yes | no }}", "no"),
        ("{{#ifexist: Plantilla:zzzz | yes | no }}", "no"),
    ]

    for txt, ref in DATA:
        yield check_expand, txt, ref


def test_pf_namespace():
    DATA = [
        ("{{NAMESPACE:hola}}", ""),
        ("{{NAMESPACE:Template:sección}}", "Plantilla"),
        ("{{NAMESPACE:Plantilla:sección}}", "Plantilla"),
        ("{{NAMESPACE: Plantilla:sección }}", "Plantilla"),
        ("{{NAMESPACE: hola:adios }}", ""),
        ("{{NAMESPACE:Talk:olá }}", "Discusión"),
    ]

    for txt, ref in DATA:
        yield check_expand, txt, ref


def test_pf_namespacee():
    DATA = [
        ("{{NAMESPACEE:hola}}", ""),
        ("{{NAMESPACEE:Template:sección}}", "Plantilla"),
        ("{{NAMESPACEE:Plantilla:sección}}", "Plantilla"),
        ("{{NAMESPACEE: Plantilla:sección }}", "Plantilla"),
        ("{{NAMESPACEE: hola:adios }}", ""),
        ("{{NAMESPACEE:Talk:olá }}", "Discusi%C3%B3n"),
    ]

    for txt, ref in DATA:
        yield check_expand, txt, ref


def test_mw_namespace():
    DATA = [
        ("hola", ""),
        ("Plantilla:sección", "Plantilla"),
        ("Template:sección", "Plantilla"),
        ("Template talk:sección", "Plantilla discusión"),
    ]

    for page, ref in DATA:
        yield check_expand, "{{NAMESPACE}}", ref, page


def test_mw_namespacee():
    DATA = [
        ("hola", ""),
        ("Plantilla:sección", "Plantilla"),
        ("Template:sección", "Plantilla"),
        ("Template talk:sección", "Plantilla_discusi%C3%B3n"),
    ]

    for page, ref in DATA:
        yield check_expand, "{{NAMESPACEE}}", ref, page


def test_pf_pagename():
    DATA = [
        ("{{PAGENAME:hola}}", "hola"),
        ("{{PAGENAME:Plantilla:sección}}", "sección"),
        ("{{PAGENAME:Template:sección}}", "sección"),
        ("{{PAGENAME: Template:sección }}", "sección"),
        ("{{PAGENAME:Template talk:sección}}", "sección"),
        ("{{PAGENAME:hola:adios}}", "hola:adios"),
        ("{{PAGENAME: hola:adios }}", "hola:adios"),
        ("{{PAGENAME:media}}", "media"),
        ("{{PAGENAME:holá_adios\"}}", "holá adios\""),
        ("{{PAGENAME:holá  adios&}}", "holá adios&"),
        ("{{PAGENAME:holá  adios'}}", "holá adios'"),
    ]

    for txt, ref in DATA:
        yield check_expand, txt, ref


def test_pf_pagenamee():
    DATA = [
        ("{{PAGENAMEE:hola}}", "hola"),
        ("{{PAGENAMEE:Plantilla:sección}}", "secci%C3%B3n"),
        ("{{PAGENAMEE:Template:esta sección}}", "esta_secci%C3%B3n"),
        ("{{PAGENAMEE:holá_adios\"}}", "hol%C3%A1_adios%22"),
        ("{{PAGENAMEE:holá  adios&}}", "hol%C3%A1_adios%26"),
    ]

    for txt, ref in DATA:
        yield check_expand, txt, ref


def test_mw_pagename():
    DATA = [
        ("hola", "hola"),
        ("Plantilla:sección", "sección"),
        ("Template:sección", "sección"),
        ("Template talk:sección", "sección"),
        ("hola:adios", "hola:adios"),
        ("holá_adios\"", "holá adios\""),
        ("holá  adios&", "holá adios&"),
        ("holá  adios'", "holá adios'"),
    ]

    for page, ref in DATA:
        yield check_expand, "{{PAGENAME}}", ref, page


def test_mw_pagenamee():
    DATA = [
        ("hola", "hola"),
        ("Plantilla:sección", "secci%C3%B3n"),
        ("Template:esta sección", "esta_secci%C3%B3n"),
        ("Template talk:sección", "secci%C3%B3n"),
        ("hola:adios", "hola:adios"),
        ("holá_adios\"", "hol%C3%A1_adios%22"),
        ("holá  adios&", "hol%C3%A1_adios%26"),
    ]

    for page, ref in DATA:
        yield check_expand, "{{PAGENAMEE}}", ref, page


def test_pf_fullpagename():
    DATA = [
        ("{{FULLPAGENAME:hola}}", "hola"),
        ("{{FULLPAGENAME:Plantilla:sección}}", "Plantilla:sección"),
        ("{{FULLPAGENAME:Template:sección}}", "Plantilla:sección"),
        ("{{FULLPAGENAME: Template:sección }}", "Plantilla:sección"),
        ("{{FULLPAGENAME:Template talk:sección}}", "Plantilla discusión:sección"),
        ("{{FULLPAGENAME:hola:adios}}", "hola:adios"),
        ("{{FULLPAGENAME: hola:adios }}", "hola:adios"),
        ("{{FULLPAGENAME:media}}", "media"),
        ("{{FULLPAGENAME:holá_adios\"}}", "holá adios\""),
        ("{{FULLPAGENAME:holá  adios&}}", "holá adios&"),
        ("{{FULLPAGENAME:holá  adios'}}", "holá adios'"),
    ]

    for txt, ref in DATA:
        yield check_expand, txt, ref


def test_mw_fullpagename():
    DATA = [
        ("hola", "hola"),
        ("Plantilla:sección", "Plantilla:sección"),
        ("Template:sección", "Plantilla:sección"),
        ("Template talk:sección", "Plantilla discusión:sección"),
        ("hola:adios", "hola:adios"),
        ("holá_adios\"", "holá adios\""),
        ("holá  adios&", "holá adios&"),
        ("holá  adios'", "holá adios'"),
    ]

    for page, ref in DATA:
        yield check_expand, "{{FULLPAGENAME}}", ref, page


def test_pf_talkspace():
    DATA = [
        ("{{TALKSPACE:hola}}", "Discusión"),
        ("{{TALKSPACE:Plantilla:sección}}", "Plantilla discusión"),
        ("{{TALKSPACE:Template:sección}}", "Plantilla discusión"),
        ("{{TALKSPACE: Template:sección }}", "Plantilla discusión"),
        ("{{TALKSPACE:Template talk:sección}}", "Plantilla discusión"),
        ("{{TALKSPACE:hola:adios}}", "Discusión"),
        ("{{TALKSPACE: hola:adios }}", "Discusión"),
        ("{{TALKSPACE:Wikcionario:Café}}", "Wikcionario discusión"),
        ("{{TALKSPACE:media}}", "Discusión"),
    ]

    for txt, ref in DATA:
        yield check_expand, txt, ref


def test_mw_talkspace():
    DATA = [
        ("hola", "Discusión"),
        ("Plantilla:sección", "Plantilla discusión"),
        ("Template:sección", "Plantilla discusión"),
        ("Template talk:sección", "Plantilla discusión"),
        ("hola:adios", "Discusión"),
        ("Wikcionario:Café", "Wikcionario discusión"),
        ("media", "Discusión"),
    ]

    for page, ref in DATA:
        yield check_expand, "{{TALKSPACE}}", ref, page


def test_pf_talkpagename():
    DATA = [
        ("{{TALKPAGENAME:hola}}", "Discusión:hola"),
        ("{{TALKPAGENAME:Plantilla:sección}}", "Plantilla discusión:sección"),
        ("{{TALKPAGENAME:Template:sección}}", "Plantilla discusión:sección"),
        ("{{TALKPAGENAME: Template:sección }}", "Plantilla discusión:sección"),
        ("{{TALKPAGENAME:Template talk:sección}}", "Plantilla discusión:sección"),
        ("{{TALKPAGENAME:hola:adios}}", "Discusión:hola:adios"),
        ("{{TALKPAGENAME: hola:adios }}", "Discusión:hola:adios"),
        ("{{TALKPAGENAME:Wikcionario:Café}}", "Wikcionario discusión:Café"),
        ("{{TALKPAGENAME:media}}", "Discusión:media"),
        ("{{TALKPAGENAME:holá_adios\"}}", "Discusión:holá adios\""),
        ("{{TALKPAGENAME:holá  adios&}}", "Discusión:holá adios&"),
        ("{{TALKPAGENAME:holá  adios'}}", "Discusión:holá adios'"),
    ]

    for txt, ref in DATA:
        yield check_expand, txt, ref


def test_mw_talkpagename():
    DATA = [
        ("hola", "Discusión:hola"),
        ("Plantilla:sección", "Plantilla discusión:sección"),
        ("Template:sección", "Plantilla discusión:sección"),
        ("Template talk:sección", "Plantilla discusión:sección"),
        ("hola:adios", "Discusión:hola:adios"),
        ("Wikcionario:Café", "Wikcionario discusión:Café"),
        ("media", "Discusión:media"),
        ("holá_adios\"", "Discusión:holá adios\""),
        ("holá  adios&", "Discusión:holá adios&"),
        ("holá  adios'", "Discusión:holá adios'"),
    ]

    for page, ref in DATA:
        yield check_expand, "{{TALKPAGENAME}}", ref, page


def test_pf_talkpagenamee():
    DATA = [
        ("{{TALKPAGENAMEE:hola}}", "Discusi%C3%B3n:hola"),
        ("{{TALKPAGENAMEE:Plantilla:sección}}", "Plantilla_discusi%C3%B3n:secci%C3%B3n"),
        ("{{TALKPAGENAMEE:media}}", "Discusi%C3%B3n:media"),
        ("{{TALKPAGENAMEE:hola  adios}}", "Discusi%C3%B3n:hola_adios"),
    ]

    for txt, ref in DATA:
        yield check_expand, txt, ref


def test_mw_talkpagenamee():
    DATA = [
        ("hola", "Discusi%C3%B3n:hola"),
        ("hola:adios", "Discusi%C3%B3n:hola:adios"),
        ("Plantilla:sección", "Plantilla_discusi%C3%B3n:secci%C3%B3n"),
        ("media", "Discusi%C3%B3n:media"),
        ("hola  adios", "Discusi%C3%B3n:hola_adios"),
    ]

    for page, ref in DATA:
        yield check_expand, "{{TALKPAGENAMEE}}", ref, page


def test_pf_articlespace():
    DATA = [
        ("{{ARTICLESPACE:hola}}", ""),
        ("{{ARTICLESPACE:Plantilla:sección}}", "Plantilla"),
        ("{{ARTICLESPACE:Template:sección}}", "Plantilla"),
        ("{{ARTICLESPACE: Template:sección }}", "Plantilla"),
        ("{{ARTICLESPACE:Template talk:sección}}", "Plantilla"),
        ("{{ARTICLESPACE:hola:adios}}", ""),
        ("{{ARTICLESPACE: hola:adios }}", ""),
        ("{{ARTICLESPACE: Discusión:hola:adios }}", ""),
        ("{{ARTICLESPACE: Talk:hola:adios }}", ""),
        ("{{ARTICLESPACE:Wikcionario:Café}}", "Wikcionario"),
        ("{{ARTICLESPACE:Wikcionario discusión:Café}}", "Wikcionario"),
        ("{{ARTICLESPACE:media}}", ""),
        #
        ("{{SUBJECTSPACE:hola}}", ""),
        ("{{SUBJECTSPACE:Plantilla:sección}}", "Plantilla"),
        ("{{SUBJECTSPACE:Template:sección}}", "Plantilla"),
        ("{{SUBJECTSPACE: Template:sección }}", "Plantilla"),
        ("{{SUBJECTSPACE:Template talk:sección}}", "Plantilla"),
        ("{{SUBJECTSPACE:hola:adios}}", ""),
        ("{{SUBJECTSPACE: hola:adios }}", ""),
        ("{{SUBJECTSPACE: Discusión:hola:adios }}", ""),
        ("{{SUBJECTSPACE: Talk:hola:adios }}", ""),
        ("{{SUBJECTSPACE:Wikcionario:Café}}", "Wikcionario"),
        ("{{SUBJECTSPACE:Wikcionario discusión:Café}}", "Wikcionario"),
        ("{{SUBJECTSPACE:media}}", ""),
    ]

    for txt, ref in DATA:
        yield check_expand, txt, ref


def test_mw_articlespace():
    DATA = [
        ("hola", ""),
        ("Plantilla:sección", "Plantilla"),
        ("Template:sección", "Plantilla"),
        ("Template talk:sección", "Plantilla"),
        ("hola:adios", ""),
        ("Discusión:hola:adios", ""),
        ("Talk:hola:adios", ""),
        ("Wikcionario:Café", "Wikcionario"),
        ("Wikcionario discusión:Café", "Wikcionario"),
        ("media", ""),
    ]

    for page, ref in DATA:
        yield check_expand, "{{ARTICLESPACE}}", ref, page

    for page, ref in DATA:
        yield check_expand, "{{SUBJECTSPACE}}", ref, page


def test_pf_articlepagename():
    DATA = [
        ("{{ARTICLEPAGENAME:hola}}", "hola"),
        ("{{ARTICLEPAGENAME:Plantilla:sección}}", "Plantilla:sección"),
        ("{{ARTICLEPAGENAME:Template:sección}}", "Plantilla:sección"),
        ("{{ARTICLEPAGENAME: Template:sección }}", "Plantilla:sección"),
        ("{{ARTICLEPAGENAME:Template talk:sección}}", "Plantilla:sección"),
        ("{{ARTICLEPAGENAME:hola:adios}}", "hola:adios"),
        ("{{ARTICLEPAGENAME: hola:adios }}", "hola:adios"),
        ("{{ARTICLEPAGENAME: Discusión:hola:adios }}", "hola:adios"),
        ("{{ARTICLEPAGENAME: Talk:hola:adios }}", "hola:adios"),
        ("{{ARTICLEPAGENAME:Wikcionario:Café}}", "Wikcionario:Café"),
        ("{{ARTICLEPAGENAME:Wikcionario discusión:Café}}", "Wikcionario:Café"),
        ("{{ARTICLEPAGENAME:media}}", "media"),
        #
        ("{{SUBJECTPAGENAME:hola}}", "hola"),
        ("{{SUBJECTPAGENAME:Plantilla:sección}}", "Plantilla:sección"),
        ("{{SUBJECTPAGENAME:Template:sección}}", "Plantilla:sección"),
        ("{{SUBJECTPAGENAME: Template:sección }}", "Plantilla:sección"),
        ("{{SUBJECTPAGENAME:Template talk:sección}}", "Plantilla:sección"),
        ("{{SUBJECTPAGENAME:hola:adios}}", "hola:adios"),
        ("{{SUBJECTPAGENAME: hola:adios }}", "hola:adios"),
        ("{{SUBJECTPAGENAME: Discusión:hola:adios }}", "hola:adios"),
        ("{{SUBJECTPAGENAME: Talk:hola:adios }}", "hola:adios"),
        ("{{SUBJECTPAGENAME:Wikcionario:Café}}", "Wikcionario:Café"),
        ("{{SUBJECTPAGENAME:Wikcionario discusión:Café}}", "Wikcionario:Café"),
        ("{{SUBJECTPAGENAME:media}}", "media"),
    ]

    for txt, ref in DATA:
        yield check_expand, txt, ref


def test_mw_articlepagename():
    DATA = [
        ("hola", "hola"),
        ("Plantilla:sección", "Plantilla:sección"),
        ("Template:sección", "Plantilla:sección"),
        ("Template talk:sección", "Plantilla:sección"),
        ("hola:adios", "hola:adios"),
        ("Discusión:hola:adios", "hola:adios"),
        ("Talk:hola:adios", "hola:adios"),
        ("Wikcionario:Café", "Wikcionario:Café"),
        ("Wikcionario discusión:Café", "Wikcionario:Café"),
        ("media", "media"),
    ]

    for page, ref in DATA:
        yield check_expand, "{{ARTICLEPAGENAME}}", ref, page

    for page, ref in DATA:
        yield check_expand, "{{SUBJECTPAGENAME}}", ref, page


def test_pf_fullurl():
    DATA = [
        ("{{fullurl:cosa}}", "https://es.wiktionary.org/wiki/cosa"),
    ]

    for txt, ref in DATA:
        yield check_expand, txt, ref


"""
switch test in Plantilla:detección namespace
"""


def test_deteccion_namespace_case_param():
    text = """{{lc:               <!--Resultado a minúscula-->
    <!--Si "demospace" no tiene contenido, detecta el espacio de nombres-->
    {{#if:{{{demospace|}}}
    | {{{demospace}}}
    | {{#if:{{{page|{{{página|}}}}}}
      | <!--Detecta el espacio de nombres en el parámetro "página"-->
        {{#ifeq:{{NAMESPACE:{{{page|{{{página}}}}}} }}|{{TALKSPACE:{{{page|{{{página}}}}}} }}
        | discusion
        | {{SUBJECTSPACE:{{{page|{{{página}}}}}} }}
        }}
      | <!-- No hay parámetros "demospace" o "página", así que detectamos el espacio de nombres actual-->
        {{#ifeq:{{NAMESPACE}}|{{TALKSPACE}}
        | discusión
        | {{SUBJECTSPACE}}
        }}
      }}
    }}
  }}"""

    pages = [
        ("comiera", ""),
        ("Plantilla:sección", "plantilla"),
    ]

    for page, ref in pages:
        yield check_expand, text, ref, page


def test_preserve_previous_wikicode():
    DATA = [
        ("{{hola}}", "[[API#Discusión]]"),
        ("{{hola|BLA}}", "[[BLA#Discusión]]"),
        ("{{hola}} {{hola|BLA}}", "[[API#Discusión]] [[BLA#Discusión]]"),
        ("[[{{{1|BLA}}}#{{PAGENAME}}]]", "[[BLA#API]]"),
        ("{{adios}}", "== X =="),
        ("{{adios}}\n{{adios|Y}}", "== X ==\n== Y =="),
        ("{{adios|z}}\n{{adios|Y}}", "== z ==\n== Y =="),
        ("{{kaixo|2=yes|3=no}}", "no"),
        ("{{kaixo|2=yes|3=no}} {{kaixo|x|si|nanai}}", "no si"),
        ("{{hej}}", '<span class="A">API</span>'),
        ("{{hej|BLA}}", '<span class="A">BLA</span>'),
        ("{{hej|2=Z}} {{hej|BLA}}", '<span class="Z">API</span> <span class="A">BLA</span>'),
        ("{{privet}}", "== API =="),
        ("{{privet}}\n{{privet|A}}", "== API ==\n== A =="),
    ]

    for txt, ref in DATA:
        yield check_expand, txt, ref


def test_preserve_wikicode():
    DATA = [
        ("== {{{1|BLA}}} =="),
        ("=={{{1|BLA}}}=="),
        ("=={{PAGENAME}}=="),
        ("=={{hola}} {{hola|BLA}}=="),
        ("{{hola}} {{hola|BLA}}"),
        ("[[{{{1|BLA}}}#{{PAGENAME}}]]"),
    ]

    for txt in DATA:
        yield check_preserve_wikicode, txt


def check_preserve_wikicode(txt, page="API"):
    p_context = CONTEXT.page_context(page)
    sc = ExpansionContext(templates=TEMPLATES, page_context=p_context)

    wc = tools.parse(txt)

    expanded = p3_str(sc.expand(wc))

    print("TXT: '%s'" % txt)
    print("EXP: '%s'" % expanded)
    print("WIK: '%s'" % wc)

    assert(p3_str(wc) == txt)


def test_time():
    DATA = [
        ("{{CURRENTTIMESTAMP}}", "20160209183400"),
        ("{{LOCALTIMESTAMP}}", "20160209183400"),
        ("{{CURRENTWEEK}}", "6"),
        ("{{LOCALWEEK}}", "6"),
        ("{{CURRENTTIME}}", "18:34"),
        ("{{LOCALTIME}}", "18:34"),
        ("{{CURRENTHOUR}}", "18"),
        ("{{LOCALHOUR}}", "18"),
        ("{{CURRENTDAYNAME}}", "Tuesday"),
        ("{{LOCALDAYNAME}}", "Tuesday"),
        ("{{CURRENTDOW}}", "2"),
        ("{{LOCALDOW}}", "2"),
        ("{{CURRENTDAY}}", "9"),
        ("{{LOCALDAY}}", "9"),
        ("{{CURRENTDAY2}}", "09"),
        ("{{LOCALDAY2}}", "09"),
        ("{{CURRENTYEAR}}", "2016"),
        ("{{LOCALYEAR}}", "2016"),
        ("{{CURRENTMONTH}}", "02"),
        ("{{LOCALMONTH}}", "02"),
        ("{{CURRENTMONTH1}}", "2"),
        ("{{LOCALMONTH1}}", "2"),
        ("{{CURRENTMONTHNAME}}", "February"),
        ("{{LOCALMONTHNAME}}", "February"),
        ("{{CURRENTMONTHABBREV}}", "Feb"),
        ("{{LOCALMONTHABBREV}}", "Feb"),
        ("{{#time: bla}}", "2016-02-09T18:34:00"),
        ("{{#timel: bla}}", "2016-02-09T18:34:00"),
    ]

    t = datetime(2016, 2, 9, 18, 34)

    for txt, ref in DATA:
        yield check_time, txt, ref, t


def check_time(txt, ref, time):
    sc = ExpansionContext(TEMPLATES)
    sc.context.parser_functions.aux_time = time

    exp = p3_str(sc.expand(txt))

    print("TXT: '%s'" % txt)
    print("REF: '%s'" % ref)
    print("EXP: '%s'" % exp)

    assert exp == ref


def test_pf_sharp_titleparts():
    DATA = [
        # translated namespace with subpages
        ("{{#titleparts: Talk:Foo/bar/baz/quok }}", "Discusión:Foo/bar/baz/quok"),
        ("{{#titleparts: Talk:Foo/bar/baz/quok | 1 }}", "Discusión:Foo"),
        ("{{#titleparts: Talk:hola adios/bar/baz/quok | 1 }}", "Discusión:hola adios"),
        ("{{#titleparts: Talk:hola_adios/bar/baz/quok | 1 }}", "Discusión:hola adios"),
        ("{{#titleparts: Talk:Foo/bar/baz/quok | 2 }}", "Discusión:Foo/bar"),
        ("{{#titleparts: Talk:Foo/bar/baz/quok | 2 | 2 }}", "bar/baz"),
        ("{{#titleparts: Talk:Foo/bar/baz/quok | | 2 }}", "bar/baz/quok"),
        ("{{#titleparts: Talk:Foo/bar/baz/quok | | 5 }}", ""),
        ("{{#titleparts: Talk:Foo/bar/baz/quok | -1 }}", "Discusión:Foo/bar/baz"),
        ("{{#titleparts: Talk:Foo/bar/baz/quok | -4 }}", ""),
        ("{{#titleparts: Talk:Foo/bar/baz/quok | -5 }}", ""),
        ("{{#titleparts: Talk:Foo/bar/baz/quok | | -1 }}", "quok"),
        ("{{#titleparts: Talk:Foo/bar/baz/quok | -1 | 2 }}", "bar/baz"),
        ("{{#titleparts: Talk:Foo/bar/baz/quok | -1 | -2 }}", "baz"),
        ("{{#titleparts: Talk:Foo/bar/baz/quok | a }}", "Discusión:Foo/bar/baz/quok"),
        ("{{#titleparts: Talk:Foo/bar/baz/quok | a | b }}", "Discusión:Foo/bar/baz/quok"),
        ("{{#titleparts: Talk:Foo/bar/baz/quok | -1 | b }}", "Discusión:Foo/bar/baz"),
        ("{{#titleparts: Talk:Foo/bar/baz/quok | a | -1 }}", "quok"),

        # translated namespace without subpages
        ("{{#titleparts: Foo/bar/baz/quok }}", "Foo/bar/baz/quok"),
        ("{{#titleparts: Foo/bar/baz/quok | 1 }}", "Foo"),
        ("{{#titleparts: hola adios/bar/baz/quok | 1 }}", "hola adios"),
        ("{{#titleparts: hola_adios/bar/baz/quok | 1 }}", "hola adios"),
        ("{{#titleparts: Foo/bar/baz/quok | 2 }}", "Foo/bar"),
        ("{{#titleparts: Foo/bar/baz/quok | 2 | 2 }}", "bar/baz"),
        ("{{#titleparts: Foo/bar/baz/quok | | 2 }}", "bar/baz/quok"),
        ("{{#titleparts: Foo/bar/baz/quok | | 5 }}", ""),
        ("{{#titleparts: Foo/bar/baz/quok | -1 }}", "Foo/bar/baz"),
        ("{{#titleparts: Foo/bar/baz/quok | -4 }}", ""),
        ("{{#titleparts: Foo/bar/baz/quok | -5 }}", ""),
        ("{{#titleparts: Foo/bar/baz/quok | | -1 }}", "quok"),
        ("{{#titleparts: Foo/bar/baz/quok | -1 | 2 }}", "bar/baz"),
        ("{{#titleparts: Foo/bar/baz/quok | -1 | -2 }}", "baz"),
        ("{{#titleparts: Foo/bar/baz/quok | a }}", "Foo/bar/baz/quok"),
        ("{{#titleparts: Foo/bar/baz/quok | a | b }}", "Foo/bar/baz/quok"),
        ("{{#titleparts: Foo/bar/baz/quok | -1 | b }}", "Foo/bar/baz"),
        ("{{#titleparts: Foo/bar/baz/quok | a | -1 }}", "quok"),
    ]

    for txt, ref in DATA:
        yield check_expand, txt, ref


def test_pf_basepagename():
    DATA = [
        ("{{BASEPAGENAME:hola}}", "hola"),
        ("{{BASEPAGENAME:hola adios}}", "hola adios"),
        ("{{BASEPAGENAME:hola_adios}}", "hola adios"),
        ("{{BASEPAGENAME:hola__adios}}", "hola adios"),
        ("{{BASEPAGENAME:hola  adios}}", "hola adios"),
        ("{{BASEPAGENAME:hola:adios/bla}}", "hola:adios/bla"),
        ("{{BASEPAGENAME:Plantilla:a&ntilde;o/cosa}}", "año"),
        ("{{BASEPAGENAME:Plantilla:hola/bla}}", "hola"),
        ("{{BASEPAGENAME:Template:hola/bla}}", "hola"),
        ("{{BASEPAGENAME:Plantilla:hola/bla/alb}}", "hola/bla"),
    ]

    for txt, ref in DATA:
        yield check_expand, txt, ref


def test_pf_basepagenamee():
    DATA = [
        ("{{BASEPAGENAMEE:hola}}", "hola"),
        ("{{BASEPAGENAMEE:hola adios}}", "hola_adios"),
        ("{{BASEPAGENAMEE:hola  adios}}", "hola_adios"),
        ("{{BASEPAGENAMEE:hola__adios}}", "hola_adios"),
        ("{{BASEPAGENAMEE:hola:adios/bla}}", "hola:adios/bla"),
        ("{{BASEPAGENAMEE:Plantilla:blá/bla}}", "bl%C3%A1"),
        ("{{BASEPAGENAMEE:Plantilla:a&ntilde;o/cosa}}", "a%C3%B1o"),
        ("{{BASEPAGENAMEE:Plantilla:hola/bla}}", "hola"),
        ("{{BASEPAGENAMEE:Template:hola/bla}}", "hola"),
        ("{{BASEPAGENAMEE:Plantilla:hola/bla/alb}}", "hola/bla"),
        ("{{BASEPAGENAMEE:Plantilla Discusión:hola/bla/alb}}", "hola/bla"),
    ]

    for txt, ref in DATA:
        yield check_expand, txt, ref


def test_mw_basepagename():
    DATA = [
        ("hola", "hola"),
        ("hola adios", "hola adios"),
        ("hola  adios", "hola adios"),
        ("hola_adios", "hola adios"),
        ("hola:adios/bla", "hola:adios/bla"),
        ("Plantilla:a&ntilde;o/cosa", "año"),
        ("Plantilla:hola/bla", "hola"),
        ("Template:hola/bla", "hola"),
        ("Plantilla:hola/bla/alb", "hola/bla"),
    ]

    for page, ref in DATA:
        yield check_expand, "{{BASEPAGENAME}}", ref, page


def test_mw_basepagenamee():
    DATA = [
        ("hola", "hola"),
        ("hola adios", "hola_adios"),
        ("hola  adios", "hola_adios"),
        ("hola:adios/bla", "hola:adios/bla"),
        ("Plantilla:blá/bla", "bl%C3%A1"),
        ("Plantilla:a&ntilde;o/cosa", "a%C3%B1o"),
        ("Plantilla:hola/bla", "hola"),
        ("Template:hola/bla", "hola"),
        ("Plantilla:hola/bla/alb", "hola/bla"),
        ("Plantilla Discusión:hola/bla/alb", "hola/bla"),
    ]

    for page, ref in DATA:
        yield check_expand, "{{BASEPAGENAMEE}}", ref, page


def test_pf_rootpagename():
    DATA = [
        # without subpages
        ("{{ROOTPAGENAME:hola adios/bla}}", "hola adios/bla"),
        ("{{ROOTPAGENAME:hola_adios/bla}}", "hola adios/bla"),
        ("{{ROOTPAGENAME:hola  adios/bla}}", "hola adios/bla"),
        ("{{ROOTPAGENAME:hola__adios/bla}}", "hola adios/bla"),
        ("{{ROOTPAGENAME:hola adios/bla/alb}}", "hola adios/bla/alb"),
        # with subpages
        ("{{ROOTPAGENAME:Talk:hola adios/bla}}", "hola adios"),
        ("{{ROOTPAGENAME:Talk:hola_adios/bla}}", "hola adios"),
        ("{{ROOTPAGENAME:Talk:hola adios/bla/alb}}", "hola adios"),
    ]

    for txt, ref in DATA:
        yield check_expand, txt, ref


def test_pf_rootpagenamee():
    DATA = [
        # without subpages
        ("{{ROOTPAGENAMEE:holá adios/bla}}", "hol%C3%A1_adios/bla"),
        ("{{ROOTPAGENAMEE:holá_adios/bla}}", "hol%C3%A1_adios/bla"),
        ("{{ROOTPAGENAMEE:holá  adios/bla}}", "hol%C3%A1_adios/bla"),
        ("{{ROOTPAGENAMEE:holá__adios/bla}}", "hol%C3%A1_adios/bla"),
        ("{{ROOTPAGENAMEE:holá adios/bla/alb}}", "hol%C3%A1_adios/bla/alb"),
        # with subpages
        ("{{ROOTPAGENAMEE:Talk:holá adios/bla}}", "hol%C3%A1_adios"),
        ("{{ROOTPAGENAMEE:Talk:holá_adios/bla}}", "hol%C3%A1_adios"),
        ("{{ROOTPAGENAMEE:Talk:holá adios/bla/alb}}", "hol%C3%A1_adios"),
    ]

    for txt, ref in DATA:
        yield check_expand, txt, ref


def test_mw_rootpagename():
    DATA = [
        # without subpages
        ("hola adios/bla", "hola adios/bla"),
        ("hola_adios/bla", "hola adios/bla"),
        ("hola  adios/bla", "hola adios/bla"),
        ("hola__adios/bla", "hola adios/bla"),
        ("hola adios/bla/alb", "hola adios/bla/alb"),
        # with subpages
        ("Talk:hola adios/bla", "hola adios"),
        ("Talk:hola_adios/bla", "hola adios"),
        ("Talk:hola adios/bla/alb", "hola adios"),
    ]

    for page, ref in DATA:
        yield check_expand, "{{ROOTPAGENAME}}", ref, page


def test_mw_rootpagenamee():
    DATA = [
        # without subpages
        ("holá adios/bla", "hol%C3%A1_adios/bla"),
        ("holá_adios/bla", "hol%C3%A1_adios/bla"),
        ("holá  adios/bla", "hol%C3%A1_adios/bla"),
        ("holá__adios/bla", "hol%C3%A1_adios/bla"),
        ("holá adios/bla/alb", "hol%C3%A1_adios/bla/alb"),
        # with subpages
        ("Talk:holá adios/bla", "hol%C3%A1_adios"),
        ("Talk:holá_adios/bla", "hol%C3%A1_adios"),
        ("Talk:holá adios/bla/alb", "hol%C3%A1_adios"),
    ]

    for page, ref in DATA:
        yield check_expand, "{{ROOTPAGENAMEE}}", ref, page


def test_pf_subpagename():
    DATA = [
        # without subpages
        ("{{SUBPAGENAME:hola adios/bla}}", "hola adios/bla"),
        ("{{SUBPAGENAME:hola_adios/bla}}", "hola adios/bla"),
        ("{{SUBPAGENAME:hola adios/bla/alb}}", "hola adios/bla/alb"),
        # with subpages
        ("{{SUBPAGENAME:Talk:bla/hola adios}}", "hola adios"),
        ("{{SUBPAGENAME:Talk:bla/hola_adios}}", "hola adios"),
        ("{{SUBPAGENAME:Talk:hola adios/bla/alb}}", "alb"),
    ]

    for txt, ref in DATA:
        yield check_expand, txt, ref


def test_pf_subpagenamee():
    DATA = [
        # without subpages
        ("{{SUBPAGENAMEE:holá adios/bla}}", "hol%C3%A1_adios/bla"),
        ("{{SUBPAGENAMEE:holá_adios/bla}}", "hol%C3%A1_adios/bla"),
        ("{{SUBPAGENAMEE:holá adios/bla/alb}}", "hol%C3%A1_adios/bla/alb"),
        # with subpages
        ("{{SUBPAGENAMEE:Talk:bla/holá adios}}", "hol%C3%A1_adios"),
        ("{{SUBPAGENAMEE:Talk:bla/holá_adios}}", "hol%C3%A1_adios"),
        ("{{SUBPAGENAMEE:Talk:hola adios/bla/álb}}", "%C3%A1lb"),
    ]

    for txt, ref in DATA:
        yield check_expand, txt, ref


def test_mw_subpagename():
    DATA = [
        # without subpages
        ("hola adios/bla", "hola adios/bla"),
        ("hola_adios/bla", "hola adios/bla"),
        ("hola adios/bla/alb", "hola adios/bla/alb"),
        # with subpages
        ("Talk:bla/hola adios", "hola adios"),
        ("Talk:bla/hola_adios", "hola adios"),
        ("Talk:hola adios/bla/alb", "alb"),
    ]

    for page, ref in DATA:
        yield check_expand, "{{SUBPAGENAME}}", ref, page


def test_mw_subpagenamee():
    DATA = [
        # without subpages
        ("holá adios/bla", "hol%C3%A1_adios/bla"),
        ("holá_adios/bla", "hol%C3%A1_adios/bla"),
        ("holá adios/bla/alb", "hol%C3%A1_adios/bla/alb"),
        # with subpages
        ("Talk:bla/holá adios", "hol%C3%A1_adios"),
        ("Talk:bla/holá_adios", "hol%C3%A1_adios"),
        ("Talk:hola adios/bla/álb", "%C3%A1lb"),
    ]

    for page, ref in DATA:
        yield check_expand, "{{SUBPAGENAMEE}}", ref, page
