import json
from ..output import row_gen, output


def _tag(client, **kwargs):
    if kwargs.get('action') == 'add':
        response = [client.add_tags(
            kwargs.get('query'), kwargs.get('tags')).data]
    elif kwargs.get('action') == 'set':
        response = [client.set_tags(
            kwargs.get('query'), kwargs.get('tags')).data]
    elif kwargs.get('action') == 'delete':
        response = [client.delete_tags(
            kwargs.get('query'), kwargs.get('tags')).data]
    elif kwargs.get('action') == 'get':
        response = [client.get_tags(
            kwargs.get('query')).data]
    elif kwargs.get('action') == 'search':
        response = client.search_tags(kwargs.get('tag')).data['results']
    return response


def actions(client, monitor=None, **kwargs):
    if kwargs.get('subcmd') == 'tag':
        response = _tag(client, **kwargs)
        rows = row_gen(response)

    if kwargs.get('subcmd') == 'monitor':
        response = [client.get_monitor(kwargs.get('domain')).data]
        rows = row_gen(response)

    if kwargs.get('subcmd') == 'classify':
        if kwargs.get('set') is not None:
            response = client.set_classification_bulk(
                kwargs.get('domains'),
                kwargs.get('set')
            ).data
        else:
            result = client.get_classification_bulk(
                kwargs.get('domains')
            ).data['results']
            response = [{'resolve': key,
                         'classification': result[key]['classification']}
                        for key in result]
        rows = row_gen(response)

    if kwargs.get('subcmd') == 'compromised':
        if kwargs.get('set') is not None:
            response = [client.set_compromised(
                kwargs.get('domain'),
                kwargs.get('set') == 'true'
            ).data]
        else:
            response = [client.get_compromised(
                kwargs.get('domain')
            ).data]
        rows = row_gen(response)

    if kwargs.get('subcmd') == 'dyndns':
        if kwargs.get('set') is not None:
            response = [client.set_dynamic_dns(
                kwargs.get('domain'),
                kwargs.get('set') == 'true'
            ).data]
        else:
            response = [client.get_dynamic_dns(
                kwargs.get('domain')
            ).data]
        rows = row_gen(response)

    if kwargs.get('subcmd') == 'sinkhole':
        if kwargs.get('set') is not None:
            response = [client.set_sinkhole(
                kwargs.get('IP'),
                kwargs.get('set') == 'true'
            ).data]
        else:
            response = [client.get_sinkhole(
                kwargs.get('IP')
            ).data]
        rows = row_gen(response)

    if kwargs.get('json'):
        return json.dumps(response, indent=4)
    return output(list(rows), **kwargs)
