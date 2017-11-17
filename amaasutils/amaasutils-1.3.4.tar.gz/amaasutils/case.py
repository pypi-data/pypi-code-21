""" Helper functions for converting string cases """
from __future__ import absolute_import, division, print_function, unicode_literals

import re


def dict_camel_to_snake_case(camel_dict, convert_keys=True, convert_subkeys=False):
    """
    Recursively convert camelCased keys for a camelCased dict into snake_cased keys

    :param camel_dict: Dictionary to convert
    :param convert_keys: Whether the key should be converted
    :param convert_subkeys: Whether to also convert the subkeys, in case they are named properties of the dict
    :return:
    """

    converted = {}
    for key, value in camel_dict.items():
        if isinstance(value, dict):
            new_value = dict_camel_to_snake_case(value, convert_keys=convert_subkeys,
                                                 convert_subkeys=True)
        elif isinstance(value, list):
            new_value = []
            for subvalue in value:
                new_subvalue = dict_camel_to_snake_case(subvalue, convert_keys=convert_subkeys,
                                                        convert_subkeys=True) \
                    if isinstance(subvalue, dict) else subvalue
                new_value.append(new_subvalue)
        else:
            new_value = value
        new_key = to_snake_case(key) if convert_keys else key
        converted[new_key] = new_value
    return converted


def dict_snake_to_camel_case(snake_dict, convert_keys=True, convert_subkeys=False):
    """
    Recursively convert a snake_cased dict into a camelCased dict

    :param snake_dict: Dictionary to convert
    :param convert_keys: Whether the key should be converted
    :param convert_subkeys: Whether to also convert the subkeys, in case they are named properties of the dict
    :return:
    """

    converted = {}
    for key, value in snake_dict.items():
        if isinstance(value, dict):
            new_value = dict_snake_to_camel_case(value, convert_keys=convert_subkeys,
                                                 convert_subkeys=True)
        elif isinstance(value, list):
            new_value = []
            for subvalue in value:
                new_subvalue = dict_snake_to_camel_case(subvalue, convert_keys=convert_subkeys,
                                                        convert_subkeys=True) \
                    if isinstance(subvalue, dict) else subvalue
                new_value.append(new_subvalue)
        else:
            new_value = value
        new_key = to_camel_case(key) if convert_keys else key
        converted[new_key] = new_value
    return converted


def to_camel_case(snake_str):
    """
    Convert a snake_case string into a camelCase string
    """
    components = snake_str.split('_')
    return components[0] + "".join(x.title() for x in components[1:])


def to_snake_case(camel_str):
    """
    Convert a camelCase string into a snake_case string
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_str)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
