import json
import sys
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


def dns(client, queries=None, unique=False, keyword=False, **kwargs):
    headers = ['value', 'resolve', 'resolveType', 'recordType',
               'firstSeen', 'lastSeen', 'source']
    strip = ['collected', 'recordHash']

    queries = _stdin_extend(queries)

    results = None
    for query in queries:
        if unique:
            res = client.get_dns_unique(query)
        elif keyword:
            res = client.get_dns_keyword(query)
        else:
            res = client.get_dns_passive(query)
        if res.status != 200:
            sys.exit(
                'Status {!r}: {!r}'.format(res.status, res.text)
            )
        if results:
            if results.data['queryType'] != res.data['queryType']:
                sys.exit(
                    'unable to mix query types in bulk query'
                    # not strictly true, we could mix them
                )
            results.data['firstSeen'] = 'First Seen unavailable in bulk query'
            results.data['lastSeen'] = 'Last Seen unavailable in bulk query'
            results.data['totalRecords'] += res.data['totalRecords']
            results.data['queryValue'] += ';'+res.data['queryValue']
            results.data['results'].extend(res.data['results'])
        else:
            results = res

    if kwargs.get('json'):
        return json.dumps(results.data, indent=4)
    if unique:
        headers = ['resolve', 'count']
        frequency = [
            {'resolve': i[0], 'count': i[1]}
            for i in results.data['frequency']
        ]
        rows = row_gen(frequency,
                       headers=headers,
                       **kwargs)
    elif keyword:
        rows = row_gen(results.data['results'],
                       headers=['focusPoint', 'matchType'],
                       strip=strip,
                       **kwargs)
    else:
        rows = row_gen(results.data['results'], headers=headers, strip=strip,
                       **kwargs)
    return output(list(rows), **kwargs)
