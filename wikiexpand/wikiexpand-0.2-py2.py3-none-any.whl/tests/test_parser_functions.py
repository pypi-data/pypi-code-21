#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import unicode_literals
from __future__ import print_function

import mwparserfromhell as mw
import wikiexpand.expand.parser_functions as PF
from wikiexpand.compat import p3_str


def test_as_parser_function():
    pass


def test_as_template():
    pass


def test_as_parser_function_equal_sign_direct_parsing():
    text = "{{subst:=}}"

    tpl = mw.parse(text).nodes[0]
    pf = PF.as_parser_function(tpl.name, tpl.params)

    print(pf)

    assert "=" == p3_str(pf.params[0].value)
    assert "1" == p3_str(pf.params[0].name)


def test_as_parser_function_equal_sign_unit_separator():
    text = "{{subst:=}}"
    text = PF.ParserFunction(None).prepare(text)

    tpl = mw.parse(text).nodes[0]
    pf = PF.as_parser_function(tpl.name, tpl.params)

    print(pf)

    assert "=" == p3_str(pf.params[0].value)
    assert "1" == p3_str(pf.params[0].name)
