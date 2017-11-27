from __future__ import absolute_import, division, print_function
from .listalgo import move

# Tweak the tsort case to have callback to handle cycle case
# common usage would be to throw, or print that a cycle was broken


def depends_tsort(data, depends):
    '''
    data is list data to sort 
    depends is a dictionary {data item:[items to come after]}
    returns a list of items in data sort by depends requirements, 
        keeping order of orginal list otherwise
    '''
    ret = []
    visited = set([])
    org_data = set(data)

    for d in data:
        _visit(d, org_data, visited, ret, depends)
    return ret


def _visit(item, org_data, visited, sorted, depends):
    # if we have not visited this item yet
    if not item in visited:
        # Add item to know items we have visited
        visited.add(item)
        # go over dependant the we want before us
        for d in depends.get(item, []):
            # only add if this is in the orginal set of
            # data we are sorting
            if d in org_data:
                _visit(d, org_data, visited, sorted, depends)
        # add the item to sorted list
        sorted.append(item)
    else:
        if item not in sorted:
            print("cycle found with ", item, sorted)


def depends_back_sort(items, depends, copy=True):
    if copy:
        items = items[:]
    size = len(items)
    i = 0
    while i < size:
        org_indx = i
        idx = 0
        for d in depends.get(items[i], []):
            try:
                tmp = items.index(d)
            except ValueError:
                tmp = 0
            if tmp > idx:
                idx = tmp
        if org_indx < idx:
            move(items, org_indx, idx)
        else:
            i += 1

    return items


def depends_forward_sort(items, depends, copy=True):
    if copy:
        items = items[:]
    size = len(items)
    i = 0
    while i < size:
        org_indx = i
        idx = 0
        for d in depends.get(items[i], []):
            try:
                tmp = items.index(d)
            except ValueError:
                tmp = 0
            if tmp > org_indx:
                move(items, tmp, org_indx)
                org_indx += 1
        i += 1
    return items


def flatten_depends_map(depends):
    '''
        flattens a depends map only adds keys in map
        not all values the mapping
    '''
    return depends_forward_sort(list(depends.keys()), depends)
