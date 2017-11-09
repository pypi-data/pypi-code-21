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
This module contains implementation of object representations of rule tree traversers,
that are supposed to be used to work with rule tree structures.

The base implementation and interface definition is can be found in following class:

* :py:class:`pynspect.traversers.BaseRuleTreeTraverser`

There is a simple example implementation of rule tree traverser capable of printing
rule tree into a formated string:

* :py:class:`pynspect.traversers.PrintingTreeTraverser`

There is also a base class for implementing filtering rule tree traversers, that
provides many usefull tools and features and can be used to implement traversers
that actually do something:

* :py:class:`pynspect.traversers.BaseFilteringTreeTraverser`

"""


__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import re
import collections
import datetime
import calendar

from pynspect.rules import FilteringRuleException


class BaseRuleTreeTraverser(object):
    """
    Base class and interface definition for all rule tree traversers. This is a
    mandatory interface that is required for an object to be able to traverse
    through given :py:class:`pynspect.rules.Rule` tree.
    """
    def ipv4(self, rule, **kwargs):
        """
        Callback method for rule tree traversing. Will be called at proper time
        from :py:class:`pynspect.rules.IPV4Rule.traverse` method.

        :param pynspect.rules.Rule rule: Reference to rule.
        :param dict kwargs: Optional callback arguments.
        """
        raise NotImplementedError()

    def ipv6(self, rule, **kwargs):
        """
        Callback method for rule tree traversing. Will be called at proper time
        from :py:class:`pynspect.rules.IPV6Rule.traverse` method.

        :param pynspect.rules.Rule rule: Reference to rule.
        :param dict kwargs: Optional callback arguments.
        """
        raise NotImplementedError()

    def datetime(self, rule, **kwargs):
        """
        Callback method for rule tree traversing. Will be called at proper time
        from :py:class:`pynspect.rules.DatetimeRule.traverse` method.

        :param pynspect.rules.Rule rule: Reference to rule.
        :param dict kwargs: Optional callback arguments.
        """
        raise NotImplementedError()

    def timedelta(self, rule, **kwargs):
        """
        Callback method for rule tree traversing. Will be called at proper time
        from :py:class:`pynspect.rules.TimedeltaRule.traverse` method.

        :param pynspect.rules.Rule rule: Reference to rule.
        :param dict kwargs: Optional callback arguments.
        """
        raise NotImplementedError()

    def integer(self, rule, **kwargs):
        """
        Callback method for rule tree traversing. Will be called at proper time
        from :py:class:`pynspect.rules.IntegerRule.traverse` method.

        :param pynspect.rules.Rule rule: Reference to rule.
        :param dict kwargs: Optional callback arguments.
        """
        raise NotImplementedError()

    def float(self, rule, **kwargs):
        """
        Callback method for rule tree traversing. Will be called at proper time
        from :py:class:`pynspect.rules.FloatRule.traverse` method.

        :param pynspect.rules.Rule rule: Reference to rule.
        :param dict kwargs: Optional callback arguments.
        """
        raise NotImplementedError()

    def constant(self, rule, **kwargs):
        """
        Callback method for rule tree traversing. Will be called at proper time
        from :py:class:`pynspect.rules.ConstantRule.traverse` method.

        :param pynspect.rules.Rule rule: Reference to rule.
        :param dict kwargs: Optional callback arguments.
        """
        raise NotImplementedError()

    def variable(self, rule, **kwargs):
        """
        Callback method for rule tree traversing. Will be called at proper time
        from :py:class:`pynspect.rules.VariableRule.traverse` method.

        :param pynspect.rules.Rule rule: Reference to rule.
        :param dict kwargs: Optional callback arguments.
        """
        raise NotImplementedError()

    def list(self, rule, **kwargs):
        """
        Callback method for rule tree traversing. Will be called at proper time
        from :py:class:`pynspect.rules.ListRule.traverse` method.

        :param pynspect.rules.Rule rule: Reference to rule.
        :param dict kwargs: Optional callback arguments.
        """
        raise NotImplementedError()

    def binary_operation_logical(self, rule, left, right, **kwargs):
        """
        Callback method for rule tree traversing. Will be called at proper time
        from :py:class:`pynspect.rules.LogicalBinOpRule.traverse` method.

        :param pynspect.rules.Rule rule: Reference to rule.
        :param left: Left operand for operation.
        :param right: right operand for operation.
        :param dict kwargs: Optional callback arguments.
        """
        raise NotImplementedError()

    def binary_operation_comparison(self, rule, left, right, **kwargs):
        """
        Callback method for rule tree traversing. Will be called at proper time
        from :py:class:`pynspect.rules.ComparisonBinOpRule.traverse` method.

        :param pynspect.rules.Rule rule: Reference to rule.
        :param left: Left operand for operation.
        :param right: right operand for operation.
        :param dict kwargs: Optional callback arguments.
        """
        raise NotImplementedError()

    def binary_operation_math(self, rule, left, right, **kwargs):
        """
        Callback method for rule tree traversing. Will be called at proper time
        from :py:class:`pynspect.rules.MathBinOpRule.traverse` method.

        :param pynspect.rules.Rule rule: Reference to rule.
        :param left: Left operand for operation.
        :param right: right operand for operation.
        :param dict kwargs: Optional callback arguments.
        """
        raise NotImplementedError()

    def unary_operation(self, rule, right, **kwargs):
        """
        Callback method for rule tree traversing. Will be called at proper time
        from :py:class:`pynspect.rules.UnaryOperationRule.traverse` method.

        :param pynspect.rules.Rule rule: Reference to rule.
        :param right: right operand for operation.
        :param dict kwargs: Optional callback arguments.
        """
        raise NotImplementedError()

    def function(self, rule, args, **kwargs):
        """
        Callback method for rule tree traversing. Will be called at proper time
        from :py:class:`pynspect.rules.FunctionRule.traverse` method.

        :param pynspect.rules.Rule rule: Reference to rule.
        :param args: Optional function arguments.
        :param dict kwargs: Optional callback arguments.
        """
        raise NotImplementedError()


#-------------------------------------------------------------------------------


class PrintingTreeTraverser(BaseRuleTreeTraverser):
    """
    Demonstation of simple rule tree traverser - printing traverser.
    """
    def ipv4(self, rule, **kwargs):
        """
        Callback method for rule tree traversing. Will be called at proper time
        from :py:class:`pynspect.rules.IPV4Rule.traverse` method.

        :param pynspect.rules.Rule rule: Reference to rule.
        :param dict kwargs: Optional callback arguments.
        """
        return "IPV4({})".format(rule.value)

    def ipv6(self, rule, **kwargs):
        """
        Callback method for rule tree traversing. Will be called at proper time
        from :py:class:`pynspect.rules.IPV6Rule.traverse` method.

        :param pynspect.rules.Rule rule: Reference to rule.
        :param dict kwargs: Optional callback arguments.
        """
        return "IPV6({})".format(rule.value)

    def datetime(self, rule, **kwargs):
        """
        Callback method for rule tree traversing. Will be called at proper time
        from :py:class:`pynspect.rules.DatetimeRule.traverse` method.

        :param pynspect.rules.Rule rule: Reference to rule.
        :param dict kwargs: Optional callback arguments.
        """
        return "DATETIME({})".format(rule.value)

    def timedelta(self, rule, **kwargs):
        """
        Callback method for rule tree traversing. Will be called at proper time
        from :py:class:`pynspect.rules.TimedeltaRule.traverse` method.

        :param pynspect.rules.Rule rule: Reference to rule.
        :param dict kwargs: Optional callback arguments.
        """
        return "TIMEDELTA({})".format(rule.value)

    def integer(self, rule, **kwargs):
        """
        Callback method for rule tree traversing. Will be called at proper time
        from :py:class:`pynspect.rules.IntegerRule.traverse` method.

        :param pynspect.rules.Rule rule: Reference to rule.
        :param dict kwargs: Optional callback arguments.
        """
        return "INTEGER({})".format(rule.value)

    def float(self, rule, **kwargs):
        """
        Callback method for rule tree traversing. Will be called at proper time
        from :py:class:`pynspect.rules.FloatRule.traverse` method.

        :param pynspect.rules.Rule rule: Reference to rule.
        :param dict kwargs: Optional callback arguments.
        """
        return "FLOAT({})".format(rule.value)

    def constant(self, rule, **kwargs):
        """
        Callback method for rule tree traversing. Will be called at proper time
        from :py:class:`pynspect.rules.ConstantRule.traverse` method.

        :param pynspect.rules.Rule rule: Reference to rule.
        :param dict kwargs: Optional callback arguments.
        """
        return "CONSTANT({})".format(rule.value)

    def variable(self, rule, **kwargs):
        """
        Callback method for rule tree traversing. Will be called at proper time
        from :py:class:`pynspect.rules.VariableRule.traverse` method.

        :param pynspect.rules.Rule rule: Reference to rule.
        :param dict kwargs: Optional callback arguments.
        """
        return "VARIABLE({})".format(rule.value)

    def list(self, rule, **kwargs):
        """
        Callback method for rule tree traversing. Will be called at proper time
        from :py:class:`pynspect.rules.ListRule.traverse` method.

        :param pynspect.rules.Rule rule: Reference to rule.
        :param dict kwargs: Optional callback arguments.
        """
        return "LIST({})".format(', '.join([v.traverse(self, **kwargs) for v in rule.value]))

    def binary_operation_logical(self, rule, left, right, **kwargs):
        """
        Callback method for rule tree traversing. Will be called at proper time
        from :py:class:`pynspect.rules.LogicalBinOpRule.traverse` method.

        :param pynspect.rules.Rule rule: Reference to rule.
        :param left: Left operand for operation.
        :param right: right operand for operation.
        :param dict kwargs: Optional callback arguments.
        """
        return "LOGBINOP({};{};{})".format(rule.operation, left, right)

    def binary_operation_comparison(self, rule, left, right, **kwargs):
        """
        Callback method for rule tree traversing. Will be called at proper time
        from :py:class:`pynspect.rules.ComparisonBinOpRule.traverse` method.

        :param pynspect.rules.Rule rule: Reference to rule.
        :param left: Left operand for operation.
        :param right: right operand for operation.
        :param dict kwargs: Optional callback arguments.
        """
        return "COMPBINOP({};{};{})".format(rule.operation, left, right)

    def binary_operation_math(self, rule, left, right, **kwargs):
        """
        Callback method for rule tree traversing. Will be called at proper time
        from :py:class:`pynspect.rules.MathBinOpRule.traverse` method.

        :param pynspect.rules.Rule rule: Reference to rule.
        :param left: Left operand for operation.
        :param right: right operand for operation.
        :param dict kwargs: Optional callback arguments.
        """
        return "MATHBINOP({};{};{})".format(rule.operation, left, right)

    def unary_operation(self, rule, right, **kwargs):
        """
        Callback method for rule tree traversing. Will be called at proper time
        from :py:class:`pynspect.rules.UnaryOperationRule.traverse` method.

        :param pynspect.rules.Rule rule: Reference to rule.
        :param right: right operand for operation.
        :param dict kwargs: Optional callback arguments.
        """
        return "UNOP({};{})".format(rule.operation, right)

    def function(self, rule, args, **kwargs):
        """
        Callback method for rule tree traversing. Will be called at proper time
        from :py:class:`pynspect.rules.FunctionRule.traverse` method.

        :param pynspect.rules.Rule rule: Reference to rule.
        :param args: Optional function arguments.
        :param dict kwargs: Optional callback arguments.
        """
        return "FUNCTION({};{})".format(rule.function, ','.join(args))


class HTMLTreeTraverser(BaseRuleTreeTraverser):
    """
    Demonstation of simple rule tree traverser - HTML printing traverser.
    """
    def ipv4(self, rule, **kwargs):
        """
        Callback method for rule tree traversing. Will be called at proper time
        from :py:class:`pynspect.rules.IPV4Rule.traverse` method.

        :param pynspect.rules.Rule rule: Reference to rule.
        :param dict kwargs: Optional callback arguments.
        """
        return '<div class="pynspect-rule-constant pynspect-rule-constant-ipv4"><code>{}</code></div>'.format(rule.value)

    def ipv6(self, rule, **kwargs):
        """
        Callback method for rule tree traversing. Will be called at proper time
        from :py:class:`pynspect.rules.IPV6Rule.traverse` method.

        :param pynspect.rules.Rule rule: Reference to rule.
        :param dict kwargs: Optional callback arguments.
        """
        return '<div class="pynspect-rule-constant pynspect-rule-constant-ipv6"><code>{}</code></div>'.format(rule.value)

    def datetime(self, rule, **kwargs):
        """
        Callback method for rule tree traversing. Will be called at proper time
        from :py:class:`pynspect.rules.DatetimeRule.traverse` method.

        :param pynspect.rules.Rule rule: Reference to rule.
        :param dict kwargs: Optional callback arguments.
        """
        return '<div class="pynspect-rule-constant pynspect-rule-constant-datetime"><code>{}</code></div>'.format(rule.value)

    def timedelta(self, rule, **kwargs):
        """
        Callback method for rule tree traversing. Will be called at proper time
        from :py:class:`pynspect.rules.TimedeltaRule.traverse` method.

        :param pynspect.rules.Rule rule: Reference to rule.
        :param dict kwargs: Optional callback arguments.
        """
        return '<div class="pynspect-rule-constant pynspect-rule-constant-timedelta"><code>{}</code></div>'.format(rule.value)

    def integer(self, rule, **kwargs):
        """
        Callback method for rule tree traversing. Will be called at proper time
        from :py:class:`pynspect.rules.IntegerRule.traverse` method.

        :param pynspect.rules.Rule rule: Reference to rule.
        :param dict kwargs: Optional callback arguments.
        """
        return '<div class="pynspect-rule-constant pynspect-rule-constant-integer"><code>{}</code></div>'.format(rule.value)

    def float(self, rule, **kwargs):
        """
        Callback method for rule tree traversing. Will be called at proper time
        from :py:class:`pynspect.rules.FloatRule.traverse` method.

        :param pynspect.rules.Rule rule: Reference to rule.
        :param dict kwargs: Optional callback arguments.
        """
        return '<div class="pynspect-rule-constant pynspect-rule-constant-float"><code>{}</code></div>'.format(rule.value)

    def constant(self, rule, **kwargs):
        """
        Callback method for rule tree traversing. Will be called at proper time
        from :py:class:`pynspect.rules.ConstantRule.traverse` method.

        :param pynspect.rules.Rule rule: Reference to rule.
        :param dict kwargs: Optional callback arguments.
        """
        return '<div class="pynspect-rule-constant pynspect-rule-constant-string"><code>&quot;{}&quot;</code></div>'.format(rule.value)

    def variable(self, rule, **kwargs):
        """
        Callback method for rule tree traversing. Will be called at proper time
        from :py:class:`pynspect.rules.VariableRule.traverse` method.

        :param pynspect.rules.Rule rule: Reference to rule.
        :param dict kwargs: Optional callback arguments.
        """
        return '<div class="pynspect-rule-variable"><kbd>{}</kbd></div>'.format(rule.value)

    def list(self, rule, **kwargs):
        """
        Callback method for rule tree traversing. Will be called at proper time
        from :py:class:`pynspect.rules.ListRule.traverse` method.

        :param pynspect.rules.Rule rule: Reference to rule.
        :param dict kwargs: Optional callback arguments.
        """
        return '<ul class="pynspect-rule-list">{}</ul>'.format(''.join(['<li class="pynspect-rule-list-item">{}</li>'.format(v.traverse(self, **kwargs)) for v in rule.value]))

    def binary_operation_logical(self, rule, left, right, **kwargs):
        """
        Callback method for rule tree traversing. Will be called at proper time
        from :py:class:`pynspect.rules.LogicalBinOpRule.traverse` method.

        :param pynspect.rules.Rule rule: Reference to rule.
        :param left: Left operand for operation.
        :param right: right operand for operation.
        :param dict kwargs: Optional callback arguments.
        """
        return '<div class="pynspect-rule-operation pynspect-rule-operation-logical"><h3 class="pynspect-rule-operation-name">{}</h3><ul class="pynspect-rule-operation-arguments"><li class="pynspect-rule-operation-argument-left">{}</li><li class="pynspect-rule-operation-argument-right">{}</li></ul></div>'.format(rule.operation, left, right)

    def binary_operation_comparison(self, rule, left, right, **kwargs):
        """
        Callback method for rule tree traversing. Will be called at proper time
        from :py:class:`pynspect.rules.ComparisonBinOpRule.traverse` method.

        :param pynspect.rules.Rule rule: Reference to rule.
        :param left: Left operand for operation.
        :param right: right operand for operation.
        :param dict kwargs: Optional callback arguments.
        """
        return '<div class="pynspect-rule-operation pynspect-rule-operation-comparison"><h3 class="pynspect-rule-operation-name">{}</h3><ul class="pynspect-rule-operation-arguments"><li class="pynspect-rule-operation-argument-left">{}</li><li class="pynspect-rule-operation-argument-right">{}</li></ul></div>'.format(rule.operation, left, right)

    def binary_operation_math(self, rule, left, right, **kwargs):
        """
        Callback method for rule tree traversing. Will be called at proper time
        from :py:class:`pynspect.rules.MathBinOpRule.traverse` method.

        :param pynspect.rules.Rule rule: Reference to rule.
        :param left: Left operand for operation.
        :param right: right operand for operation.
        :param dict kwargs: Optional callback arguments.
        """
        return '<div class="pynspect-rule-operation pynspect-rule-operation-math"><h3 class="pynspect-rule-operation-name">{}</h3><ul class="pynspect-rule-operation-arguments"><li class="pynspect-rule-operation-argument-left">{}</li><li class="pynspect-rule-operation-argument-right">{}</li></ul></div>'.format(rule.operation, left, right)

    def unary_operation(self, rule, right, **kwargs):
        """
        Callback method for rule tree traversing. Will be called at proper time
        from :py:class:`pynspect.rules.UnaryOperationRule.traverse` method.

        :param pynspect.rules.Rule rule: Reference to rule.
        :param right: right operand for operation.
        :param dict kwargs: Optional callback arguments.
        """
        return '<div class="pynspect-rule-operation pynspect-rule-operation-unary"><h3 class="pynspect-rule-operation-name">{}</h3><ul class="pynspect-rule-operation-arguments"><li class="pynspect-rule-operation-argument-right">{}</li></ul></div>'.format(rule.operation, right)

    def function(self, rule, args, **kwargs):
        """
        Callback method for rule tree traversing. Will be called at proper time
        from :py:class:`pynspect.rules.FunctionRule.traverse` method.

        :param pynspect.rules.Rule rule: Reference to rule.
        :param args: Optional function arguments.
        :param dict kwargs: Optional callback arguments.
        """
        return '<div class="pynspect-rule-function"><h3 class="pynspect-rule-function-name">{}</h3><ul class="pynspect-rule-function-arguments>{}</ul></div>'.format(rule.function, ''.join(['<li class="pynspect-rule-function-argument">{}</li>'.format(v) for v in args]))


#-------------------------------------------------------------------------------


def _py2_timestamp(val):
    """
    Get unix timestamp value out of given datetime object.

    Implemented for Python2 compatibility purposes.
    """
    return calendar.timegm(val.timetuple()) + val.microsecond / 1000000.0


def _to_numeric(val):
    """
    Helper function for conversion of various data types into numeric representation.
    """
    if isinstance(val, (int, float)):
        return val
    if isinstance(val, datetime.datetime):
        try:
            return val.timestamp()
        except AttributeError:
            # python 2 compatibility
            return _py2_timestamp(val)
    if isinstance(val, datetime.timedelta):
        return val.total_seconds()
    return float(val)


class ListIP(collections.MutableSequence):
    """
    Special list implementation designed to provide special handling of 'IN' operator.
    When item is being compared using 'IN' operator with this list, the IN operation
    is propagated down to each of the items in the list.
    """

    def __init__(self, iterable = None):
        self.data = list()
        if iterable:
            self.extend(iterable)

    def __getitem__(self, val):
        return self.data[val]

    def __delitem__(self, val):
        del self.data[val]

    def __len__(self):
        return len(self.data)

    def __setitem__(self, idx, val):
        self.data[idx] = val

    def insert(self, idx, val):
        self.data.insert(idx, val)

    # Following definitions are not strictly necessary as MutableSequence
    # already defines them, however we can override them by calling to
    # possibly more optimized underlying implementations.

    def __contains__(self, val):
        for value in self.data:
            if val in value:
                return True
        return False

    def index(self, val):
        return self.data.index(val)

    def count(self, val):
        return self.data.count(val)

    def __iter__(self):
        return iter(self.data)

    def reverse(self):
        return self.data.reverse()

    def __reversed__(self):
        return reversed(self.data)

    def pop(self, index=-1):
        return self.data.pop(index)

    def __str__(self):
        return "%s(%s)" % (type(self).__name__, str(self.data))

    def __repr__(self):
        return "%s(%s)" % (type(self).__name__, repr(self.data))


class BaseFilteringTreeTraverser(BaseRuleTreeTraverser):
    """
    Base class for all filtering rule tree traversers.
    """

    binops_logical = {
        'OP_OR':    lambda x, y : x or y,
        'OP_XOR':   lambda x, y : (x and not y) or (not x and y),
        'OP_AND':   lambda x, y : x and y,
        'OP_OR_P':  lambda x, y : x or y,
        'OP_XOR_P': lambda x, y : (x and not y) or (not x and y),
        'OP_AND_P': lambda x, y : x and y,
    }
    """
    Definitions of all logical binary operations.
    """

    binops_comparison = {
        'OP_LIKE': lambda x, y : re.search(y, x),
        'OP_IN':   lambda x, y : x in y,
        'OP_IS':   lambda x, y : x == y,
        'OP_EQ':   lambda x, y : x == y,
        'OP_NE':   lambda x, y : x != y,
        'OP_GT':   lambda x, y : x > y,
        'OP_GE':   lambda x, y : x >= y,
        'OP_LT':   lambda x, y : x < y,
        'OP_LE':   lambda x, y : x <= y,
    }
    """
    Definitions of all comparison binary operations.
    """

    binops_math = {
        'OP_PLUS':   lambda x, y : x + y,
        'OP_MINUS':  lambda x, y : x - y,
        'OP_TIMES':  lambda x, y : x * y,
        'OP_DIVIDE': lambda x, y : x / y,
        'OP_MODULO': lambda x, y : x % y,
    }
    """
    Definitions of all mathematical binary operations.
    """

    unops = {
        'OP_NOT':    lambda x : not x,
        'OP_EXISTS': lambda x : x,
    }
    """
    Definitions of all unary operations.
    """

    def __init__(self):
        self.functions = {}

    def evaluate_binop_logical(self, operation, left, right, **kwargs):
        """
        Evaluate given logical binary operation with given operands.
        """
        if not operation in self.binops_logical:
            raise ValueError("Invalid logical binary operation '{}'".format(operation))
        result = self.binops_logical[operation](left, right)
        return bool(result)

    def evaluate_binop_comparison(self, operation, left, right, **kwargs):
        """
        Evaluate given comparison binary operation with given operands.
        """
        if not operation in self.binops_comparison:
            raise ValueError("Invalid comparison binary operation '{}'".format(operation))
        if left is None or right is None:
            return None
        if not isinstance(left, (list, ListIP)):
            left = [left]
        if not isinstance(right, (list, ListIP)):
            right = [right]
        if not left or not right:
            return None
        if operation in ['OP_IS']:
            res = self.binops_comparison[operation](left, right)
            if res:
                return True
        elif operation in ['OP_IN']:
            for iteml in left:
                res = self.binops_comparison[operation](iteml, right)
                if res:
                    return True
        else:
            for iteml in left:
                if iteml is None:
                    continue
                for itemr in right:
                    if itemr is None:
                        continue
                    res = self.binops_comparison[operation](iteml, itemr)
                    if res:
                        return True
        return False

    def _calculate_vector(self, operation, left, right):
        """
        Calculate vector result from two list operands with given mathematical operation.
        """
        result = []
        if len(right) == 1:
            right = _to_numeric(right[0])
            for iteml in left:
                iteml = _to_numeric(iteml)
                result.append(self.binops_math[operation](iteml, right))
        elif len(left) == 1:
            left = _to_numeric(left[0])
            for itemr in right:
                itemr = _to_numeric(itemr)
                result.append(self.binops_math[operation](left, itemr))
        elif len(left) == len(right):
            for iteml, itemr in zip(left, right):
                iteml = _to_numeric(iteml)
                itemr = _to_numeric(itemr)
                result.append(self.binops_math[operation](iteml, itemr))
        else:
            raise FilteringRuleException("Uneven length of math operation '{}' operands".format(operation))
        return result

    def evaluate_binop_math(self, operation, left, right, **kwargs):
        """
        Evaluate given mathematical binary operation with given operands.
        """
        if not operation in self.binops_math:
            raise ValueError("Invalid math binary operation '{}'".format(operation))
        if left is None or right is None:
            return None
        if not isinstance(left, (list, ListIP)):
            left = [left]
        if not isinstance(right, (list, ListIP)):
            right = [right]
        if not left or not right:
            return None
        try:
            vect = self._calculate_vector(operation, left, right)
            if len(vect) > 1:
                return vect
            return vect[0]
        except:
            return None

    def evaluate_unop(self, operation, right, **kwargs):
        """
        Evaluate given unary operation with given operand.
        """
        if not operation in self.unops:
            raise ValueError("Invalid unary operation '{}'".format(operation))
        if right is None:
            return None
        return self.unops[operation](right)

    #---------------------------------------------------------------------------

    def register_function(self, name, callback):
        """
        Register given callback as filtering rule function with given name.

        :param str name: Name of the function.
        :param callable callback: Function callback.
        """
        self.functions[name] = callback

    def decorate_function(self, name, decorator):
        """
        Decorate function with given name with given decorator.

        :param str name: Name of the function.
        :param callable decorator: Decorator callback.
        """
        self.functions[name] = decorator(self.functions[name])

    def function(self, rule, args, **kwargs):
        """
        Implementation of :py:func:`pynspect.traversers.RuleTreeTraverser.function` interface.
        """
        fname = rule.function
        try:
            return self.functions[fname](args)
        except KeyError:
            raise FilteringRuleException("Invalid function name '{}'".format(fname))


#-------------------------------------------------------------------------------


#
# Perform the demonstration.
#
if __name__ == "__main__":

    from pynspect.rules import IntegerRule, VariableRule, LogicalBinOpRule,\
        UnaryOperationRule, ComparisonBinOpRule, MathBinOpRule

    # Create couple of test rules.
    RULE_VAR     = VariableRule("Test")
    RULE_INTEGER = IntegerRule(15)
    RULE_BINOP_L = LogicalBinOpRule('OP_OR', RULE_VAR, RULE_INTEGER)
    RULE_BINOP_C = ComparisonBinOpRule('OP_GT', RULE_VAR, RULE_INTEGER)
    RULE_BINOP_M = MathBinOpRule('OP_PLUS', RULE_VAR, RULE_INTEGER)
    RULE_BINOP   = LogicalBinOpRule('OP_OR', ComparisonBinOpRule('OP_GT', MathBinOpRule('OP_PLUS', VariableRule("Test"), IntegerRule(10)), IntegerRule(20)), ComparisonBinOpRule('OP_LT', VariableRule("Test"), IntegerRule(5)))
    RULE_UNOP    = UnaryOperationRule('OP_NOT', RULE_VAR)

    print("* Traverser usage:")
    RULE_TRAVERSER = PrintingTreeTraverser()
    print("{}".format(RULE_BINOP_L.traverse(RULE_TRAVERSER)))
    print("{}".format(RULE_BINOP_C.traverse(RULE_TRAVERSER)))
    print("{}".format(RULE_BINOP_M.traverse(RULE_TRAVERSER)))
    print("{}".format(RULE_BINOP.traverse(RULE_TRAVERSER)))
    print("{}".format(RULE_UNOP.traverse(RULE_TRAVERSER)))
