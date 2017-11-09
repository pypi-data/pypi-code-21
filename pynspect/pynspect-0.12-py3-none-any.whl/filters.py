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


"""
This module provides tools for data filtering based on filtering and query
grammar.

The filtering grammar is thoroughly described in following module:

* :py:mod:`pynspect.lexer`

  Lexical analyzer, descriptions of valid grammar tokens.

* :py:mod:`pynspect.gparser`

  Grammar parser, language grammar description

* :py:mod:`pynspect.rules`

  Object representation of grammar rules, interface definition

* :py:mod:`pynspect.jpath`

  The addressing language JPath.

Please refer to appropriate module for more in-depth information.

There are following main tools in this package:

* :py:class:`DataObjectFilter`

  Tool capable of filtering data structures according to given filtering rules.

.. warning::

    Be carefull with the grammar function names. Currently, there is a flaw in the expression
    grammar that forbids using function names that begin with the same characters as
    grammar keywords like 'and', 'le', 'like', etc. For example the name 'len' is not
    a valid function name, because there is a collision with 'le' comparison operator.

.. todo::

    There is quite a lot of code that needs to be written before actual filtering
    can take place. In the future, there should be some kind of object, that will
    be tailored for immediate processing and will take care of initializing
    uderlying parser, compiler and filter. This object will be designed later.

"""


__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>"


import time

from pynspect.rules import FilteringRuleException
from pynspect.traversers import BaseFilteringTreeTraverser
from pynspect.jpath import jpath_values


#-------------------------------------------------------------------------------


def grfcbk_size(args):
    """
    Grammar rule function callback: **size**. This function will count the size of
    first item in argument list.

    :param list args: List of function arguments.
    :return: Size of the first item in argument list.
    :rtype: int
    """
    return len(args[0])

def grfcbk_time(args):
    """
    Grammar rule function callback: **time**. This function will call the
    :py:func:`time.time` function and return the result.

    :param list args: List of function arguments. Should be empty, but
    :return: The time in seconds since the epoch as a floating point number.
    :rtype: float
    """
    if args:
        raise FilteringRuleException("The 'time' function does not take any arguments.")
    return time.time()


#-------------------------------------------------------------------------------


class DataObjectFilter(BaseFilteringTreeTraverser):
    """
    Rule tree traverser implementing  default object filtering logic.

    Following example demonstrates DataObjectFilter usage in conjuction with
    PynspectFilterParser::

    >>> flt = DataObjectFilter()
    >>> psr = PynspectFilterParser()
    >>> psr.build()
    >>> rule = psr.parse('ID like "e214d2d9"')
    >>> result = flt.filter(rule, test_msg)

    You may use the built-in shortcuts for parsing and compiling rules:

    >>> flt = DataObjectFilter(
    ...     parser   = PynspectFilterParser,
    ...     compiler = IDEAFilterCompiler
    ... )
    >>> rule   = flt.prepare('(Source.IP4 == 188.14.166.39)')
    >>> result = flt.filter(rule, test_msg)

    Rule tree can be created by hand/programatically:

    >>> rule = ComparisonBinOpRule('OP_GT', VariableRule("ConnCount"), IntegerRule(1))
    >>> result = flt.filter(rule, test_msg)
    """

    def __init__(self, parser = None, compiler = None):
        super(DataObjectFilter, self).__init__()
        self.register_function('size', grfcbk_size)
        self.register_function('time', grfcbk_time)

        self.parser   = parser
        self.compiler = compiler

        if callable(self.parser):
            self.parser = self.parser()
            self.parser.build()
        if callable(self.compiler):
            self.compiler = self.compiler()

    def prepare(self, rule):
        """
        Parse and/or compile given rule into rule tree.

        :param rule: Filtering grammar rule.
        :return: Parsed and/or compiled rule.
        """
        if self.parser:
            rule = self.parser.parse(rule)
        if self.compiler:
            rule = self.compiler.compile(rule)
        return rule

    def filter(self, rule, data):
        """
        Apply given filtering rule to given data structure.

        :param pynspect.rules.Rule rule: filtering rule to be checked
        :param any data: data structure to check against rule, ussually dict
        :return: True or False or expression result
        :rtype: bool or any
        """
        return rule.traverse(self, obj = data)

    #---------------------------------------------------------------------------

    def ipv4(self, rule, **kwargs):
        """
        Implementation of :py:func:`pynspect.traversers.RuleTreeTraverser.ipv4` interface.
        """
        return rule.value

    def ipv6(self, rule, **kwargs):
        """
        Implementation of :py:func:`pynspect.traversers.RuleTreeTraverser.ipv6` interface.
        """
        return rule.value

    def datetime(self, rule, **kwargs):
        """
        Implementation of :py:func:`pynspect.traversers.RuleTreeTraverser.datetime` interface.
        """
        return rule.value

    def timedelta(self, rule, **kwargs):
        """
        Implementation of :py:func:`pynspect.traversers.RuleTreeTraverser.timedelta` interface.
        """
        return rule.value

    def integer(self, rule, **kwargs):
        """
        Implementation of :py:func:`pynspect.traversers.RuleTreeTraverser.integer` interface.
        """
        return rule.value

    def float(self, rule, **kwargs):
        """
        Implementation of :py:func:`pynspect.traversers.RuleTreeTraverser.float` interface.
        """
        return rule.value

    def constant(self, rule, **kwargs):
        """
        Implementation of :py:func:`pynspect.traversers.RuleTreeTraverser.constant` interface.
        """
        return rule.value

    def variable(self, rule, **kwargs):
        """
        Implementation of :py:func:`pynspect.traversers.RuleTreeTraverser.variable` interface.
        """
        return jpath_values(kwargs['obj'], rule.value)

    def list(self, rule, **kwargs):
        """
        Implementation of :py:func:`pynspect.traversers.RuleTreeTraverser.list` interface.
        """
        return rule.values()

    def binary_operation_logical(self, rule, left, right, **kwargs):
        """
        Implementation of :py:func:`pynspect.traversers.RuleTreeTraverser.binary_operation_logical` interface.
        """
        return self.evaluate_binop_logical(rule.operation, left, right, **kwargs)

    def binary_operation_comparison(self, rule, left, right, **kwargs):
        """
        Implementation of :py:func:`pynspect.traversers.RuleTreeTraverser.binary_operation_comparison` interface.
        """
        return self.evaluate_binop_comparison(rule.operation, left, right, **kwargs)

    def binary_operation_math(self, rule, left, right, **kwargs):
        """
        Implementation of :py:func:`pynspect.traversers.RuleTreeTraverser.binary_operation_math` interface.
        """
        return self.evaluate_binop_math(rule.operation, left, right, **kwargs)

    def unary_operation(self, rule, right, **kwargs):
        """
        Implementation of :py:func:`pynspect.traversers.RuleTreeTraverser.unary_operation` interface.
        """
        return self.evaluate_unop(rule.operation, right, **kwargs)


#-------------------------------------------------------------------------------


#
# Perform the demonstration.
#
if __name__ == "__main__":

    import pprint

    from pynspect.rules import IntegerRule, VariableRule, ComparisonBinOpRule

    DEMO_DATA   = {"Test": 15, "Attr": "ABC"}
    DEMO_RULE   = ComparisonBinOpRule('OP_GT', VariableRule("Test"), IntegerRule(10))
    DEMO_FILTER = DataObjectFilter()
    pprint.pprint(DEMO_FILTER.filter(DEMO_RULE, DEMO_DATA))
