import csv
from tabulate import tabulate
import collections
import re
import datetime

IP = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')

def get_dt_object(x):
    try:
        return datetime.datetime.strptime(x, '%Y-%m-%d')
    except:
        try:
            return datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')
        except:
            return datetime.datetime.min


def _expand_ip_zeros(ip):
    if not IP.match(ip):
        return ip
    ip_split = ip.split('.')
    return '.'.join(['{:>03}'.format(b) for b in ip_split])


MODIFIERS = {
    'lastSeen': get_dt_object,
    'firstSeen': get_dt_object,
    'resolve': _expand_ip_zeros,
}


def _flatten(d, parent_key='', sep='.'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(_flatten(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            items.append((new_key, ';'.join(v)))
        else:
            items.append((new_key, v))
    return dict(items)


def _dict2row(d, headers=None, strip=None, **kwargs):
    d = _flatten(d)
    headers = headers or []
    strip = strip or []
    keys = headers + sorted(set(d.keys()) - set(headers + strip))
    # Optional user filter
    keys = kwargs['include'] or keys
    for s in strip:
        # string remove
        if s in keys:
            keys.remove(s)
        # regex
        if hasattr(s, 'match'):
            for k in list(keys):
                if s.match(k):
                    keys.remove(k)
    return keys, [_truncate(d, key) for key in keys]


def _truncate(d, key):
    val = d.get(key, '')
    if isinstance(val, str) and len(val) > 40:
        return val[:37] + '...'
    return val


def sort(rows, sort_columns=None, **kwargs):
    def index(li, q):
        return li.index(q) if q in li else None
    def build_function(*args):
        return lambda x: tuple([i[1](x[i[0]]) for i in args if i[0] is not None])

    sort_key = build_function(
        *[
            (index(rows[0], i), MODIFIERS.get(i, lambda x: x))
            for i in sort_columns
        ]
    )
    return [rows[0]] + sorted(rows[1:], key=sort_key)


def output(rows, delim=None, write_csv=None, sort_columns=None, rotate=False,
           **kwargs):
    from io import StringIO
    data = StringIO()
    if not rows:
        return
    rows = sort(list(rows), sort_columns=sort_columns.split(','), **kwargs)
    if kwargs['no_headers']:
        rows = rows[1:]
        fmt = 'plain'
    else:
        fmt = 'default'
    if delim:
        writer = csv.writer(data, delimiter=delim)
        writer.writerows(rows)
        return data.getvalue()
    if write_csv:
        writer = csv.writer(data, delimiter=',')
        writer.writerows(rows)
        return data.getvalue()
    else:
        if rotate:
            return tabulate(list(zip(*rows)), tablefmt=fmt)
        else:
            return tabulate(rows, headers='firstrow', tablefmt=fmt)



def row_gen(results, headers=None, strip=None, include=None, exclude=None,
            no_headers=False, order=None, **kwargs):
    strip = (strip or []) + (exclude or [])
    if order:
        headers = order
    if results:
        passed = False
        for result in results:
            keys, row = _dict2row(result, headers=headers, strip=strip,
                                  include=include, **kwargs)
            if not passed:
                yield keys
                passed = True
            yield row
