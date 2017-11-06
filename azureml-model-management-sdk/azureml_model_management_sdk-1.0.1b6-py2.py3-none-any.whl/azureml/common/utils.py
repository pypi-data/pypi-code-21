# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t; python-indent: 4 -*-

from __future__ import absolute_import
from six import get_function_code, get_function_globals, PY2, text_type

import types
import re
import inspect

from azureml.__version__ import __version__ as _sdk_version

def to_camel_case(token, prefix=''):
    if token is None:
        return ''

    # starts with numeric
    token = prefix + token if token[0].isdigit() else token
    components = re.sub('[^0-9a-zA-Z]+', '_', token).split('_')

    return ''.join(x.title() for x in components)


def function_beget(fn, fn_name, fn_args, doc=''):
    """
    Create a dynamic function object.

    :param fn: The base function.
    :param fn_name: The function name.
    :param fn_args: The function arguments in a list.
    :param doc: The doc string for the function.
    :return: The new function.
    """

    if PY2:
        co = fn.func_code

        if isinstance(fn_name, text_type):
            fn_name = fn_name.encode('utf8')

        for i in range(len(fn_args)):
            if isinstance(fn_args[i], text_type):
                fn_args[i] = fn_args[i].encode('utf8')

        f_code = types.CodeType(len(fn_args),
                                co.co_nlocals,
                                co.co_stacksize,
                                co.co_flags,
                                co.co_code,
                                co.co_consts,
                                co.co_names,
                                tuple(fn_args),
                                co.co_filename,
                                fn_name,
                                co.co_firstlineno,
                                co.co_lnotab,
                                co.co_freevars,
                                co.co_cellvars)
    else:
        f_code = types.CodeType(len(fn_args),
                                get_function_code(fn).co_kwonlyargcount,
                                get_function_code(fn).co_nlocals,
                                get_function_code(fn).co_stacksize,
                                get_function_code(fn).co_flags,
                                get_function_code(fn).co_code,
                                get_function_code(fn).co_consts,
                                get_function_code(fn).co_names,
                                tuple(fn_args),
                                get_function_code(fn).co_filename,
                                fn_name,
                                get_function_code(fn).co_firstlineno,
                                get_function_code(fn).co_lnotab)

    fn = types.FunctionType(f_code, get_function_globals(fn), fn_name)
    fn.__doc__ = doc

    return fn


def function_args(fn):
    """
    Shim `getfullargspe/getargspec` between PY3 and P2
    :param function fn: The function to extract arguments from.
    :return: ordered list of function arguments.
    """

    return inspect.getargspec(fn).args if PY2 \
        else inspect.getfullargspec(fn).args


def to_self_execution_block(fn, output=None):
    """
    A self-executing named function code block from function handle.

    Stringify an immediately invoked function expression that calls itself.

    Turn this function handle:

    def run(x, y):
       return x + y

    Into this:

    "def run(x, y):
       return x + y
    run(x, y)"

    :param fn: THe function
    :param output: The excepted return value.
    :return: A immediately invoked function expression as a string.
    """

    # function arguments (argument order is important!)
    inputs = function_args(fn)

    # function definition as source code
    src = inspect.getsource(fn).lstrip()

    # build IIFE function call with arguments (ex) `run(input)
    args = ', '.join(str(item) for item in inputs)
    call = fn.__name__ + '(' + args + ')'

    # output assignment to function call (ex) `output_name = run(input)`
    call = output + ' = ' + call if output else call

    return src + '\n' + call


def get_sdk_version():
    return _sdk_version
