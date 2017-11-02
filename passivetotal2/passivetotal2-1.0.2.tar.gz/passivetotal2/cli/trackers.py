import json
from ..output import row_gen, output


def trackers(client, **kwargs):
    response = client.get_trackers(kwargs.get('query'), kwargs.get('type')).data
    rows = row_gen(response["results"], **kwargs)

    if kwargs.get('json'):
        return json.dumps(response, indent=4)
    return output(list(rows), **kwargs)
