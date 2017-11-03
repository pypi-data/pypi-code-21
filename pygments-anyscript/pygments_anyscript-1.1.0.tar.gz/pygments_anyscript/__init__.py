# -*- coding: utf-8 -*-

"""Top-level package for Pygments AnyScript plugin."""

__author__ = """Morten Enemark Lund"""
__email__ = 'mel@anybodytech.com'
__version__ = '1.1.0'

import os

from pygments.lexer import (RegexLexer, bygroups, default,
                            include, inherit, words)
from pygments.style import Style
from pygments.token import (Comment, Error, Generic, Keyword,
                            Name, Number, Operator, Other,
                            Punctuation, String, Text, Whitespace)

_ROOT = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(_ROOT, 'classes.txt')) as f:
    ANYCLASSES = f.read().split()
with open(os.path.join(_ROOT, 'functions.txt')) as f:
    ANYFUNCTIONS = f.read().split()
with open(os.path.join(_ROOT, 'globals.txt')) as f:
    ANYGLOBALS = f.read().split()
with open(os.path.join(_ROOT, 'BM_parameters.txt')) as f:
    ANYSTATEMENTS = f.read().split()
with open(os.path.join(_ROOT, 'BM_constants.txt')) as f:
    ANYOPTIONS = f.read().split()


class AnyScriptLexer(RegexLexer):
    """
    """
    name = 'AnyScript'
    aliases = ['anyscript']
    filenames = ['*.any']

    # The trailing ?, rather than *, avoids a geometric performance drop here.
    #: only one /* */ style comment
    _ws1 = r'\s*(?:/[*].*?[*]/\s*)?'

    tokens = {
        'whitespace': [
            # # preprocessor directives: without whitespace
            # ('^#if\s+0', Comment.Preproc, 'if0'),
            # ('^#', Comment.Preproc, 'macro'),
            # # or with whitespace
            # ('^(' + _ws1 + r')(#if\s+0)',
            # bygroups(using(this), Comment.Preproc), 'if0'),
            # ('^(' + _ws1 + ')(#)',
            # bygroups(using(this), Comment.Preproc), 'macro'),
            (r'\n', Text),
            (r'\s+', Text),
            (r'\\\n', Text),  # line continuation
            (r'//(\n|(.|\n)*?[^\\]\n)', Comment.Single),
            (r'/(\\\n)?[*](.|\n)*?[*](\\\n)?/', Comment.Multiline),
        ],

        'statements': [
            (words(('#if', '#ifdef', '#ifndef', '#undef', '#endif', '#include', '#import',
                    '#else', '#elif', '#class_template', '#define', '#path', '#var')), Comment.Preproc),
            (r'"', String, 'string'),
            (r'(\d+\.\d*|\.\d+|\d+)[eE][+-]?\d+', Number.Float),
            (r'(\d+\.\d*|\.\d+|\d+[fF])[fF]?', Number.Float),
            (r'\d+', Number.Integer),
            (r"['&*+=|!\^<>/-]", Operator),
            # TODO: "correctly" parse complex code attributes
            (r'[()\[\],.]', Punctuation),
            # Globals
            (words(ANYGLOBALS,
                   suffix=r'\b'), Keyword.Pseudo),
            # BM_Statements
            (words(ANYSTATEMENTS,
                   suffix=r'\b'), Other.Statements),
            # BM_Options
            (words(ANYOPTIONS,
                   suffix=r'\b'), Other.Options),
            # Functions
            (words(ANYFUNCTIONS, suffix=r'\b'), Name.Builtin),
            # (r'(\.)([a-zA-Z_]\w*)',
            # bygroups(Operator, Name.Attribute)),
            # void is an actual keyword, others are in glib-2.0.vapi
            (words(ANYCLASSES,
                   suffix=r'\b'), Keyword.Type),
            (r'[a-zA-Z_]\w*', Name),
        ],
        'root': [
            include('whitespace'),
            default('statement'),
        ],
        'statement': [
            include('whitespace'),
            include('statements'),
            ('[{}]', Punctuation),
            (';', Punctuation, '#pop'),
        ],
        'string': [
            (r'"', String, '#pop'),
            (r'\\([\\abfnrtv"\']|x[a-fA-F0-9]{2,4}|[0-7]{1,3})',
             String.Escape),
            (r'[^\\"\n]+', String),  # all other characters
            (r'\\\n', String),  # line continuation
            (r'\\', String),  # stray backslash
        ],
        # 'macro': [
        # (r'[^/\n]+', Comment.Preproc),
        # (r'/[*](.|\n)*?[*]/', Comment.Multiline),
        # (r'//.*?\n', Comment.Single, '#pop'),
        # (r'/', Comment.Preproc),
        # (r'(?<=\\)\n', Comment.Preproc),
        # (r'\n', Comment.Preproc, '#pop'),
        # ],
        # 'if0': [
        # (r'^\s*#if(?:def).*?(?<!\\)\n', Comment.Preproc, '#push'),
        # (r'^\s*#el(?:se|if).*\n', Comment.Preproc, '#pop'),
        # (r'^\s*#endif.*?(?<!\\)\n', Comment.Preproc, '#pop'),
        # (r'.*?\n', Comment),
        # ]
    }


class AnyScriptDocLexer(AnyScriptLexer):
    """
    """
    name = 'AnyScriptDoc'
    aliases = ['anyscriptdoc']
    filenames = ['*.anydoc']

    tokens = {
        'multiline-directive': [
            (r'(.*?)(§)', bygroups(Comment.Single, Generic.Deleted), 'new-codes'),
            (r'.*?\n', Comment.Single, '#pop')
        ],
        'new-codes': [
            (r'[^§]+', Generic.Error),
            (r'§', Generic.Deleted, '#pop'),
            (r'[§]', Generic.Error)
        ],
        'statements': [
            # For AnyDoc highlighting
            (r'(§)(/[*])(§)((.|\n)*?)(§)([*]/)(§)',
             bygroups(Generic.Deleted, Generic.Error, Generic.Deleted, Comment.Multiline,
                      Comment.Multiline, Generic.Deleted, Generic.Error, Generic.Deleted)),
            (r'(§)(//)(§)',
             bygroups(Generic.Deleted, Generic.Error, Generic.Deleted), 'multiline-directive'),
            (r'§', Generic.Deleted, 'new-codes'),
            inherit
        ],
    }

    # This remove the § markers used in the Documentation to highlight specific lines
    def get_tokens_unprocessed(self, text):
        for index, token, value in AnyScriptLexer.get_tokens_unprocessed(self, text):
            if token is Generic.Deleted and value == '§':
                yield index, token, ''
            elif token is Error:
                yield index, Text, value
            else:
                yield index, token, value

    # It also ensures the AnyScriptDoc lexer doesn't create Error tokens,
    # since such tokens cause Sphinx to skip highlighting.
    # Hence AnyScriptDoc can be used with AnyScript that is not
    # syntacticly correct in Sphinx
    # def get_tokens(self, text):
    #     for tokentype, value in super().get_tokens(text):
    #         if tokentype is Error:
    #             yield Text, value
    #         else:
    #             yield tokentype, value


class AnyScriptStyle(Style):
    background_color = "#f8f8f8"
    default_style = ""

    styles = {
        Whitespace: "#bbbbbb",
        Comment: "noitalic #4AA02C",
        Comment.Preproc: "noitalic #0000FF",

        Keyword: "#0000FF",
        Keyword.Pseudo: "noinherit",

        Operator: "#111111",
        Operator.Word: "bold #AA22FF",

        Name.Builtin: "noinherit",
        Name.Function: "#0000FF",
        Name.Class: "#0000FF",
        Name.Namespace: "#900090",
        Name.Exception: "#D2413A",
        Name.Variable: "#19177C",
        Name.Constant: "#880000",
        Name.Label: "#A0A000",
        Name.Entity: "bold #999999",
        Name.Attribute: "#7D9029",
        Name.Tag: "bold #008000",
        Name.Decorator: "#AA22FF",

        Other.Statements: "#900090",
        Other.Options: "bold",

        # String: "#666666",
        String.Doc: "italic",
        String.Interpol: "bold #BB6688",
        String.Escape: "bold #BB6622",
        String.Regex: "#BB6688",
        # String.Symbol: "#B8860B",
        String.Symbol: "#19177C",
        String.Other: "#008000",

        # Number: "#666666",

        Generic.Heading: "bold #000080",
        Generic.Subheading: "bold #800080",
        Generic.Deleted: "#f8f8f8",  # Used for $ tag in AnyScript.
        Generic.Inserted: "#00A000",
        Generic.Error: "#FF0000",
        Generic.Emph: "italic",
        Generic.Strong: "bold",
        Generic.Prompt: "bold #000080",
        Generic.Output: "#888",
        Generic.Traceback: "#04D",

        Error: "border:#FF0000"


    }
