#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of Pynspect package (https://pypi.python.org/pypi/pynspect).
# Originally part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2016 CESNET, z.s.p.o (http://www.ces.net/).
# Copyright (C) since 2016 Jan Mach <honza.mach.ml@gmail.com>
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------


r"""
This module contains object encapsulation of `PLY <http://www.dabeaz.com/ply/>`__
parser for universal filtering and query language grammar. It is designed
for working with almost arbitrary data structures and can be used in wide range
of projects.


Grammar features
^^^^^^^^^^^^^^^^

* Logical operations: ``and or xor not exists``

  All logical operations support upper case and lower case name variants.
  Additionally, there are also symbolic variants ``|| ^^ && ! ?`` with higher
  priority and which can be used in some cases instead of parentheses and thus
  improve parsing performance.

* Comparison operations: ``like in is eq ne gt ge lt le``

  All comparison operations support upper case and lower case name variants.
  Additionally, there are also symbolic variants ``=~ ~~ == != <> >= > <= <``.

* Mathematical operations: ``+ - * / %``
* JPath variables: ``Source[0].IP4[1]``
* Directly recognized constants:

    * IPv4: ``127.0.0.1 127.0.0.1/32 127.0.0.1-127.0.0.5 127.0.0.1..127.0.0.5``
    * IPv6: ``::1 ::1/64 ::1-::5 ::1..::5``
    * Datetime: ``2017-01-01T12:00:00Z 2017-01-01t12:00:00.123-02:00``
    * Integer: ``0 1 42``
    * Float: ``3.14159``

* Quoted literal constants: ``"double quoted"`` or ``'single quoted'``

* Functions: ``time() size(Source.IP4)``

  Grammar supports calling arbitrary functions with optional arguments. Argument
  may be any valid expression, multiple arguments must be passed down as list.
  Function support in grammar is only one part of the whole picture, it must also
  be implemented in tree traversers to fully work. Each traverser may provide
  certain set of available functions and define required and optional arguments.

For more details on supported grammar token syntax please see the documentation
of :py:mod:`pynspect.lexer` module.


Example expressions
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    time() > (CreateTime + 3600)
    CreateTime > 2017-01-01T12:00:00Z and Source.IP4 in [127.0.0.1, 127.0.0.2]
    Category in ['Attempt.Login'] and (Target.Proto in ['telnet'] or Source.Proto in ['telnet'] or Target.Port in [23])


Currently implemented grammar
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bnf

    expression : xor_expression OP_OR expression
               | xor_expression

    xor_expression : and_expression OP_XOR xor_expression
                   | and_expression

    and_expression : or_p_expression OP_AND and_expression
                   | or_p_expression

    or_p_expression : xor_p_expression OP_OR_P or_p_expression
                    | xor_p_expression

    xor_p_expression : and_p_expression OP_XOR_P xor_p_expression
                     | and_p_expression

    and_p_expression : not_expression OP_AND_P and_p_expression
                     | not_expression

    not_expression : OP_NOT ex_expression
                   | ex_expression

    ex_expression : OP_EXISTS cmp_expression
                  | cmp_expression

    cmp_expression : term OP_LIKE cmp_expression
                   | term OP_IN cmp_expression
                   | term OP_IS cmp_expression
                   | term OP_EQ cmp_expression
                   | term OP_NE cmp_expression
                   | term OP_GT cmp_expression
                   | term OP_GE cmp_expression
                   | term OP_LT cmp_expression
                   | term OP_LE cmp_expression
                   | term

    term : factor OP_PLUS term
         | factor OP_MINUS term
         | factor OP_TIMES term
         | factor OP_DIVIDE term
         | factor OP_MODULO term
         | factor

    factor : IPV4
           | IPV6
           | DATETIME
           | INTEGER
           | FLOAT
           | VARIABLE
           | CONSTANT
           | FUNCTION RPAREN
           | FUNCTION expression RPAREN
           | LBRACK list RBRACK
           | LPAREN expression RPAREN

    list : IPV4
         | IPV6
         | DATETIME
         | INTEGER
         | FLOAT
         | VARIABLE
         | CONSTANT
         | IPV4 COMMA list
         | IPV6 COMMA list
         | DATETIME COMMA list
         | INTEGER COMMA list
         | FLOAT COMMA list
         | VARIABLE COMMA list
         | CONSTANT COMMA list

.. note::

    Implementation of this module is very *PLY* specific, please read the
    appropriate `documentation <http://www.dabeaz.com/ply/ply.html#ply_nn3>`__
    to understand it. For the same reason the `pylint <https://pylint.readthedocs.io/en/latest/>`__
    tool comlains a lot about code style in this module, but that is a feature.

"""


__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>"


import logging
import ply.yacc

from pynspect.lexer import PynspectFilterLexer
from pynspect.rules import IPV4Rule, IPV6Rule, DatetimeRule, IntegerRule, FloatRule, VariableRule, ConstantRule,\
    LogicalBinOpRule, UnaryOperationRule, ComparisonBinOpRule, MathBinOpRule, FunctionRule, ListRule


class PynspectGrammarSyntaxError(Exception):
    """

    """
    pass


class PynspectFilterParser():
    """
    Object encapsulation of *PLY* parser implementation for filtering and
    query language grammar used in Mentat project.
    """

    def __init__(self):
        self.logger = None
        self.lexer  = None
        self.tokens = None
        self.parser = None

    def build(self):
        """
        Build/rebuild the parser object
        """
        self.logger = logging.getLogger('ply_parser')

        self.lexer = PynspectFilterLexer()
        self.lexer.build()

        # Skip the first item in self.lexer.tokens, which is the 'EXP_ALL' token
        # to get rid of following message:
        # ... Token 'EXP_ALL' defined, but not used
        # ... There is 1 unused token
        #
        self.tokens = self.lexer.tokens[1:]

        self.parser = ply.yacc.yacc(
            module=self,
            #debuglog=self.logger,
            errorlog=self.logger
            #start='statements',
            #debug=yacc_debug,
            #optimize=yacc_optimize,
            #tabmodule=yacctab
        )

    def parse(self, data, filename='', debuglevel=0):
        """
        Parse given data.

            data:
                A string containing the filter definition
            filename:
                Name of the file being parsed (for meaningful
                error messages)
            debuglevel:
                Debug level to yacc
        """
        self.lexer.filename = filename
        self.lexer.reset_lineno()
        if not data or data.isspace():
            return []
        return self.parser.parse(data, lexer=self.lexer, debug=debuglevel)


    #---------------------------------------------------------------------------


    @staticmethod
    def _create_factor_rule(tok):
        """
        Simple helper method for creating factor node objects based on node name.
        """
        if tok[0] == 'IPV4':
            return IPV4Rule(tok[1])
        if tok[0] == 'IPV6':
            return IPV6Rule(tok[1])
        if tok[0] == 'DATETIME':
            return DatetimeRule(tok[1])
        if tok[0] == 'INTEGER':
            return IntegerRule(tok[1])
        if tok[0] == 'FLOAT':
            return FloatRule(tok[1])
        if tok[0] == 'VARIABLE':
            return VariableRule(tok[1])
        return ConstantRule(tok[1])

    @staticmethod
    def _create_function_rule(tok, args = None):
        """
        Simple helper method for creating function node objects.
        """
        if args:
            return FunctionRule(tok[1], args)
        return FunctionRule(tok[1])

    @staticmethod
    def p_expression(tok):
        """expression : xor_expression OP_OR expression
                      | xor_expression"""
        if len(tok) == 4:
            tok[0] = LogicalBinOpRule(tok[2], tok[1], tok[3])
        else:
            tok[0] = tok[1]

    @staticmethod
    def p_xor_expression(tok):
        """xor_expression : and_expression OP_XOR xor_expression
                          | and_expression"""
        if len(tok) == 4:
            tok[0] = LogicalBinOpRule(tok[2], tok[1], tok[3])
        else:
            tok[0] = tok[1]

    @staticmethod
    def p_and_expression(tok):
        """and_expression : or_p_expression OP_AND and_expression
                          | or_p_expression"""
        if len(tok) == 4:
            tok[0] = LogicalBinOpRule(tok[2], tok[1], tok[3])
        else:
            tok[0] = tok[1]

    @staticmethod
    def p_or_p_expression(tok):
        """or_p_expression : xor_p_expression OP_OR_P or_p_expression
                      | xor_p_expression"""
        if len(tok) == 4:
            tok[0] = LogicalBinOpRule(tok[2], tok[1], tok[3])
        else:
            tok[0] = tok[1]

    @staticmethod
    def p_xor_p_expression(tok):
        """xor_p_expression : and_p_expression OP_XOR_P xor_p_expression
                          | and_p_expression"""
        if len(tok) == 4:
            tok[0] = LogicalBinOpRule(tok[2], tok[1], tok[3])
        else:
            tok[0] = tok[1]


    @staticmethod
    def p_and_p_expression(tok):
        """and_p_expression : not_expression OP_AND_P and_p_expression
                          | not_expression"""
        if len(tok) == 4:
            tok[0] = LogicalBinOpRule(tok[2], tok[1], tok[3])
        else:
            tok[0] = tok[1]

    @staticmethod
    def p_not_expression(tok):
        """not_expression : OP_NOT ex_expression
                          | ex_expression"""
        if len(tok) == 3:
            tok[0] = UnaryOperationRule(tok[1], tok[2])
        else:
            tok[0] = tok[1]

    @staticmethod
    def p_ex_expression(tok):
        """ex_expression : OP_EXISTS cmp_expression
                         | cmp_expression"""
        if len(tok) == 3:
            tok[0] = UnaryOperationRule(tok[1], tok[2])
        else:
            tok[0] = tok[1]


    @staticmethod
    def p_cmp_expression(tok):
        """cmp_expression : term OP_LIKE cmp_expression
                          | term OP_IN cmp_expression
                          | term OP_IS cmp_expression
                          | term OP_EQ cmp_expression
                          | term OP_NE cmp_expression
                          | term OP_GT cmp_expression
                          | term OP_GE cmp_expression
                          | term OP_LT cmp_expression
                          | term OP_LE cmp_expression
                          | term"""
        if len(tok) == 4:
            tok[0] = ComparisonBinOpRule(tok[2], tok[1], tok[3])
        else:
            tok[0] = tok[1]

    @staticmethod
    def p_term(tok):
        """term : factor OP_PLUS term
                | factor OP_MINUS term
                | factor OP_TIMES term
                | factor OP_DIVIDE term
                | factor OP_MODULO term
                | factor"""
        if len(tok) == 4:
            tok[0] = MathBinOpRule(tok[2], tok[1], tok[3])
        else:
            tok[0] = tok[1]

    def p_factor(self, tok):
        """factor : IPV4
                  | IPV6
                  | DATETIME
                  | INTEGER
                  | FLOAT
                  | VARIABLE
                  | CONSTANT
                  | FUNCTION RPAREN
                  | FUNCTION expression RPAREN
                  | LBRACK list RBRACK
                  | LPAREN expression RPAREN"""
        if len(tok) == 2:
            tok[0] = self._create_factor_rule(tok[1])
        elif len(tok) == 3:
            tok[0] = self._create_function_rule(tok[1])
        elif tok[1][0] == 'FUNCTION':
            tok[0] = self._create_function_rule(tok[1], tok[2])
        else:
            tok[0] = tok[2]

    def p_list(self, tok):
        """list : IPV4
                | IPV6
                | DATETIME
                | INTEGER
                | FLOAT
                | VARIABLE
                | CONSTANT
                | IPV4 COMMA list
                | IPV6 COMMA list
                | DATETIME COMMA list
                | INTEGER COMMA list
                | FLOAT COMMA list
                | VARIABLE COMMA list
                | CONSTANT COMMA list"""
        node = self._create_factor_rule(tok[1])
        if len(tok) == 2:
            tok[0] = ListRule([node])
        else:
            tok[0] = ListRule([node], tok[3])

    @staticmethod
    def p_error(tok):
        if tok:
            raise PynspectGrammarSyntaxError("Syntax error at '%s'" % str(tok))
        else:
            raise PynspectGrammarSyntaxError("Syntax error while parsing the grammar rule")


#
# Perform the demonstration.
#
if __name__ == "__main__":

    import pprint

    TEST_DATA = "1 and 1 or 1 xor 1"

    # Build the parser and try it out
    DEMO_PARSER = PynspectFilterParser()
    DEMO_PARSER.build()

    print("Parsing: {}".format(TEST_DATA))
    pprint.pprint(DEMO_PARSER.parse(TEST_DATA))
