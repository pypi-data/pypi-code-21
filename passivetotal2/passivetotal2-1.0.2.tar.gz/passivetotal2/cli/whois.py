import sys
import json
from ..output import row_gen, output


def _stdin_extend(items):
    _items = []
    for item in items:
        if item == '-':
            stdin = [x.strip() for x in sys.stdin.readlines() if x.strip()]
            _items.extend(stdin)
        else:
            _items.append(item)
    return _items


def whois(client, queries=None, field=None, keyword=False, **kwargs):
    queries = _stdin_extend(queries)

    results = None
    for query in queries:
        if keyword:
            res = client.get_whois_keyword(query)
        elif field:
            res = client.get_whois_search(query, field)
        else:
            res = client.get_whois(query)
        if res.status != 200:
            sys.exit('Status {!r}: {!r}'.format(res.status, res.text))
        if results:
            results.data['results'].extend(res.data['results'])
        else:
            results = res

    if kwargs.get('json'):
        return json.dumps(res.data, indent=4)

    if keyword:
        rows = row_gen(res.data['results'],
                       headers=['focusPoint', 'matchType'],
                       **kwargs)
    elif field:
        rows = row_gen(res.data['results'], **kwargs)
    else:
        rows = row_gen([res.data], **kwargs)

    return output(list(rows), **kwargs)
