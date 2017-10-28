#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division

from nose.tools import (assert_raises,
                        assert_almost_equal)

from wikiexpand.expand.expr import eval_expr


def test_implemented_eval():
    DATA = [
        ("1", 1),
        (" 1 ", 1),
        ("-1", -1),
        ("- 1", -1),
        ("+1", 1),
        ("+ 1", 1),
        ("-1.2e-2", -0.012),
        ("1 + 2", 3),
        (" 1+2 ", 3),
        ("1\t+2\n", 3),
        ("1.2 + 2.22", 3.42),
        ("1.2 - 2.22", -1.02),
        ("1 * 2", 2),
        ("1.2 * 2.2", 2.64),
        ("4 / 2", 2),
        ("1 / 2", 0.5),
        ("1.2 / 2.2", 0.54545454545455),
        ("2^3", 8),
        ("2.2^3", 10.648),
        ("2.2^3.1", 11.521534126786),
        ("1+2*3", 7),
        ("(1+2)*3", 9),
    ]

    for txt, ref in DATA:
        yield check_implemented_eval, txt, ref


def check_implemented_eval(txt, ref):
    out = eval_expr(txt)
    print("TXT", txt)
    print("REF", ref)
    print("OUT", out)
    assert_almost_equal(ref, out)


def test_not_implemented_eval():
    DATA = [
        "",
        ".",
        "a",
        "1 // 2",
        "5 mod 2",
        "round 1.2",
        "ceil(1.3)",
        "floor(2.4)",
        "sin(3)",
        "e",
        "pi",
        "1 <= 2",
        "not 1",
        "1 and -1",
        "-1 or 0",
        "1+",
        "1 foo 2",
    ]

    for txt in DATA:
        yield check_not_implemented_eval, txt


def check_not_implemented_eval(txt):
    with assert_raises((NotImplementedError, SyntaxError)):
        eval_expr(txt)
