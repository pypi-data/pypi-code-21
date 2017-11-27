#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import unicode_literals
from __future__ import print_function

from nose.tools import assert_list_equal

import mwparserfromhell as mw

from wikiexpand.expand import tools
#from wikiexpand.compat import p3_str


DATA = [
    (" {{{1}}} bla \n",
     "{{{1}}} bla"),
    ("{{{1}}}",
     "{{{1}}}"),
]


def test_str2wikicode():
    for txt, _ in DATA:
        yield check_str2wikicode, txt


def check_str2wikicode(text):
    out = tools.str2wikicode(text)

    assert isinstance(out, mw.wikicode.Wikicode), "is wikicode"
    assert out == text, "equal string"


def test_strip_code_wiki_equal():
    for txt, ref in DATA:
        yield check_strip_code_wiki_equal, txt, ref


def check_strip_code_wiki_equal(text, ref):
    text = mw.parse(text)
    ref = mw.parse(ref)

    out = tools.strip_code(text)

    assert out == ref, "equal wikicode"

    assert len(out.nodes) == len(ref.nodes), "same length"

    assert all(type(x) == type(y) for x, y in zip(out.nodes, ref.nodes)), "same type in nodes"


def test_headings():
    txt = """

== <span id="gd" class="headline-lang">Gaélico escocés</span>[[Categoría:Gaélico escocés-Español]] ==

bla bla bla

=== Etimología ===

=== Sustantivo&nbsp;masculino[[Categoría:GD:Sustantivos]][[Categoría:GD:Sustantivos&nbsp;masculinos]] ===
{| class="inflection-table collapsible" style="float:right;" lang="gd" xml:lang="gd"
|+ class="normal" |<big>'''cosa'''</big>
|-  lang="es" xml:lang="es"
!
! class="vertical" | Singular
! class="vertical" | Plural
|-
! lang="es" xml:lang="es" | Nominativo
| <span lang="gd" xml:lang="gd" style="" class="">[[athair#Gaélico escocés|athair]]</span>
| rowspan="3" |<span lang="gd" xml:lang="gd" style="" class="">[[athraichean#Gaélico escocés|athraichean]]</span><br/>
|-
! lang="es" xml:lang="es" | Genitivo
| <span lang="gd" xml:lang="gd" style="" class="">[[athar#Gaélico escocés|athar]]</span>
|}

;1: [[padre#Español|Padre]].

== <span id="ga" class="headline-lang">[[Wikcionario:Referencia/GA|Irlandés]]</span>[[Categoría:Irlandés-Español]] ==

=== Etimología ===

=== Sustantivo&nbsp;masculino[[Categoría:GA:Sustantivos]][[Categoría:GA:Sustantivos&nbsp;masculinos]] ===

{| class="inflection-table collapsible" style="float: right;"
|+ class="normal" lang="ga" xml:lang="ga"|<span style="font-size: 125%">'''cosa'''</span>
|-
!
!class="vertical"|Singular
!class="vertical"|Plural
|-lang="ga" xml:lang="ga"
! lang="es" xml:lang="es"| [[nominativo|Nominativo]]
|athair
|aithreacha
|-lang="ga" xml:lang="ga"
!lang="es" xml:lang="es" | [[vocativo|Vocativo]]
|a athair
|a aithreacha
|-lang="ga" xml:lang="ga"
!lang="es" xml:lang="es" | [[genitivo|Genitivo]]
|athar
|aithreacha
|-lang="ga" xml:lang="ga"
!lang="es" xml:lang="es" | [[dativo|Dativo]]
|athair
|aithreacha

|}
;1: [[padre#Español|Padre]].
:*'''Antónimo:''' <span lang="ga" xml:lang="ga" style="" class="">[[máthair#Irlandés|máthair]]</span>.
:*'''[[hiperónimo#Español|Hiperónimo]]:''' <span lang="ga" xml:lang="ga" style="" class="">[[fear#Irlandés|fear]]</span>.

==== Referencias y notas ====

<br clear="all"/>
=<div id="es" class="toccolours" >'''[[Wikcionario:Referencia/ES|Español]]'''</div>=

<div class="lemma">cosa</div>
[[Categoría:Español]]

<br clear="all"/>
=<div id="ga" class="toccolours" >'''Irlandés'''</div>=

<div class="lemma">cosa</div>[[Categoría:Irlandés-Español]]

"""
    ref = [
        "Gaélico escocés",
        "Etimología",
        "Sustantivo masculino",
        "Irlandés",
        "Etimología 2",
        "Sustantivo masculino 2",
        #"Referencias y notas",
        "Español",
        "Irlandés 2",
    ]

    out = [title for _, title in tools.headings(txt, levels=(1, 2, 3))]

    print(ref)
    print(out)

    assert_list_equal(ref, out)


def check_equal(val, ref):
    assert val == ref


def test_title_parts():
    DATA = [
        ("hola", ("", "hola")),
        ("Template:hola", ("Template", "hola")),
        ("Template:hola:adios", ("Template", "hola:adios")),
        (":hola", ("", "hola")),
    ]

    for title, ref in DATA:
        val = tools.title_parts(title)
        yield check_equal, val, ref


def test_join_title():
    DATA = [
        (("", "hola"), "hola"),
        (("Template", "hola"), "Template:hola"),
        (("Template", "hola:adios"), "Template:hola:adios"),
    ]

    for (ns, name), ref in DATA:
        val = tools.join_title(ns, name)
        yield check_equal, val, ref
