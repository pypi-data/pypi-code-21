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
This module contains implementation of object representations of filtering
and query language grammar.

There is a separate class defined for each grammar rule. There are following
classes representing all possible constant and variable values (tree leaves,
without child nodes):

* :py:class:`VariableRule`
* :py:class:`ConstantRule`
* :py:class:`IPv4Rule`
* :py:class:`IPv6Rule`
* :py:class:`IntegerRule`
* :py:class:`FloatRule`
* :py:class:`ListRule`

There are following classes representing various binary and unary operations:

* :py:class:`LogicalBinOpRule`
* :py:class:`ComparisonBinOpRule`
* :py:class:`MathBinOpRule`
* :py:class:`UnaryOperationRule`

Desired hierarchical rule tree can be created either programatically, or by
parsing string rules using :py:mod:`pynspect.gparser`.

Working with rule tree is then done via objects implementing rule tree
traverser interface:

* :py:class:`pynspect.traversers.RuleTreeTraverser`

There is a simple example implementation of rule tree traverser capable of
printing rule tree into a formated string:

* :py:class:`pynspect.traversers.PrintingTreeTraverser`

Rule evaluation
^^^^^^^^^^^^^^^

* Logical operations ``and or xor not exists``

  There is no special handling for operands of logical operations. Operand(s) are
  evaluated in logical expression exactly as they are received, there is no
  mangling involved.

* Comparison operations

    All comparison operations are designed to work with lists as both operands.
    This is because :py:func:`pynspect.jpath.jpath_values` function is
    used to retrieve variable values and this function always returns list.

    * Operation: ``is``

      Like in the case of logical operations, there is no mangling involved when
      evaluating this operation. Both operands are compared using Python`s native
      ``is`` operation and result is returned.

    * Operation: ``in``

      In this case left operand is iterated and each value is compared using Python`s
      native ``in`` operation with right operand. First ``True`` result wins and
      operation immediatelly returns ``True``, ``False`` is returned otherwise.

    * Any other operation: ``like eq ne gt ge lt le``

      In case of this operation both of the operands are iterated and each one is
      compared with each other. First ``True`` result wins and operation immediatelly
      returns ``True``, ``False`` is returned otherwise.

    * Math operations: ``+ - * / %``

      Current math operation implementation supports following options:

        * Both operands are lists of the same length. In this case corresponding
          elements at certain position within the list are evaluated with given
          operation. Result is a list.

        * One of the operands is a list, second is scalar value or list of the
          size 1. In this case given operation is evaluated with each element of
          the longer list. Result is a list.

        * Operands are lists of the different size. This option is **forbidden**
          and the result is ``None``.

"""


__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


class FilteringRuleException(Exception):
    """
    Custom filtering rule specific exception.

    This exception will be thrown on module specific errors.
    """
    def __init__(self, description):
        super(FilteringRuleException).__init__()
        self.description = description

    def __str__(self):
        return repr(self.description)


class Rule(object):
    """
    Base class for all filter tree rules.
    """
    def traverse(self, traverser, **kwargs):
        """
        Mandatory interface for traversing the whole rule tree. This method must
        call apropriate method of given traverser object with apropriate arguments.
        The optional ``kwargs`` are passed down to traverser callback as additional
        arguments and can be used to provide additional data or context.

        :param pynspect.rules.RuleTreeTraverser traverser: Traverser object providing appropriate interface.
        :param dict kwargs: Additional optional keyword arguments to be passed down to traverser callback.
        """
        raise NotImplementedError()


class ValueRule(Rule):
    """
    Base class for all filter tree value rules.
    """
    def __init__(self, value):
        """
        Initialize the rule with given value.

        :param value: Value for the rule.
        """
        self.value = value

    def __str__(self):
        return '{}'.format(self.value)


class VariableRule(ValueRule):
    """
    Class representing filtering expression variables.
    """
    def __repr__(self):
        return "VARIABLE({})".format(repr(self.value))

    def traverse(self, traverser, **kwargs):
        """
        Implementation of mandatory interface for traversing the whole rule tree.
        This method will call the implementation of :py:func:`pynspect.rules.RuleTreeTraverser.variable`
        method with reference to ``self`` instance as first argument. The optional
        ``kwargs`` are passed down to traverser callback as additional arguments
        and can be used to provide additional data or context.

        :param pynspect.rules.RuleTreeTraverser traverser: Traverser object providing appropriate interface.
        :param dict kwargs: Additional optional keyword arguments to be passed down to traverser callback.
        """
        return traverser.variable(self, **kwargs)


class ConstantRule(ValueRule):
    """
    Class representing filtering expression string constants.
    """
    def __str__(self):
        return '"{}"'.format(self.value)

    def __repr__(self):
        return "CONSTANT({})".format(repr(self.value))

    def traverse(self, traverser, **kwargs):
        """
        Implementation of mandatory interface for traversing the whole rule tree.
        This method will call the implementation of :py:func:`pynspect.rules.RuleTreeTraverser.constant`
        method with reference to ``self`` instance as first argument. The optional
        ``kwargs`` are passed down to traverser callback as additional arguments
        and can be used to provide additional data or context.

        :param pynspect.rules.RuleTreeTraverser traverser: Traverser object providing appropriate interface.
        :param dict kwargs: Additional optional keyword arguments to be passed down to traverser callback.
        """
        return traverser.constant(self, **kwargs)


class IPV4Rule(ConstantRule):
    """
    Class representing filtering expression IPv4 address/range/network constants.
    """
    def __str__(self):
        return '{}'.format(self.value)

    def __repr__(self):
        return "IPV4({})".format(repr(self.value))

    def traverse(self, traverser, **kwargs):
        """
        Implementation of mandatory interface for traversing the whole rule tree.
        This method will call the implementation of :py:func:`pynspect.rules.RuleTreeTraverser.ipv4`
        method with reference to ``self`` instance as first argument. The optional
        ``kwargs`` are passed down to traverser callback as additional arguments
        and can be used to provide additional data or context.

        :param pynspect.rules.RuleTreeTraverser traverser: Traverser object providing appropriate interface.
        :param dict kwargs: Additional optional keyword arguments to be passed down to traverser callback.
        """
        return traverser.ipv4(self, **kwargs)


class IPV6Rule(ConstantRule):
    """
    Class representing filtering expression IPv6 address/range/network constants.
    """
    def __str__(self):
        return '{}'.format(self.value)

    def __repr__(self):
        return "IPV6({})".format(repr(self.value))

    def traverse(self, traverser, **kwargs):
        """
        Implementation of mandatory interface for traversing the whole rule tree.
        This method will call the implementation of :py:func:`pynspect.rules.RuleTreeTraverser.ipv6`
        method with reference to ``self`` instance as first argument. The optional
        ``kwargs`` are passed down to traverser callback as additional arguments
        and can be used to provide additional data or context.

        :param pynspect.rules.RuleTreeTraverser traverser: Traverser object providing appropriate interface.
        :param dict kwargs: Additional optional keyword arguments to be passed down to traverser callback.
        """
        return traverser.ipv6(self, **kwargs)


class DatetimeRule(ConstantRule):
    """
    Class representing filtering expression datetime constants.
    """
    def __str__(self):
        return '{}'.format(self.value)

    def __repr__(self):
        return "DATETIME({})".format(repr(self.value))

    def traverse(self, traverser, **kwargs):
        """
        Implementation of mandatory interface for traversing the whole rule tree.
        This method will call the implementation of :py:func:`pynspect.rules.RuleTreeTraverser.datetime`
        method with reference to ``self`` instance as first argument. The optional
        ``kwargs`` are passed down to traverser callback as additional arguments
        and can be used to provide additional data or context.

        :param pynspect.rules.RuleTreeTraverser traverser: Traverser object providing appropriate interface.
        :param dict kwargs: Additional optional keyword arguments to be passed down to traverser callback.
        """
        return traverser.datetime(self, **kwargs)


class TimedeltaRule(ConstantRule):
    """
    Class representing filtering expression timedelta constants.
    """
    def __str__(self):
        return '{}'.format(self.value)

    def __repr__(self):
        return "TIMEDELTA({})".format(repr(self.value))

    def traverse(self, traverser, **kwargs):
        """
        Implementation of mandatory interface for traversing the whole rule tree.
        This method will call the implementation of :py:func:`pynspect.rules.RuleTreeTraverser.timedelta`
        method with reference to ``self`` instance as first argument. The optional
        ``kwargs`` are passed down to traverser callback as additional arguments
        and can be used to provide additional data or context.

        :param pynspect.rules.RuleTreeTraverser traverser: Traverser object providing appropriate interface.
        :param dict kwargs: Additional optional keyword arguments to be passed down to traverser callback.
        """
        return traverser.timedelta(self, **kwargs)


class NumberRule(ConstantRule):
    """
    Base class for all filtering expression numerical constants.
    """
    def __str__(self):
        return '{}'.format(self.value)


class IntegerRule(NumberRule):
    """
    Class representing filtering expression integer numerical constants.
    """
    def __repr__(self):
        return "INTEGER({})".format(repr(self.value))

    def traverse(self, traverser, **kwargs):
        """
        Implementation of mandatory interface for traversing the whole rule tree.
        This method will call the implementation of :py:func:`pynspect.rules.RuleTreeTraverser.integer`
        method with reference to ``self`` instance as first argument. The optional
        ``kwargs`` are passed down to traverser callback as additional arguments
        and can be used to provide additional data or context.

        :param pynspect.rules.RuleTreeTraverser traverser: Traverser object providing appropriate interface.
        :param dict kwargs: Additional optional keyword arguments to be passed down to traverser callback.
        """
        return traverser.integer(self, **kwargs)


class FloatRule(NumberRule):
    """
    Class representing filtering expression floating point numerical constants.
    """
    def __repr__(self):
        return "FLOAT({})".format(repr(self.value))

    def traverse(self, traverser, **kwargs):
        """
        Implementation of mandatory interface for traversing the whole rule tree.
        This method will call the implementation of :py:func:`pynspect.rules.RuleTreeTraverser.float`
        method with reference to ``self`` instance as first argument. The optional
        ``kwargs`` are passed down to traverser callback as additional arguments
        and can be used to provide additional data or context.

        :param pynspect.rules.RuleTreeTraverser traverser: Traverser object providing appropriate interface.
        :param dict kwargs: Additional optional keyword arguments to be passed down to traverser callback.
        """
        return traverser.float(self, **kwargs)


class ListRule(ValueRule):
    """
    Class representing filtering expression list of constants.
    """
    def __init__(self, rule, next_rule = None):
        """
        Initialize the list with given rule. Optionally add next rule to the list.

        :param pysnpect.rules.Rule rule: Rule to be added to the list.
        :param pysnpect.rules.ListRule next_rule: Next rule in the chain.
        """
        if not isinstance(rule, list):
            rule = [rule]

        super(ListRule, self).__init__(rule)

        if next_rule:
            self.value += next_rule.value

    def __str__(self):
        return '[{}]'.format(', '.join([str(v) for v in self.value]))

    def __repr__(self):
        return "LIST({})".format(', '.join([repr(v) for v in self.value]))

    def values(self):
        """
        Return true values of the rules in the list.
        """
        return [i.value for i in self.value]

    def traverse(self, traverser, **kwargs):
        """
        Implementation of mandatory interface for traversing the whole rule tree.
        This method will call the implementation of :py:func:`pynspect.rules.RuleTreeTraverser.list`
        method with reference to ``self`` instance as first argument. The optional
        ``kwargs`` are passed down to traverser callback as additional arguments
        and can be used to provide additional data or context.

        :param pynspect.rules.RuleTreeTraverser traverser: Traverser object providing appropriate interface.
        :param dict kwargs: Additional optional keyword arguments to be passed down to traverser callback.
        """
        return traverser.list(self, **kwargs)


class OperationRule(Rule):
    """
    Base class for all expression operations (both unary and binary).
    """
    pass


class BinaryOperationRule(OperationRule):
    """
    Base class for all expression binary operations.
    """
    def __init__(self, operation, left, right):
        """
        Initialize the object with operation type and both operands.

        :param str operation: Type of the binary operations.
        :param pynspect.rules.Rule left: Left operation operand.
        :param pynspect.rules.Rule right: Right operation operand.
        """
        self.operation = operation
        self.left = left
        self.right = right

    def __str__(self):
        return "({} {} {})".format(str(self.left), str(self.operation), str(self.right))


class LogicalBinOpRule(BinaryOperationRule):
    """
    Base class for all expression logical binary operations.
    """
    def __repr__(self):
        return "LOGBINOP({} {} {})".format(repr(self.left), str(self.operation), repr(self.right))

    def traverse(self, traverser, **kwargs):
        """
        Implementation of mandatory interface for traversing the whole rule tree.
        This method will call the implementation of :py:func:`pynspect.rules.RuleTreeTraverser.binary_operation_logical`
        method with reference to ``self`` instance as first argument, with the
        result of traversing left subtree as second argument and with the result
        of traversing right subtree as third argument. The optional ``kwargs``
        are passed down to traverser callback as additional arguments and can be
        used to provide additional data or context.

        :param pynspect.rules.RuleTreeTraverser traverser: Traverser object providing appropriate interface.
        :param dict kwargs: Additional optional keyword arguments to be passed down to traverser callback.
        """
        lrt = self.left.traverse(traverser, **kwargs)
        rrt = self.right.traverse(traverser, **kwargs)
        return traverser.binary_operation_logical(self, lrt, rrt, **kwargs)


class ComparisonBinOpRule(BinaryOperationRule):
    """
    Base class for all expression comparison binary operations.
    """
    def __repr__(self):
        return "COMPBINOP({} {} {})".format(repr(self.left), str(self.operation), repr(self.right))

    def traverse(self, traverser, **kwargs):
        """
        Implementation of mandatory interface for traversing the whole rule tree.
        This method will call the implementation of :py:func:`pynspect.rules.RuleTreeTraverser.binary_operation_comparison`
        method with reference to ``self`` instance as first argument, with the
        result of traversing left subtree as second argument and with the result
        of traversing right subtree as third argument. The optional ``kwargs``
        are passed down to traverser callback as additional arguments and can be
        used to provide additional data or context.

        :param pynspect.rules.RuleTreeTraverser traverser: Traverser object providing appropriate interface.
        :param dict kwargs: Additional optional keyword arguments to be passed down to traverser callback.
        """
        lrt = self.left.traverse(traverser, **kwargs)
        rrt = self.right.traverse(traverser, **kwargs)
        return traverser.binary_operation_comparison(self, lrt, rrt, **kwargs)


class MathBinOpRule(BinaryOperationRule):
    """
    Base class for all expression mathematical binary operations.
    """
    def __repr__(self):
        return "MATHBINOP({} {} {})".format(repr(self.left), str(self.operation), repr(self.right))

    def traverse(self, traverser, **kwargs):
        """
        Implementation of mandatory interface for traversing the whole rule tree.
        This method will call the implementation of :py:func:`pynspect.rules.RuleTreeTraverser.binary_operation_math`
        method with reference to ``self`` instance as first argument, with the
        result of traversing left subtree as second argument and with the result
        of traversing right subtree as third argument. The optional ``kwargs``
        are passed down to traverser callback as additional arguments and can be
        used to provide additional data or context.

        :param pynspect.rules.RuleTreeTraverser traverser: Traverser object providing appropriate interface.
        :param dict kwargs: Additional optional keyword arguments to be passed down to traverser callback.
        """
        lrt = self.left.traverse(traverser, **kwargs)
        rrt = self.right.traverse(traverser, **kwargs)
        return traverser.binary_operation_math(self, lrt, rrt, **kwargs)


class UnaryOperationRule(OperationRule):
    """
    Base class for all expression unary operations.
    """
    def __init__(self, operation, operand):
        """
        Initialize the object with operation type operand.

        :param str operation: Type of the binary operations.
        :param pynspect.rules.Rule operand: Operation operand.
        """
        self.operation = operation
        self.right = operand

    def __str__(self):
        return "({} {})".format(str(self.operation), str(self.right))

    def __repr__(self):
        return "UNOP({} {})".format(str(self.operation), repr(self.right))

    def traverse(self, traverser, **kwargs):
        """
        Implementation of mandatory interface for traversing the whole rule tree.
        This method will call the implementation of :py:func:`pynspect.rules.RuleTreeTraverser.binary_operation_logical`
        method with reference to ``self`` instance as first argument and with the
        result of traversing left subtree as second argument. The optional ``kwargs``
        are passed down to traverser callback as additional arguments and can be
        used to provide additional data or context.

        :param pynspect.rules.RuleTreeTraverser traverser: Traverser object providing appropriate interface.
        :param dict kwargs: Additional optional keyword arguments to be passed down to traverser callback.
        """
        rrt = self.right.traverse(traverser, **kwargs)
        return traverser.unary_operation(self, rrt, **kwargs)


class FunctionRule(Rule):
    """
    Base class for all expression binary operations.
    """
    def __init__(self, function, *args):
        """
        Initialize the object with function name and arguments.

        :param str function: Name of the function.
        :param args: Optional function arguments.
        """
        self.function = function
        self.args = args

    def __str__(self):
        return "{}{}".format(str(self.function), str(self.args))

    def __repr__(self):
        return "FUNCTION({}{})".format(str(self.function), repr(self.args))

    def traverse(self, traverser, **kwargs):
        """
        Implementation of mandatory interface for traversing the whole rule tree.
        This method will call the implementation of :py:func:`pynspect.rules.RuleTreeTraverser.binary_operation_logical`
        method with reference to ``self`` instance as first argument and with the
        result of traversing left subtree as second argument. The optional ``kwargs``
        are passed down to traverser callback as additional arguments and can be
        used to provide additional data or context.

        :param pynspect.rules.RuleTreeTraverser traverser: Traverser object providing appropriate interface.
        :param dict kwargs: Additional optional keyword arguments to be passed down to traverser callback.
        """
        art = []
        for arg in self.args:
            art.append(arg.traverse(traverser, **kwargs))
        return traverser.function(self, art, **kwargs)

#-------------------------------------------------------------------------------


#
# Perform the demonstration.
#
if __name__ == "__main__":

    print("* Rule usage:")
    RULE_VAR = VariableRule("Test")
    print("STR:  {}".format(str(RULE_VAR)))
    print("REPR: {}".format(repr(RULE_VAR)))
    RULE_CONST = ConstantRule("constant")
    print("STR:  {}".format(str(RULE_CONST)))
    print("REPR: {}".format(repr(RULE_CONST)))
    RULE_IPV4 = IPV4Rule("127.0.0.1")
    print("STR:  {}".format(str(RULE_IPV4)))
    print("REPR: {}".format(repr(RULE_IPV4)))
    RULE_IPV6 = IPV6Rule("::1")
    print("STR:  {}".format(str(RULE_IPV6)))
    print("REPR: {}".format(repr(RULE_IPV6)))
    RULE_DATETIME = DatetimeRule("2017-01-01T12:00:00Z")
    print("STR:  {}".format(str(RULE_DATETIME)))
    print("REPR: {}".format(repr(RULE_DATETIME)))
    RULE_TIMEDELTA = TimedeltaRule(3600.30)
    print("STR:  {}".format(str(RULE_TIMEDELTA)))
    print("REPR: {}".format(repr(RULE_TIMEDELTA)))
    RULE_INTEGER = IntegerRule(15)
    print("STR:  {}".format(str(RULE_INTEGER)))
    print("REPR: {}".format(repr(RULE_INTEGER)))
    RULE_FLOAT = FloatRule(15.5)
    print("STR:  {}".format(str(RULE_FLOAT)))
    print("REPR: {}".format(repr(RULE_FLOAT)))
    RULE_BINOP_L = LogicalBinOpRule('OP_OR', RULE_VAR, RULE_INTEGER)
    print("STR:  {}".format(str(RULE_BINOP_L)))
    print("REPR: {}".format(repr(RULE_BINOP_L)))
    RULE_BINOP_C = ComparisonBinOpRule('OP_GT', RULE_VAR, RULE_INTEGER)
    print("STR:  {}".format(str(RULE_BINOP_C)))
    print("REPR: {}".format(repr(RULE_BINOP_C)))
    RULE_BINOP_M = MathBinOpRule('OP_PLUS', RULE_VAR, RULE_INTEGER)
    print("STR:  {}".format(str(RULE_BINOP_M)))
    print("REPR: {}".format(repr(RULE_BINOP_M)))
    RULE_BINOP = LogicalBinOpRule('OP_OR', ComparisonBinOpRule('OP_GT', MathBinOpRule('OP_PLUS', VariableRule("Test"), IntegerRule(10)), IntegerRule(20)), ComparisonBinOpRule('OP_LT', VariableRule("Test"), IntegerRule(5)))
    print("STR:  {}".format(str(RULE_BINOP)))
    print("REPR: {}".format(repr(RULE_BINOP)))
    RULE_UNOP = UnaryOperationRule('OP_NOT', RULE_VAR)
    print("STR:  {}".format(str(RULE_UNOP)))
    print("REPR: {}".format(repr(RULE_UNOP)))
