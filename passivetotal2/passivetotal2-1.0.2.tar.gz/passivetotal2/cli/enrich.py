import re
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


def enrich(client, query=None, malware=False, osint=False,
           subdomains=False, **kwargs):
    if malware:
        res = client.get_malware(query)
    elif osint:
        res = client.get_osint(query)
    elif subdomains:
        res = client.get_subdomains(query)
    else:
        res = client.get_enrichment(query)
    if res.status != 200:
        sys.exit('Status {!r}: {!r}'.format(res.status, res.text))

    if kwargs.get('json'):
        return json.dumps(res.data, indent=4)

    if malware:
        rows = row_gen(res.data['results'] or [],
                       headers=['sample', 'source', 'sourceUrl'],
                       **kwargs)
        print(json.dumps(res.data['results'], indent=4))
    elif osint:
        rows = row_gen(res.data['results'] or [],
                       headers=['source', 'sourceUrl', 'tags'],
                       strip=['derived', 'inReport'])
    elif subdomains:
        rows = row_gen(
            [
                {'subdomain': x + ('.' + query)*(not kwargs.get('short'))}
                for x in res.data['subdomains']
            ] or [], **kwargs
        )
    else:
        rows = row_gen([res.data], strip=[re.compile(r'^tag_meta.*')],
                       **kwargs)
    return output(list(rows), **kwargs)


def bulkenrich(client, queries=None, **kwargs):
    queries = _stdin_extend(queries)
    res = client.get_enrichment_bulk(queries)
    if res.status != 200:
        sys.exit('Status {!r}: {!r}'.format(res.status, res.text))

    if kwargs.get('json'):
        return json.dumps(res.data, indent=4)

    rows = row_gen(res.data['results'].values(),
                   strip=[re.compile(r'^tag_meta.*')],
                   **kwargs)
    return output(list(rows), **kwargs)
