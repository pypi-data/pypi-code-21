# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
"""Condition evaluator."""

import operator
from collections import deque
from logging import getLogger

from .binding_accessor import BindingAccessor
from .exceptions import SqreenException
from .utils import is_string

LOGGER = getLogger(__name__)


class ConditionError(SqreenException):
    """Base class for condition errors."""


class ConditionValueError(ConditionError):
    """Exception raised when the condition is invalid."""


class ConditionRecursionError(ConditionError):
    """Exception raised when the condition is too deeply nested."""


def hash_value_includes(value, iterable, min_value_size, max_iterations=1000):
    """Check whether a nested iterable value is included into a string.

    The iterable can be a combination of dicts and lists. The argument
    min_value_size  is used to avoid comparison on small strings: For example,
    there is no possible SQL injection below 8 characters.
    """
    iteration = 0

    # Early stop.
    if iterable is None:
        return False

    if not is_string(value) and isinstance(value, bytes):
        value = str(value)

    if isinstance(iterable, dict):
        remaining_iterables = deque(iterable.values())
    else:
        remaining_iterables = deque(iterable)

    while remaining_iterables:

        iteration += 1
        # If we have a very big or nested iterable, return True to execute the
        # rule.
        if iteration >= max_iterations:
            return True

        iterable = remaining_iterables.popleft()

        # If we get an iterable, add it to the list of remaining iterables.
        if isinstance(iterable, dict):
            remaining_iterables.extend(iterable.values())
        elif isinstance(iterable, list):
            remaining_iterables.extend(iterable)
        else:
            # Convert and check the value.
            if not is_string(iterable):
                iterable = str(iterable)
            if len(iterable) >= min_value_size and iterable in value:
                return True

    return False


def hash_key_includes(patterns, iterable, min_value_size, max_iterations=1000):
    """Check whether a nested iterable key matches a pattern.

    The iterable can be a combination of dicts and lists. The argument
    min_value_size is used to avoid comparison on small strings: for example,
    there is no possible MongoDB injection below 1 characters.
    """
    iteration = 0

    # Early stop.
    if not isinstance(iterable, dict):
        return False

    remaining_iterables = deque([iterable])

    while remaining_iterables:

        iteration += 1
        # If we have a very big or nested iterable, return True to execute the
        # rule.
        if iteration >= max_iterations:
            return True

        iterable_value = remaining_iterables.popleft()

        if not iterable_value:
            continue

        if isinstance(iterable_value, list):
            remaining_iterables.extend(iterable_value)
        elif isinstance(iterable_value, dict):
            # Process the keys.
            for key, value in iterable_value.items():

                if isinstance(value, dict):
                    remaining_iterables.extend(iterable_value.values())
                elif isinstance(value, list):
                    remaining_iterables.extend(value)
                elif len(key) >= min_value_size and key in patterns:
                    return True

    return False


def and_(*args):
    """Return the boolean value of "and" between all values."""
    return all(args)


def or_(*args):
    """Return the boolean value of "or"" between all values."""
    return any(args)


OPERATORS = {
    '%and': and_,
    '%or': or_,
    '%equals': operator.eq,
    '%not_equals': operator.ne,
    '%gt': operator.gt,
    '%gte': operator.ge,
    '%lt': operator.lt,
    '%lte': operator.le,
    '%include': operator.contains,
    '%hash_val_include': hash_value_includes,
    '%hash_key_include': hash_key_includes
}

OPERATORS_ARITY = {
    '%equals': 2,
    '%not_equals': 2,
    '%gt': 2,
    '%gte': 2,
    '%lt': 2,
    '%lte': 2,
    '%include': 2,
    '%hash_val_include': 3,
    '%hash_key_include': 3
}


def is_condition_empty(condition):
    """Return True if the condition is no-op, False otherwise."""
    if condition is None:
        return True
    elif isinstance(condition, bool):
        return False
    elif isinstance(condition, dict):
        return len(condition) == 0
    else:
        LOGGER.warning("Invalid precondition type: %r", condition)
        return True


def compile_condition(condition, level):
    """Compile a raw condition.

    Values are replaced by BindingAccessor instances and operator validity and
    arity are checked.
    """
    if level <= 0:
        raise ConditionRecursionError("compile recursion depth exceeded")

    if isinstance(condition, bool):
        return condition

    compiled = {}

    for _operator, values in condition.items():

        # Check operator validity.
        if _operator not in OPERATORS:
            raise ConditionValueError("unkown operator {!r}".format(_operator))

        # Check operator arity.
        arity = OPERATORS_ARITY.get(_operator, len(values))
        if len(values) != arity:
            raise ConditionValueError(
                "bad arity for operator {!r}: expected {}, got {}".format(
                    _operator, arity, len(values)))

        # Check types.
        if not isinstance(values, list):
            raise ConditionValueError("values should be an array, got {}"
                                      .format(type(values)))

        compiled_values = []
        for value in values:
            if isinstance(value, bool):
                compiled_values.append(value)
            elif isinstance(value, dict):
                compiled_values.append(compile_condition(value, level - 1))
            elif is_string(value):
                compiled_values.append(BindingAccessor(value))
            else:
                compiled_values.append(BindingAccessor(str(value)))

        compiled[_operator] = compiled_values

    return compiled


def resolve_and_evaluate(condition, level, **kwargs):
    """Take a compiled condition, resolve values and evaluate the result."""
    resolved = resolve(condition, level, **kwargs)
    result = evaluate(resolved)
    return result


def resolve(condition, level, **kwargs):
    """Take a compiled condition with binding accessors and resolve them."""
    if level <= 0:
        raise ConditionRecursionError("resolve recursion depth exceeded")

    if isinstance(condition, bool):
        return condition

    resolved = {}

    for _operator, values in condition.items():

        resolved_values = []

        for value in values:

            if isinstance(value, bool):
                resolved_values.append(value)
            elif isinstance(value, dict):
                resolved_values.append(
                    resolve_and_evaluate(value, level - 1, **kwargs))
            else:
                resolved_values.append(value.resolve(**kwargs))

        resolved[_operator] = resolved_values

    return resolved


def evaluate(resolved_condition):
    """Evaluate a resolved condition and return the result."""
    if isinstance(resolved_condition, bool):
        return resolved_condition

    elif isinstance(resolved_condition, dict):

        result = True

        # Implicit and between operators.
        for operator_name, values in resolved_condition.items():
            operator_func = OPERATORS[operator_name]

            result = result and operator_func(*values)

            # Break early.
            if result is False:
                return result

        return result
    else:
        raise ConditionValueError("invalid condition type: {!r}"
                                  .format(resolved_condition))


class ConditionEvaluator(object):
    """Evaluate a condition, resolving literals using BindingAccessor.

    {"%and": ["true", "true"]} -> true
    {"%or": ["true", "false"]} -> true
    {"%and": ["false", "true"]} -> false
    {"%equal": ["coucou", "#.args[0]"]} -> "coucou" == args[0]
    {"%hash_val_include": ["toto is a small guy", "#.request_params", 0]} ->
        true if one value of request params in included
        in the sentence 'toto is a small guy'.

    Combined expressions:
    { "%or":
        [
            {"%hash_val_include": ["AAA", "#.request_params", 0]},
            {"%hash_val_include": ["BBB", "#.request_params", 0]},
        ]
    }
    will return true if one of the request_params includes either AAA or BBB.
    """

    def __init__(self, condition):
        self.raw_condition = condition
        self.compiled = compile_condition(condition, 10)

    def evaluate(self, **kwargs):
        """Evaluate the compiled condition and return the result."""
        return resolve_and_evaluate(self.compiled, level=10, **kwargs)

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.raw_condition)
