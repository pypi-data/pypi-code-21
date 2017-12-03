# -*- coding: utf8 -*-


def flatten(nested_iterable):
    return [item for sublist in nested_iterable for item in sublist]
