from __future__ import absolute_import, division, print_function


def move(lst, idx, new_idx):
    obj = lst.pop(idx)
    lst.insert(new_idx, obj)
