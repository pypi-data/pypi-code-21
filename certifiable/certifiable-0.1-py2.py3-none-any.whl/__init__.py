#!/usr/bin/env python
# -*- coding: latin-1 -*-
#   ____    ____    ____    ______ ______  ____    ______  ____    __      ____
#  /\  _`\ /\  _`\ /\  _`\ /\__  _/\__  _\/\  _`\ /\  _  \/\  _`\ /\ \    /\  _`\
#  \ \ \/\_\ \ \L\_\ \ \L\ \/_/\ \\/_/\ \/\ \ \L\_\ \ \L\ \ \ \L\ \ \ \   \ \ \L\_\
#   \ \ \/_/\ \  _\L\ \ ,  /  \ \ \  \ \ \ \ \  _\/\ \  __ \ \  _ <\ \ \  _\ \  _\L
#    \ \ \L\ \ \ \L\ \ \ \\ \  \ \ \  \_\ \_\ \ \/  \ \ \/\ \ \ \L\ \ \ \L\ \ \ \L\ \
#     \ \____/\ \____/\ \_\ \_\ \ \_\ /\_____\ \_\   \ \_\ \_\ \____/\ \____/\ \____/
#      \/___/  \/___/  \/_/\/ /  \/_/ \/_____/\/_/    \/_/\/_/\/___/  \/___/  \/___/
#
#
"""Top-level package for certifiable."""

from .__version__ import __author__, __email__, __keywords__, __short_description__, __version__
from .complex import certify_dict, certify_dict_schema, certify_email, certify_iterable_schema, \
    certify_list, certify_set, certify_tuple
from .core import certify_bool, certify_bytes, certify_date, certify_enum, certify_enum_value, \
    certify_int, certify_number, certify_object, certify_string, certify_text, certify_time, \
    certify_timestamp
from .errors import CertifierError, CertifierTypeError, CertifierValueError
from .operators import (
    ALL, AND, ANY, NAND, XOR, certify_all, certify_any, certify_none, certify_only_one,
)
from .utils import certify_required, disable, enable, enable_from_env, is_enabled, make_certifier

__all__ = [
    'certify_dict',
    'certify_dict_schema',
    'certify_iterable_schema',
    'certify_json',
    'certify_list',
    'certify_set',
    'certify_tuple',
    'certify_bool',
    'certify_bytes',
    'certify_date',
    'certify_enum',
    'certify_enum_value',
    'certify_int',
    'certify_number',
    'certify_object',
    'certify_text',
    'certify_string',
    'certify_timestamp',
    'certify_time',
    'CertifierError',
    'CertifierTypeError',
    'CertifierValueError',
    'AND',
    'ALL',
    'ANY',
    'NAND',
    'XOR',
    'certify_all',
    'certify_any',
    'certify_none',
    'certify_only_one',
    'make_certifier',
    'certify_required',
    'is_enabled',
    'enable',
    'disable',
    'enable_from_env',
]
