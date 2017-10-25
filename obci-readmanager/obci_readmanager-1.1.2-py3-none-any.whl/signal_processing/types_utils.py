# -*- coding: utf-8 -*-
# Copyright (c) 2016-2018 Braintech Sp. z o.o. [Ltd.] <http://www.braintech.pl>
# All rights reserved.

"""Module defines single :method 'to_string' converting p_object to string."""


def to_string(p_object):
    """Convert p_object to string. Convert strings to strings, floats to string with accurate precision etc."""
    if isinstance(p_object, float):
        return repr(p_object)  # preserve precision
    else:
        return str(p_object)
