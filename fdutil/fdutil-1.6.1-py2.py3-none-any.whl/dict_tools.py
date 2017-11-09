
from collections import OrderedDict

__author__ = u'Oli Davis'
__copyright__ = u'Copyright (C) 2016 Oli Davis'


def filter_dict(src_dict,
                filters,
                exclude=False):

    """
    Filters provided dict based on filters.
    NOTE: will always exclude any items that start with a '.'

    :param src_dict:    Dict to be Filtered
    :param filters:     List of filter tuples.
                        Tuple format: (Search Key, Search Value, Condition)
                        First should not have a condition
                        i.e [("A", 123), ("A", 789, u'AND)]
    :param exclude:     If true excludes items that match filters
                        If false excludes all items except those that match the filters
    :return: the filtered dict
    """

    # Validate parameters
    assert (type(src_dict) is dict), u'src_dict is not a dictionary!'
    assert (type(filters) is list), u'filters is not a list!'

    # Validate filters
    #  1) Handle not getting any filters
    if len(filters) == 0:
        return src_dict.copy() if exclude else {}

    # 2) Check first filter (it's a special case as it does not require a condition)
    assert type(filters[0]) == tuple, u'First filter is not a tuple!'
    assert (len(filters[0]) == 2), u'First filter must have two parameters'

    # 3) Check remaining filters
    for fltr in filters[1:]:
        assert type(fltr) == tuple, u'Filter is not a tuple!'
        assert (len(fltr) >= 3), u'Filter ({f}) must have at least three parameters; ' \
                                 u'(Search Key, Search Value, Condition)'.format(f=fltr)

    # Make a copy of the dict for modifying
    temp_src_dict = src_dict.copy()
    filtered_dict = {}
    new_dict = {}

    # Function that checks a filter against the dict
    def check_filters():

        for k, v in temp_src_dict.iteritems():

            # We need to act based on the value type as dict can hold any type!
            if type(v) == dict:
                if ((fltr[0] in v) and (fltr[1] is None)) or \
                                ((v.get(fltr[0]) is not None) and (v.get(fltr[0]) == fltr[1])) \
                                and k not in filtered_dict:
                    filtered_dict[k] = v.copy()

            elif type(v) == list:
                # If the 'Search value' is set we must be looking for a dict sub item!
                if ((fltr[0] in v) and (fltr[1] is None)) and k not in filtered_dict:
                    filtered_dict[k] = v[:]

            elif type(v) in [str, unicode, int]:
                # If the 'Search value' is set we must be looking for a dict sub item!
                if ((fltr[0] == v) and (fltr[1] is None)) and k not in filtered_dict:
                    filtered_dict[k] = v

            else:
                raise TypeError(u'Unsupported value type ({t}'.format(t=type(v)))

    # Apply the filters
    for fltr in filters:

        try:
            filter_condition = fltr[2]

        except IndexError:
            filter_condition = None

        # Setup the working dicts for an AND
        if filter_condition == u'AND':
            temp_src_dict.clear()
            temp_src_dict = filtered_dict.copy()

        else:
            temp_src_dict.clear()
            temp_src_dict = src_dict.copy()

        # Reset the filtered dict for this run
        filtered_dict.clear()

        # Run the filter
        check_filters()

        # Update new_dict for condition
        if filter_condition == u'AND':
            new_dict.clear()
            new_dict = filtered_dict.copy()

        else:
            new_dict.update(filtered_dict)

    if exclude:
        # Save the keys to be excluded
        exclusion_keys = new_dict.keys()

        # Re-init new_dict from src_dict
        new_dict.clear()
        new_dict = src_dict.copy()

        # Remove the excluded keys
        for key in exclusion_keys:
            del new_dict[key]

    return new_dict


def sort_dict(src_dict,
              descending=False):

    """
    Sorts provided dict.

    :param src_dict:    Dict to be Filtered
    :param descending:   Boolean: defines whether dict is sorted ascending or descending.

    :return: the sorted dict
    """

    sorted_dict = OrderedDict()

    sorted_keys = sorted(src_dict, reverse=descending)

    for key in sorted_keys:
        sorted_dict[key] = src_dict[key]

    return sorted_dict
