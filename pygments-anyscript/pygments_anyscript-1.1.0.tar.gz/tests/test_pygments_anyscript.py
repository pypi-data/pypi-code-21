#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Very simple tests for `pygments_anyscript` package."""
import os

import pygments
import pytest

import pygments_anyscript

ANYSCRIPT_TEST1 = """\
// Comment
#include "include.any"
Main =
{
    AnyFolder Model =
    {
    };

    AnyBodyStudy MyStudy =
    {
        Gravity = {0.0, 0.0, -9.81};
    };

};

"""


@pytest.mark.skipif(bool(os.getenv('NOPLUGINS')),
                    reason="Don't test plugin installation")
def test_install_lexer():
    lexer = pygments.lexers.get_lexer_by_name('AnyScript')
    assert isinstance(lexer, pygments_anyscript.AnyScriptLexer)

    lexerdoc = pygments.lexers.get_lexer_by_name('AnyScriptDoc')
    assert isinstance(lexerdoc, pygments_anyscript.AnyScriptDocLexer)


@pytest.mark.skipif(bool(os.getenv('NOPLUGINS')),
                    reason="Don't test plugin installation")
def test_install_style():
    import pygments
    style = pygments.styles.get_style_by_name('AnyScript')
    assert style is pygments_anyscript.AnyScriptStyle


def test_lexer():
    lexer = pygments_anyscript.AnyScriptLexer()
    tokens = list(lexer.get_tokens(ANYSCRIPT_TEST1))

    assert tokens[0][0] in pygments_anyscript.Comment
    assert tokens[0][1] == '// Comment\n'

    assert tokens[7][0] in pygments_anyscript.Name
    assert tokens[7][1] == 'Main'

    assert tokens[29][0] in pygments_anyscript.Keyword
    assert tokens[29][1] == 'AnyBodyStudy'
