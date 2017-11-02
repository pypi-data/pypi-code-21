import json
from ..output import row_gen, output


def host(client, query, direction=None, trackers=False,
         start=None, end=None, **kwargs):
    if direction:
        response = client.get_host_attributes_pairs(
            query, direction, start, end).data
    elif trackers:
        response = client.get_host_attributes_trackers(query, start, end).data
    else:
        response = client.get_host_attributes(query, start, end).data

    if kwargs.get('json'):
        return json.dumps(response, indent=4)

    rows = row_gen(response['results'], **kwargs)
    return output(list(rows), **kwargs)
