#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import unicode_literals
from __future__ import print_function

#from nose.plugins.skip import SkipTest
from nose.tools import assert_almost_equal

import mwparserfromhell as mw

from wikiexpand.expand import ExpansionContext
from wikiexpand.expand.templates import TemplateDict
from wikiexpand.compat import p3_str
from wikiexpand.expand.tools import strip, str2wikicode


TEMPLATES = TemplateDict()

TEMPLATES["="] = "="

TEMPLATES["hola"] = "{| titulo plantilla {{{1|NADA}}} |}"
TEMPLATES["adios"] = "[[{{1|hola}}]]{{#if:{{{1|}}}|{{{1}}}|{{{2|BLA}}}"

TEMPLATES["impropia"] = """<span class="definicion-impropia" style="font-style: italic;">{{{1}}}</span><noinclude>
{{documentación de plantilla}}
</noinclude>
"""

TEMPLATES["inflect.sust.invariante"] = """{|class="inflection-table"
! class="vertical"|{{{titulo|Singular y plural}}}
|-
|lang="{{{leng|es}}}" xml:lang="{{{leng|es}}}"|{{{1|{{PAGENAME}}}}}
|}<noinclude>
{{documentación de plantilla}}
<!-- Añade categorías e interwikis en la página de documentación, no aquí-->
</noinclude>
"""

TEMPLATES["rec"] = "{{{1}}}"

TEMPLATES["ppp"] = "{{{{{{p}}}}}}<noinclude>{{doc}}</noinclude>"
TEMPLATES["tvvv"] = "{{ppp|q=r|p=q}}"


def check_expand(txt, ref, args={}):
    sc = ExpansionContext(TEMPLATES)

    expanded = p3_str(sc.expand(txt, args))

    print("TXT", txt)
    print("REF", ref)
    print("EXP", expanded)

    assert(expanded == ref)


def test_arguments():
    DATA = [
        # arguments
        ("algo {{{1}}} algún {{{2|eo}}} alguien {{{3|}}} alguno {{{1|{{{2}}}}}}",
         "algo {{{1}}} algún eo alguien  alguno {{{2}}}",
         {}),
        ("algo {{{1}}} algún {{{2|eo}}} alguien {{{3|}}} alguno {{{1|{{{2}}}}}}",
         "algo {{{1}}} algún DOS alguien  alguno DOS",
         {"2": "DOS"}),
        ("algo {{{{{{2|1}}}}}}",
         "algo BLAM",
         {"1": "BLAM"}),
        # nested arguments
        ("{{{main|{{{principal|{{{other|{{{otro|}}}}}} }}} }}}",
         "m",
         {"main": "m"}),
    ]

    for txt, ref, args in DATA:
        yield check_expand, txt, ref, args


def test_templates():
    DATA = [
        # templates
        ("aqui hay plantilla {{hola}}",
         "aqui hay plantilla {| titulo plantilla NADA |}"),
        ("aqui hay plantilla {{ hola }}",
         "aqui hay plantilla {| titulo plantilla NADA |}"),
        ("aqui hay plantilla {{hola|{{{1|asco}}}}}",
         "aqui hay plantilla {| titulo plantilla asco |}"),
        ("aqui hay plantilla {{hola|1 = {{{1|asco}}} }}",
         "aqui hay plantilla {| titulo plantilla asco |}"),
        ("aqui hay plantilla {{hola| {{{1|asco}}} }}",
         "aqui hay plantilla {| titulo plantilla  asco  |}"),
        ("aqui hay plantilla {{hola|a|1=b}}",
         "aqui hay plantilla {| titulo plantilla b |}"),
        (";1: {{impropia|elemento compositivo que significa}} uno. un [[único]], relativo a [[uno]] [[solo]].",
         ";1: <span class=\"definicion-impropia\" style=\"font-style: italic;\">elemento compositivo que significa</span> uno. un [[\u00fanico]], relativo a [[uno]] [[solo]]."),
        ("{{inflect.sust.invariante|hola}}",
         "{|class=\"inflection-table\"\n! class=\"vertical\"|Singular y plural\n|-\n|lang=\"es\" xml:lang=\"es\"|hola\n|}"),
        ("{{{{{1}}}|b=}}",
         "{{{{{1}}}|b=}}"),
        ("{{ {{{1}}} |b=}}",
         "{{ {{{1}}} |b=}}"),
    ]

    for txt, ref in DATA:
        yield check_expand, txt, ref


def test_wikilinks():
    DATA = [
        ("[[a]]", "[[a]]"),
        ("[[a|b]]", "[[a|b]]"),
        ("[[ a{{{1|lgo}}} en qué]]",
         "[[ algo en qué]]"),
        ("[[ a{{{1|lgo}}} en qué | pensar]]",
         "[[ algo en qué | pensar]]"),
        ("[[ a{{{1|lgo}}} en qué | {{uc:pensar}}]]",
         "[[ algo en qué | PENSAR]]"),
    ]

    for txt, ref in DATA:
        yield check_expand, txt, ref


def test_tables():
    DATA = [
        ("""{|class="{{{1|es}}}"
|style="white"
|-
|-
|<span style="algo">{{{1|x}}}</span>| {{{2|segundo campo}}}
|}""",
         """{|class="es"
|style="white"
|-
|-
|<span style="algo">x</span>| segundo campo
|}"""),
    ]

    for txt, ref in DATA:
        yield check_expand, txt, ref


def test_tags():
    DATA = [
        ("<includeonly>a {{{1|b}}} c</includeonly>",
         "a b c"),
        ("<span lang=\"{{{1|es}}}\">bla {{{2|a }}}</span>",
         "<span lang=\"es\">bla a </span>"),
    ]

    for txt, ref in DATA:
        yield check_expand, txt, ref


def test_headings():
    DATA = [
        ("== ==",
         "== =="),
        ("== a {{{1|b}}} c ==",
         "== a b c =="),
        ("==<span lang=\"{{{1|es}}}\">bla {{{2|a }}}</span>==",
         "==<span lang=\"es\">bla a </span>=="),
    ]

    for txt, ref in DATA:
        yield check_expand, txt, ref


def test_commments():
    DATA = [
        ("{{{1<!--algo-->|alg<!--bla bla-->uno}}}",
         "alguno"),
    ]

    for txt, ref in DATA:
        yield check_expand, txt, ref


def test_sharp_if():
    DATA = [
        # #if
        ("{{#if:{{{1|}}}|a|b}}",
         "b"),
        ("{{#if:{{{1}}}|a|b}}",
         "a"),
        ("{{#if:{{{1|}}}|a| b }}",
         "b"),
        ("{{#if:{{{1| }}}|a| b }}",
         "b"),
        ("{{#if:{{{1|x}}}|a| b }}",
         "a"),
        ("{{#if: | yes | no}}",
         "no"),
        ("{{#if: string | yes | no}}",
         "yes"),
        ("{{#if:      | yes | no}}",
         "no"),
        ("""{{#if:


| yes | no}}""",
         "no"),
        ("{{#if: 1==2 | yes | no }}",
         "yes"),
        ("{{#if: 0 | yes | no }}",
         "yes"),
        ("{{#if: foo | yes }}",
         "yes"),
        ("{{#if: | yes }}",
         ""),
        ("{{#if: foo | | no}}",
         ""),
        ("{{#if:||1=2}}",
         "1=2"),
    ]

    for txt, ref in DATA:
        yield check_expand, txt, ref


def test_sharp_ifeq():
    DATA = [
        # #ifeq
        ("{{#ifeq: foo | bar | equal | not equal}}",
         "not equal"),
        ("{{#ifeq: foo | Foo | equal | not equal}}",
         "not equal"),
        ("{{#ifeq: \"01\" | \"1\" | equal | not equal}}",
         "not equal"),
        ("{{#ifeq: 10^3 | 1000 | equal | not equal}}",
         "not equal"),
    ]

    for txt, ref in DATA:
        yield check_expand, txt, ref


#@SkipTest
def test_ifeq_link():
    txt = "{{#ifeq: [[foo]] | [[foo]] | equal | not equal}}"
    ref = "equal"
    check_expand(txt, ref, {})


def test_sharp_ifeq_num():
    DATA = [
        # #ifeq numerico
        ("{{#ifeq: 01 | 1 | equal | not equal}}",
         "equal"),
        ("{{#ifeq: 1e3 | 1000 | equal | not equal}}",
         "equal"),
    ]

    for txt, ref in DATA:
        yield check_expand, txt, ref


def test_sharp_tag():
    DATA = [
        # #tag
        ("{{#tag:hola|adios}}",
         "<hola>adios</hola>"),
        ("{{#tag:hola| adios }}",
         "<hola> adios </hola>"),
        ("{{#tag: hola | adios }}",
         "<hola> adios </hola>"),
        ("{{#tag:hola|<}}",
         "<hola><</hola>"),
    ]

    for txt, ref in DATA:
        yield check_expand, txt, ref


def test_sharp_rel2abs():
    DATA = [
        # #rel2abs
        ("{{#rel2abs: ./quok | Help:Foo/bar/baz }}",
         "Help:Foo/bar/baz/quok"),
        ("{{#rel2abs: ../quok | Help:Foo/bar/baz }}",
         "Help:Foo/bar/quok"),
        ("{{#rel2abs: ../. | Help:Foo/bar/baz }}",
         "Help:Foo/bar"),
        ("{{#rel2abs: ../quok/. | Help:Foo/bar/baz }}",
         "Help:Foo/bar/quok"),
        ("{{#rel2abs: ../../quok | Help:Foo/bar/baz }}",
         "Help:Foo/quok"),
        ("{{#rel2abs: ../../../quok | Help:Foo/bar/baz }}",
         "quok"),
        ("{{#rel2abs: /quok | Help:Foo/bar/baz }}",
         "Help:Foo/bar/baz/quok"),
        ("{{#rel2abs: quok | foo}}", "quok"),
        ("{{#rel2abs: quok | /foo/bar}}", "quok"),
        ("{{#rel2abs: quok | foo/bar}}", "quok"),
    ]

    for txt, ref in DATA:
        yield check_expand, txt, ref


def test_sharp_switch():
    DATA = [
        ("{{#switch:1|a|=none|{{{a|1}}}=yes|no}}",
         "yes"),
        ("{{#switch:2|a|=none|{{{a|1}}}=yes|no}}",
         "no"),
        ("{{#switch: baz | foo = Foo | baz = Baz | Bar }}",
         "Baz"),
        ("{{#switch: foo | foo = Foo | baz = Baz | Bar }}",
         "Foo"),
        ("{{#switch: zzz | foo = Foo | baz = Baz | Bar }}",
         "Bar"),
        ("{{#switch: test | foo = Foo | baz = Baz | Bar }}",
         "Bar"),
        ("{{#switch: test | Bar | foo = Foo | baz = Baz }}",
         ""),
        ("{{#switch: test | foo = Foo | baz = Baz | B=ar }}",
         ""),
        ("{{#switch: test | foo = Foo | #default = Bar | baz = Baz }}",
         "Bar"),
        ("{{#switch: test | foo = Foo | baz = Baz }}",
         ""),
        ("""{{#switch: case2
 | case1 = result1
 | case2
 | case3
 | case4 = result234
 | case5 = result5
 | case6
 | case7 = result67
 | #default = default result
}}""",
         "result234"),
        ("""{{#switch: case3
 | case1 = result1
 | case2
 | case3
 | case4 = result234
 | case5 = result5
 | case6
 | case7 = result67
 | #default = default result
}}""",
         "result234"),
        ("""{{#switch: case6
 | case1 = result1
 | case2
 | case3
 | case4 = result234
 | case5 = result5
 | case6
 | case7 = result67
 | #default = default result
}}""",
         "result67"),
        ("{{#switch: | = Nothing | foo = Foo | Something }}",
         "Nothing"),
        ("{{#switch: b | f = Foo | b = Bar | b = Baz | }}",
         "Bar"),
        ("{{#switch:}}",
         ""),
        ("{{#switch: | = {{{1|b}}} | a = {{{2|c}}} }}",
         "b"),
    ]

    for txt, ref in DATA:
        yield check_expand, txt, ref


def test_sharp_switch_num():
    DATA = [
        ("{{#switch: 0 + 1 | 1 = one | 2 = two | three}}",
         "three"),
        ("{{#switch: a | a = A | b = B | C}}",
         "A"),
        ("{{#switch: A | a = A | b = B | C}}",
         "C"),
        ("{{#switch:01|b=d|1=a|01=b|2=d}}",
         "a"),
        ("{{#switch:02|b=d|1=a|01=b|+2=d|null}}",
         "d"),
    ]

    for txt, ref in DATA:
        yield check_expand, txt, ref


def test_sharp_switch_raw_equal():
    DATA = [
        ("""{{#switch: 1=2
     | 1=2 = raw
     | 1<nowiki>=</nowiki>2 = nowiki
     | 1&#61;2 = html
     | 1{{=}}2 = template
     | default
    }}""",
         "html"),
    ]

    for txt, ref in DATA:
        yield check_expand, txt, ref


def test_lc():
    DATA = [
        ("{{lc:}}", ""),
        ("{{lc:hola adios}}", "hola adios"),
        ("{{lc:HOLA ADIOS}}", "hola adios"),
        ("{{lc: HOLA ADIOS }}", "hola adios"),
        ("{{lc:Veni, Vidi, Vici}}", "veni, vidi, vici"),
        ("{{lc:AL {{{A}}} LA}}", "al {{{a}}} la"),
    ]

    for txt, ref in DATA:
        yield check_expand, txt, ref


def test_uc():
    DATA = [
        ("{{uc:}}", ""),
        ("{{uc:hola adios}}", "HOLA ADIOS"),
        ("{{uc:HOLA ADIOS}}", "HOLA ADIOS"),
        ("{{uc: HOLA ADIOS }}", "HOLA ADIOS"),
        ("{{uc:Veni, Vidi, Vici}}", "VENI, VIDI, VICI"),
        ("{{uc:al {{{a}}} la}}", "AL {{{A}}} LA"),
    ]

    for txt, ref in DATA:
        yield check_expand, txt, ref


def test_lcfirst():
    DATA = [
        ("{{lcfirst:}}", ""),
        ("{{lcfirst:hola adios}}", "hola adios"),
        ("{{lcfirst:HOLA ADIOS}}", "hOLA ADIOS"),
        ("{{lcfirst: HOLA ADIOS }}", "hOLA ADIOS"),
        ("{{lcfirst:VENI, VIDI, VICI}}", "vENI, VIDI, VICI"),
        ("{{lcfirst:AL {{{A}}} LA}}", "aL {{{A}}} LA"),
        ("{{lcfirst:_ADIOS}}", "_ADIOS"),
        ("{{lcfirst:A}}", "a"),
        ("{{lcfirst:  A  }}", "a"),
    ]

    for txt, ref in DATA:
        yield check_expand, txt, ref


def test_ucfirst():
    DATA = [
        ("{{ucfirst:}}", ""),
        ("{{ucfirst:hola adios}}", "Hola adios"),
        ("{{ucfirst:HOLA ADIOS}}", "HOLA ADIOS"),
        ("{{ucfirst: HOLA ADIOS }}", "HOLA ADIOS"),
        ("{{ucfirst:veni, vidi, vici}}", "Veni, vidi, vici"),
        ("{{ucfirst:al {{{a}}} la}}", "Al {{{a}}} la"),
        ("{{ucfirst:_adios}}", "_adios"),
        ("{{ucfirst:a}}", "A"),
        ("{{ucfirst:  a  }}", "A"),
    ]

    for txt, ref in DATA:
        yield check_expand, txt, ref


def test_padleft():
    DATA = [
        ("{{padleft:a|9|Xyz}}", "XyzXyzXya"),
        ("{{padleft:ab|9|Xyz}}", "XyzXyzXab"),
        ("{{padleft: ab | 9 | Xyz }}", "XyzXyzXab"),
        ("{{padleft: ab | a | Xyz }}", "ab"),
        ("{{padleft: xyz | 2}}", "xyz"),
        ("{{padleft:xyz|5}}", "00xyz"),
        ("{{padleft:xyz|5|_}}", "__xyz"),
        ("{{padleft:xyz|5|abc}}", "abxyz"),
        ("{{padleft:xyz|2}}", "xyz"),
        ("{{padleft:|1|xyz}}", "x"),
    ]

    for txt, ref in DATA:
        yield check_expand, txt, ref


def test_padright():
    DATA = [
        ("{{padright:a|9|Xyz}}", "aXyzXyzXy"),
        ("{{padright:ab|9|Xyz}}", "abXyzXyzX"),
        ("{{padright: ab | 9 | Xyz }}", "abXyzXyzX"),
        ("{{padright: ab | a | Xyz }}", "ab"),
        ("{{padright: xyz | 2}}", "xyz"),
        ("{{padright:xyz|5}}", "xyz00"),
        ("{{padright:xyz|5|_}}", "xyz__"),
        ("{{padright:xyz|5|abc}}", "xyzab"),
        ("{{padright:xyz|2}}", "xyz"),
        ("{{padright:|1|xyz}}", "x"),
    ]

    for txt, ref, in DATA:
        yield check_expand, txt, ref


def test_urlencode():
    DATA = [
        ("{{urlencode:}}", ""),
        ("{{urlencode:olá}}", "ol%C3%A1"),
        ("{{urlencode:hola adios}}", "hola+adios"),
        ('{{urlencode: "Wörterbuch" }}', "%22W%C3%B6rterbuch%22"),
    ]

    for txt, ref, in DATA:
        yield check_expand, txt, ref


def test_anchorencode():
    DATA = [
        ("{{anchorencode:}}", ""),
        ("{{anchorencode:olá}}", "ol.C3.A1"),
        ("{{anchorencode:hola adios}}", "hola_adios"),
        ('{{anchorencode: "Wörterbuch" }}', ".22W.C3.B6rterbuch.22"),
    ]

    for txt, ref, in DATA:
        yield check_expand, txt, ref


def test_defaultsort():
    DATA = [
        ("{{defaultsort:bla}}", ""),
        ("{{DEFAULTSORT:bla|alb}}", ""),
    ]

    for txt, ref in DATA:
        yield check_expand, txt, ref


def test_parser_funcion_expanded_name():
    DATA = [
        ("{{{{{1|uc:}}}a}}", "A"),
        ("{{{{{1|uc}}}:a}}", "A"),
    ]

    for txt, ref, in DATA:
        yield check_expand, txt, ref


def test_argument_recursion():
    DATA = [
        ("{{rec|1={{{1}}}}}",
         "{{{1}}}", {}),
        ("{{rec|1=a {{{1}}} b}}",
         "a {{{1}}} b", {}),
        ("{{rec|1={{rec|1={{{1}}} }} }}",
         "{{{1}}}", {}),
        ("{{rec|1={{rec|1=a {{{1}}} b}} }}",
         "a {{{1}}} b", {}),
        ("{{rec|1=a {{rec|{{{1}}}}} b}}",
         "a {{{1}}} b", {}),
        ("{{ppp|p=q|q=r}}",
         "r", {}),
        #("{{tvvv|p=q|q=r|r=s}}",
        # "s", {}),
    ]

    for txt, ref, args in DATA:
        yield check_expand, txt, ref, args


def test_subst():
    DATA = [("{{subst:}}", "{{subst:}}"),
            ("{{subst: }}", "{{subst: }}"),
            ("{{safesubst:}}", "{{safesubst:}}"),
            ("{{safesubst:#expr:1+1}}", "2"),
            ("{{subst:=}}", "="),
            ("{{subst:hola}}", "{| titulo plantilla NADA |}"),
            ("{{subst:hola|UNO}}", "{| titulo plantilla UNO |}"),
            ("{{subst:hola|1=UNO}}", "{| titulo plantilla UNO |}"),
            ("{{subst:hola|{{subst:=}}}}", "{| titulo plantilla = |}"),
            ("{{subst:{{subst:#expr:1+1}}}}", "{{subst:2}}"),
            ("{{safesubst:#if:|yes|{{{1|hola}}}}}", "hola"),
            ("{{safesubst:#if:|yes|{{=}}}}", "="),
            ("{{safesubst:#if:|yes|{{hola|UNO}}}}", "{| titulo plantilla UNO |}"),
            ]

    for txt, ref in DATA:
        yield check_expand, txt, ref


def test_sharp_expr():
    DATA = [
        ("{{#expr:}}", ""),
        ("{{#expr: }}", ""),
        ("{{#expr: \n}}", ""),
        ("{{#expr: \n1}}", 1),
        ("{{#expr: 1}}", 1),
        ("{{#expr:  1 }}", 1),
        ("{{#expr: -1}}", -1),
        ("{{#expr: - 1}}", -1),
        ("{{#expr: +1}}", 1),
        ("{{#expr: + 1}}", 1),
        ("{{#expr: -1.2e-2}}", -0.012),
        ("{{#expr: 1 + 2}}", 3),
        ("{{#expr:  1+2 }}", 3),
        ("{{#expr: 1\t+2\n}}", 3),
        ("{{#expr: 1.2 + 2.22}}", 3.42),
        ("{{#expr: 1.2 - 2.22}}", -1.02),
        ("{{#expr: 1 * 2}}", 2),
        ("{{#expr: 1.2 * 2.2}}", 2.64),
        ("{{#expr: 4 / 2}}", 2),
        ("{{#expr: 1 / 2}}", 0.5),
        ("{{#expr: 1.2 / 2.2}}", 0.54545454545455),
        ("{{#expr: 2^3}}", 8),
        ("{{#expr: 2.2^3}}", 10.648),
        ("{{#expr: 2.2^3.1}}", 11.521534126786),
        ("{{#expr: 1+2*3}}", 7),
        ("{{#expr: (1+2)*3}}", 9),
    ]

    for txt, ref in DATA:
        yield check_expand_expr, txt, ref


def check_expand_expr(txt, ref, args={}):
    sc = ExpansionContext(TEMPLATES)

    expanded = p3_str(sc.expand(txt, args))

    print("TXT", txt)
    print("REF", ref)
    print("EXP", expanded)

    try:
        expanded, ref = float(expanded), float(ref)
        assert_almost_equal(float(expanded), float(ref))
    except ValueError:
        assert expanded == ref


def tpl_str_number(params, fn, ctx, frame):
    text = strip(params.get("1", ""))

    ndigits = 0
    for char in text:
        if not char.isdigit():
            break
        ndigits += 1
    return str2wikicode(ndigits)


def test_expand_local_template():
    local_templates = {
        "str number": tpl_str_number,
    }
    DATA = [
        ("{{str number}}", "0"),
        ("{{str number|0}}", "1"),
        ("{{str number|1}}", "1"),
        ("{{str number|1=1}}", "1"),
        ("{{str number|12}}", "2"),
        ("{{str number|12a23}}", "2"),
        ("{{str number|a12a23}}", "0"),
        ("{{#expr:{{str number|12}} + {{str number|345}}}}", "5"),
        ("{{#invoke:str number}}", "0"),
        ("{{#invoke:str number|0}}", "1"),
        ("{{#invoke:str number|1}}", "1"),
        ("{{#invoke:str number|1=1}}", "1"),
        ("{{#invoke:str number|12}}", "2"),
        ("{{#invoke:str number|12a23}}", "2"),
        ("{{#invoke:str number|a12a23}}", "0"),
    ]

    for txt, ref in DATA:
        yield check_expand_local_template, txt, ref, local_templates


def check_expand_local_template(txt, ref, templates):
    sc = ExpansionContext(TEMPLATES)
    TEMPLATES.callable_templates.update(templates)

    expanded = p3_str(sc.expand(txt))

    TEMPLATES.callable_templates.clear()

    print("TXT", txt)
    print("REF", ref)
    print("EXP", expanded)

    assert expanded == ref


def test_preserve_wikicode():
    txt = """
    [[{{{1|{{hola}}}}}#{{UCFIRST:{{{tipo|{{hola|{{{2|es}}}}}}}}}}{{#if:{{{3|{{{núm|{{{num|}}}}}}}}}|{{#ifeq:{{{3|{{{núm|{{{num|}}}}}}}}}|1||&nbsp;{{{3|{{{núm|{{{num|}}}}}}}}}}}
}}|{{UCFIRST:{{{1|{{hola}}}}}}}]]{{#if:{{{3|{{{núm|{{{num|}}}}}}}}}|{{=|{{{3|{{{núm|{{{num|}}}}}}}}}}}|}}
    """

    args = {
        "num": "X",
        "2": "Y",
        "1": "BLA",
    }
    wc = mw.parse(txt)

    sc = ExpansionContext(TEMPLATES)

    expanded = p3_str(sc.expand(wc, args))

    print("TXT", txt)
    print("WIK", p3_str(wc))
    print("EXP", expanded)

    assert txt == wc


def test_preserve_template_pre():
    txt = """
    [[{{hola}}{{hola|1=A|2=B}}{{{1|{{hola}}}}}#{{UCFIRST:{{{tipo|{{adios|{{{2|es}}}}}}}}}}{{#if:{{{3|{{{núm|{{{num|}}}}}}}}}|{{#ifeq:{{{3|{{{núm|{{{num|}}}}}}}}}|1||&nbsp;{{{3|{{{núm|{{{num|}}}}}}}}}}}
}}|{{UCFIRST:{{{1|{{hola}}}}}}}]]{{#if:{{{3|{{{núm|{{{num|}}}}}}}}}|{{=|{{{3|{{{núm|{{{num|}}}}}}}}}}}|}}
    """

    args = {
        "num": "X",
        "2": "Y",
        "1": "BLA",
    }
    wc = mw.parse(txt)

    hola = TEMPLATES["hola"]
    adios = TEMPLATES["adios"]

    sc = ExpansionContext(TEMPLATES)

    p3_str(sc.expand(wc, args))

    assert "hola" in sc._cache_pre
    assert "adios" in sc._cache_pre

    hola_post = p3_str(sc._cache_pre["hola"])
    adios_post = p3_str(sc._cache_pre["adios"])

    print("HOLA PREV |%s|" % hola)
    print("HOLA POST |%s|" % hola_post)

    print("ADIOS PREV |%s|" % adios)
    print("ADIOS POST |%s|" % adios_post)

    assert p3_str(hola) == p3_str(hola_post)
    assert p3_str(adios) == p3_str(adios_post)


def test_preserve_template_post():
    txt = """
    [[{{hola}}{{hola|1=A|2=B}}{{{1|{{hola}}}}}#{{UCFIRST:{{{tipo|{{adios|{{{2|es}}}}}}}}}}{{#if:{{{3|{{{núm|{{{num|}}}}}}}}}|{{#ifeq:{{{3|{{{núm|{{{num|}}}}}}}}}|1||&nbsp;{{{3|{{{núm|{{{num|}}}}}}}}}}}
}}|{{UCFIRST:{{{1|{{hola}}}}}}}]]{{#if:{{{3|{{{núm|{{{num|}}}}}}}}}|{{=|{{{3|{{{núm|{{{num|}}}}}}}}}}}|}}
    """

    args = {
        "num": "X",
        "2": "Y",
        "1": "BLA",
    }
    wc = mw.parse(txt)

    hola = "{| titulo plantilla NADA |}"

    sc = ExpansionContext(TEMPLATES)

    p3_str(sc.expand(wc, args))

    assert "hola" in sc._cache_post

    hola_post = p3_str(sc._cache_post["hola"])

    print("HOLA PREV |%s|" % hola)
    print("HOLA POST |%s|" % hola_post)

    assert p3_str(hola) == p3_str(hola_post)


def test_node_types():
    DATA = [
        "{{{1|x}}}",
        "[[a|b]]",
        "== x == ",
        "g",
        "{{=}}",
        "{{hola}}",
        "{{hola|x}}",
        "{{#if:x|y|z}}",
        "<span>x</span>",
        '<span class="x">y</span>',
        "<includeonly>x</includeonly>",
        """
    [[{{hola}}
    {{hola|1=A|2=B}}
    {{{1|{{hola}}}}}#{{UCFIRST:{{{tipo|{{adios|{{{2|es}}}}}}}}}}{{#if:{{{3|{{{núm|{{{num|}}}}}}}}}|{{#ifeq:{{{3|{{{núm|{{{num|}}}}}}}}}|1||&nbsp;{{{3|{{{núm|{{{num|}}}}}}}}}}}}}|{{UCFIRST:{{{1|{{hola}}}}}}}]]
    {{#if:{{{3|{{{núm|{{{num|}}}}}}}}}|{{=|{{{3|{{{núm|{{{num|}}}}}}}}}}}|}}""",
    ]

    for txt in DATA:
        yield check_node_types, txt


def check_node_types(txt):
    sc = ExpansionContext(TEMPLATES)

    expanded = sc.expand(txt)

    for n in expanded.ifilter():
        assert not isinstance(n, p3_str)
