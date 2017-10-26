'''
Code that manipulates the in-memory version of the Olympia
database, which is composed of boxes.
'''


# uniq a list, order preserving
# see: https://www.peterbe.com/plog/uniqifiers-benchmark


def uniq_f11(seq):
    return list(_uniq_f11(seq))


def _uniq_f11(seq):
    seen = set()
    for x in seq:
        if x in seen:
            continue
        seen.add(x)
        yield x


def box_append(data, box, subbox, value, dedup=False):
    '''
    append value to list data[box][subbox], doing what's needed to initialize things
    '''
    box = str(box)
    subbox = str(subbox)
    if not isinstance(value, list):
        value = [value]

    data[box] = data.get(box, {})

    l = data[box].get(subbox, [])
    [l.append(str(v)) for v in value]
    if dedup:
        l = uniq_f11(l)  # XXXv0 replace with if value not in l ...
    data[box][subbox] = l


def box_remove(data, box, subbox, value):
    '''
    remove value from list data[box][subbox]
    '''
    box = str(box)
    subbox = str(subbox)

    data[box] = data.get(box, {})

    l = data[box].get(subbox, [])
    try:
        l.remove(value)
        data[box][subbox] = l
    except ValueError:
        pass


def box_overwrite(data, box, subbox, value):
    '''
    overwrite list with a new one
    '''
    box = str(box)
    subbox = str(subbox)
    if not isinstance(value, list):
        value = [value]
    value = [str(v) for v in value]

    data[box] = data.get(box, {})

    data[box][subbox] = value


def subbox_append(data, box, subbox, key, value, dedup=False, prepend=False):
    '''
    append value to list data[box][subbox][key], doing what's needed to initialize things
    '''
    box = str(box)
    subbox = str(subbox)
    key = str(key)
    if not isinstance(value, list):
        value = [value]

    data[box] = data.get(box, {})
    data[box][subbox] = data[box].get(subbox, {})

    l = data[box][subbox].get(key, [])
    if prepend:
        rev = value
        rev.reverse()
        [l.insert(0, str(v)) for v in rev]
    else:
        [l.append(str(v)) for v in value]
    if dedup:
        l = uniq_f11(l)  # XXXv0 replace with if value not in l ...
    data[box][subbox][key] = l


def subbox_remove(data, box, subbox, key, value):
    '''
    remove value from list data[box][subbox][key]
    '''
    box = str(box)
    subbox = str(subbox)
    key = str(key)

    data[box] = data.get(box, {})
    data[box][subbox] = data[box].get(subbox, {})

    l = data[box][subbox].get(key, [])
    try:
        l.remove(value)
        data[box][subbox][key] = l
    except ValueError:
        pass


def subbox_overwrite(data, box, subbox, key, value):
    '''
    overwrite list with a new one
    '''
    box = str(box)
    subbox = str(subbox)
    key = str(key)

    if not isinstance(value, list):
        value = [value]
    value = [str(v) for v in value]

    data[box] = data.get(box, {})
    data[box][subbox] = data[box].get(subbox, {})

    data[box][subbox][key] = value


def box_sort(data, box, key):
    box = str(box)
    value = data.get(box, {}).get(key, [])
    if len(value) > 0:
        value = sorted([int(v) for v in value])
        value = [str(v) for v in value]
        data[box][key] = value


def subbox_sort(data, box, subbox, key):
    box = str(box)
    subbox = str(subbox)
    value = data.get(box, {}).get(subbox, {}).get(key, [])
    if len(value) > 0:
        value = sorted([int(v) for v in value])
        value = [str(v) for v in value]
        data[box][subbox][key] = value


def canonicalize(data):
    '''
    Do all the stuff needed to get data into a canonical form.
    '''

    for k, v in data.items():
        fl = v['firstline'][0]

        if fl.endswith(' loc region'):
            # in g2 it's only the main world/islands that are sorted, but we sort all
            hl = v.get('LI', {}).get('hl', [])
            if hl:
                v['LI']['hl'] = sorted(hl)

        if ' player ' in fl:
            subbox_sort(data, k, 'PL', 'kn')
            # subbox_sort(data, k, 'PL', 'un') -- C code does not sort unit list
            box_sort(data, k, 'an')
            box_sort(data, k, 'ad')
            box_sort(data, k, 'ah')
            # XXXv0 special sort of PL am

        if ' char ' in fl:
            # in g2, wandering npcs have their guys first il, all else sorted; we sort all
            if 'il' in v:
                il = inventory_to_dict(v['il'])
                v['il'] = dict_to_inventory(il)
            box_sort(data, k, 'an')
            box_sort(data, k, 'ad')
            box_sort(data, k, 'ah')


def inventory_to_dict(il):
    il_copy = il.copy()
    ret = {}
    while len(il_copy) > 0:
        k = il_copy.pop(0)
        ret[k] = il_copy.pop(0)
    return ret


def dict_to_inventory(d):
    ret = []
    keys = sorted([int(k) for k in d])
    for k in keys:
        k = str(k)
        if int(d[k]) > 0:
            ret.extend([k, d[k]])
    return ret


class Box:
    '''
    This is intended to eventually wrap all box manipulation
    '''
    def __init__(self):
        self._name = None
        self._inventory = {}

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def inventory(self):
        return self._inventory

    @inventory.setter
    def inventory(self, value):
        self._inventory = value
