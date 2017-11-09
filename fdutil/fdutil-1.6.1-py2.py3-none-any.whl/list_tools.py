
__author__ = u'Oli Davis'
__copyright__ = u'Copyright (C) 2016 Oli Davis'


def filter_list(item_list,
                filters,
                exclude=False,
                case_sensitive=True):

    '''
    Filters provided list based on filters.
    NOTE: will always exclude any items that start with a '.'

    @param item_list:   List to be Filtered
    @param filters:     List of filter strings
                        i.e [u'.pyc'] will filter for any compiled python files
    @param exclude:     If true excludes items that match filters
                        If false excludes all items except those that match the filters
    @return: the filtered list
    '''

    # TODO: Expand to accept wildcards so that not excluding everything that starts with '.'

    remove_list = []

    if not case_sensitive:
        item_list = [item.lower() for item in item_list]
        filters = [filter.lower() for filter in filters]

    for item in item_list:
        if exclude:
            if any(word in item for word in filters) or item[0] == u'.':
                remove_list.append(item)

        else:
            if not any(word in item for word in filters) or item[0] == u'.':
                remove_list.append(item)

    for remove_item in remove_list:
        item_list.remove(remove_item)

    return item_list
