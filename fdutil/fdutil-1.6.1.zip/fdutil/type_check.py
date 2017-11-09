# encoding: utf-8

from collections import OrderedDict


def is_dictionary(item):
    return isinstance(item, dict) or isinstance(item, OrderedDict)


def is_list(item):
    return isinstance(item, list)


def is_list_or_dictionary(item):
    return is_list(item) or is_dictionary(item)


def is_list_of_lists(item):
    return bool(item) and all([is_list(element) for element in item])


def is_list_of_dictionaries(item):
    return bool(item) and all([is_dictionary(element) for element in item])
