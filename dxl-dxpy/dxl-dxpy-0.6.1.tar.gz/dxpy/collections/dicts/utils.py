def filter_out_none_elements(dct):
    result = dict()
    for n in dct:
        if dct[n] is not None:
            result[n] = dct[n]
    return result


def combine_dicts(*dcts, ignore_none_elements=True):
    result = dict()
    for e in reversed(dcts):
        if ignore_none_elements:
            e = filter_out_none_elements(e)
        result.update(e)
    return result


def get_hierarchy_dict(dct, path):
    from dxpy.filesystem import Path
    if isinstance(path, str):
        path = Path(path)
    result = dct
    for k in path.rel_parts():
        result = result.get(k)
        if result is None:
            return dict()
    return result
