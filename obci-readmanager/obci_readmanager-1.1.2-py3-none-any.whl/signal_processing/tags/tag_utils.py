# -*- coding: utf-8 -*-
# Copyright (c) 2016-2018 Braintech Sp. z o.o. [Ltd.] <http://www.braintech.pl>
# All rights reserved.

"""Module providing methods for packing and unpakig tags from dictionary: 'unpack_tag_from_dict', 'pack_tag_to_dict'."""


def unpack_tag_from_dict(p_dict):
    """
    For given dictionary describing tag in strings, return dictionary where numeric values are numbers, not strings.

    The method is fired by file tags reader, while parsing xml tags file.
    """
    start_timestamp = float(p_dict['position'])
    l_tag_dict = {
        'start_timestamp': start_timestamp,
        'end_timestamp': start_timestamp + float(p_dict['length']),
        'name': p_dict['name']
    }
    ch_str = p_dict['channelNumber']
    try:
        ch = float(ch_str)
        if ch == -1.0:
            ch_str = ''
    except ValueError:
        pass

    l_tag_dict['channels'] = ch_str
    l_tag_desc = {}
    for i_key, i_value in p_dict.items():
        if i_key not in ['position', 'length', 'name', 'channelNumber']:
            # TODO - use tag definition in case i_value is not a string
            # but some more complex structure
            l_tag_desc[i_key] = i_value
    l_tag_dict['desc'] = l_tag_desc
    return l_tag_dict


def pack_tag_to_dict(p_start_timestamp, p_end_timestamp,
                     p_tag_name, p_tag_desc={}, p_tag_channels=""):
    """
    For given tag parameters return a dictionary representing tag with those parameters.

    Parameters:
    - p_start_timestamp - float
    - p_end_timestamp - float
    - p_tag_name - string
    - p_tag_desc - dictionary
    - p_tag_channels - string like "0 6 7" - numbers of channels
    """
    l_tag_dict = {
        'start_timestamp': p_start_timestamp,
        'end_timestamp': p_end_timestamp,
        'name': p_tag_name,
        'channels': p_tag_channels,
        'desc': p_tag_desc
    }
    return l_tag_dict
