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


def create(client, queries=None, project=None, type=None,
           tags=None, **kwargs):
    queries = _stdin_extend(queries)
    cwargs = {'project': project}
    if type:
        cwargs['artifact_type'] = type
    if tags:
        cwargs['tags'] = tags.split(',')
    res = client.create_artifacts(queries, **cwargs)
    if res.status != 200:
        sys.exit('Status {!r}: {!r}'.format(res.status, res.text))
    if kwargs.get('json'):
        return json.dumps(res.data, indent=4)
    rows = row_gen(res.data.values(),
                   headers=['project', 'guid', 'query', 'type', 'owner',
                            'creator'],
                   strip=[re.compile(r'^links.*'),
                          re.compile(r'^tag_meta.*'),
                          re.compile(r'^success.*')],
                   **kwargs)
    return output(list(rows), **kwargs)


def find(client, guid=None, project=None, owner=None,
         creator=None, organization=None, query=None,
         type=None, **kwargs):
    res = client.get_artifact(
        artifact=guid, creator=creator, organization=organization,
        owner=owner, project=project, query=query, artifact_type=type,
    )
    if res.status != 200:
        sys.exit('Status {!r}: {!r}'.format(res.status, res.text))
    if kwargs.get('json'):
        return json.dumps(res.data, indent=4)
    if guid:
        rows = row_gen([res.data],
                       headers=['project', 'guid', 'query', 'type', 'owner',
                                'creator'],
                       strip=[re.compile(r'^links.*'),
                              re.compile(r'^tag_meta.*'),
                              re.compile(r'^success.*')],
                       **kwargs)
    else:
        rows = row_gen(res.data['artifacts'],
                       headers=['project', 'guid', 'query', 'type', 'owner',
                                'creator'],
                       strip=[re.compile(r'^links.*'),
                              re.compile(r'^tag_meta.*'),
                              re.compile(r'^success.*')],
                       **kwargs)
    return output(list(rows), **kwargs)


def update(client, guids=None, monitor=None,
           disable_monitor=False, tags=None, **kwargs):
    if tags:
        tags = tags.split(',')
    guids = _stdin_extend(guids)
    res = client.update_artifacts(guids, monitor=monitor, tags=tags)
    if res.status != 200:
        sys.exit('Status {!r}: {!r}'.format(res.status, res.text))
    if kwargs.get('json'):
        return json.dumps(res.data, indent=4)
    rows = row_gen(res.data.values(),
                   headers=['project', 'guid', 'query', 'type', 'owner',
                            'creator'],
                   strip=[re.compile(r'^links.*'),
                          re.compile(r'^tag_meta.*'),
                          re.compile(r'^success.*')],
                   **kwargs)
    return output(list(rows), **kwargs)


def delete(client, guids=None, **kwargs):
    guids = _stdin_extend(guids)
    res = client.delete_artifacts(guids)
    if res.status != 200:
        sys.exit('Status {!r}: {!r}'.format(res.status, res.text))
    if kwargs.get('json'):
        return json.dumps(res.data, indent=4)
    rows = row_gen(res.data.values(),
                   headers=['project', 'guid', 'query', 'type', 'owner',
                            'creator'],
                   strip=[re.compile(r'^links.*'),
                          re.compile(r'^tag_meta.*'),
                          re.compile(r'^success.*')],
                   **kwargs)
    return output(list(rows), **kwargs)


def tag(client, **kwargs):
    if kwargs.get('action') == 'add':
        response = [client.add_artifact_tags(
            kwargs.get('query'), kwargs.get('tags')).data]
    elif kwargs.get('action') == 'set':
        response = [client.set_artifact_tags(
            kwargs.get('query'), kwargs.get('tags')).data]
    elif kwargs.get('action') == 'delete':
        response = [client.delete_artifact_tags(
            kwargs.get('query'), kwargs.get('tags')).data]
    elif kwargs.get('action') == 'get':
        response = [client.get_artifact_tags(
            kwargs.get('query')).data]
    rows = row_gen(response)
    if kwargs.get('json'):
        return json.dumps(response, indent=4)
    return output(list(rows), **kwargs)
