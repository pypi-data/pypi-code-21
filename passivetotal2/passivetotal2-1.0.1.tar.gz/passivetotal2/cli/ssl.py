import json
from ..output import row_gen, output


def ssl(client, query, history=False, keyword=False, field=None, **kwargs):
    if history:
        response = client.get_ssl_history(query.lower()).data
        rows = row_gen(response['results'])
    elif keyword:
        response = client.get_ssl_by_keyword(query).data
        rows = row_gen(response['results'])
    elif field:
        response = client.search_ssl(query, field).data
        rows = row_gen(response['results'])
    else:
        response = client.get_ssl(query.lower()).data
        rows = row_gen([response])
    if kwargs.get('json'):
        return json.dumps(response, indent=4)
    return output(list(rows), **kwargs)
