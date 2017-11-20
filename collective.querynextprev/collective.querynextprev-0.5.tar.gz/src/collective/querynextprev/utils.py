# -*- coding: utf-8 -*-
"""Utils."""
import collections


WINDOW_SIZE = 10


def expire_session_data(request):
    """Expire all querynextprev data in session."""
    for key in request.SESSION.keys():
        if key.startswith('querynextprev'):
            del request.SESSION[key]


def first_common_item(l1, l2):
    """Get first item in l2 that is also in l1."""
    for item in l2:
        if item in l1:
            return item

    return None


def get_next_items(l, index, include_index=False):
    """Get WINDOW_SIZE next items."""
    last_index = min(index + WINDOW_SIZE, len(l))
    if include_index:
        index -= 1

    return l[index+1:last_index+1]


def get_previous_items(l, index, include_index=False):
    """Get WINDOW_SIZE previous items."""
    first_index = max(index - 10, 0)
    if include_index:
        index += 1

    return l[first_index:index]


def convert_to_str(value):
    """Converts a value to str."""
    # pylint: disable=W0141
    if isinstance(value, str):
        return value
    if isinstance(value, unicode):
        return value.encode('utf8')
    elif isinstance(value, collections.Mapping):
        return dict(map(convert_to_str, value.iteritems()))
    elif isinstance(value, collections.Iterable):
        return type(value)(map(convert_to_str, value))
    else:
        return value


def clean_query(query):
    """ Remove from eeafacetednavigation query useless keys """
    return {k: v for k, v in query.items() if k not in ('facet.field', 'b_size', 'b_start')}
