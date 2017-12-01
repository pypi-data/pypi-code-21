#!/user/bin/env python3
# coding: utf-8


from copy import deepcopy


def recursive_sort(structure, key=None):
    if isinstance(structure, (list, tuple, set, frozenset)):
        return [recursive_sort(x, key) for x in sorted(structure, key=key)]
    elif isinstance(structure, dict):
        return {k: recursive_sort(v, key) for k, v in structure.items()}
    return deepcopy(structure)


