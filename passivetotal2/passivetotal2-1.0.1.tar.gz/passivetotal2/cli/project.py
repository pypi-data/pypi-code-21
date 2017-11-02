import re
import sys
import json
from ..output import row_gen, output


def find(client, guid=None, owner=None, creator=None,
         organization=None, visibility=None, featured=None,
         **kwargs):
    query = {
        k: v for k, v in {
            'project': guid,
            'owner': owner,
            'creator': creator,
            'organization': organization,
            'visibility': visibility,
            'featured': featured,
        }.items()
        if v is not None
    }
    res = client.get_project(**query)
    if res.status != 200:
        sys.exit('Status {!r}: {!r}'.format(res.status, res.text), file=sys.stderr)

    if kwargs.get('json'):
        return json.dumps(res.data, indent=4)

    strip = ['collaborators', 'subscribers', 'active', re.compile(r'^links.*')]
    strip.extend(list(query.keys()))

    if guid is not None:
        rows = row_gen(
            [res.data],
            headers=['guid', 'name', 'tags', 'description'],
            strip=strip,
            **kwargs
        )
    else:
        rows = row_gen(
            res.data['results'],
            headers=['guid', 'name', 'tags', 'description'],
            strip=strip,
            **kwargs
        )
    return output(list(rows), **kwargs)


def create(client, name=None, description=None,
           visibility='private', featured=False, tags=None,
           **kwargs):
    if tags:
        tags = tags.split(',')
    else:
        tags = []
    description = description or ''
    name = name or 'Unnamed Project (API)'
    res = client.create_project(
        name, visibility=visibility, description=description, featured=featured,
        tags=tags)
    if res.status != 200:
        sys.exit('Status {!r}: {!r}'.format(res.status, res.text), file=sys.stderr)
    if kwargs.get('json'):
        return json.dumps(res.data, indent=4)
    rows = row_gen(
        [res.data],
        headers=['guid', 'name', 'tags', 'description'],
        strip=['collaborators', 'subscribers', 'active',
               re.compile(r'^links.*')],
        **kwargs
    )
    return output(list(rows), **kwargs)


def update(client, guid=None, name=None, description=None,
           visibility=None, featured=None, tags=None,
           **kwargs):
    upd_kwargs = {}
    if name is not None:
        upd_kwargs['name'] = name
    if description is not None:
        upd_kwargs['description'] = description
    if visibility is not None:
        upd_kwargs['visibility'] = visibility
    if featured is not None:
        upd_kwargs['featured'] = featured
    if tags is not None:
        upd_kwargs['tags'] = tags.split(',')
    res = client.update_project(guid, **upd_kwargs)
    if res.status != 200:
        sys.exit('Status {!r}: {!r}'.format(res.status, res.text), file=sys.stderr)
    if kwargs.get('json'):
        return json.dumps(res.data, indent=4)
    rows = row_gen(
        [res.data],
        headers=['guid', 'name', 'tags', 'description'],
        strip=['collaborators', 'subscribers', 'active',
               re.compile(r'^links.*')],
        **kwargs
    )
    return output(list(rows), **kwargs)


def delete(client, guid=None, **kwargs):
    res = client.delete_project(guid)
    if res.status != 200:
        sys.exit('Status {!r}: {!r}'.format(res.status, res.text), file=sys.stderr)
    if kwargs.get('json'):
        return json.dumps(res.data, indent=4)
    rows = row_gen(
        [res.data],
        headers=['guid', 'name', 'tags', 'description'],
        strip=['collaborators', 'subscribers', 'active',
               re.compile(r'^links.*')],
        **kwargs
    )
    return output(list(rows), **kwargs)


def tag(client, **kwargs):
    if kwargs.get('action') == 'add':
        response = [client.add_project_tags(
            kwargs.get('query'), kwargs.get('tags')).data]
    elif kwargs.get('action') == 'set':
        response = [client.set_project_tags(
            kwargs.get('query'), kwargs.get('tags')).data]
    elif kwargs.get('action') == 'delete':
        response = [client.remove_project_tags(
            kwargs.get('query'), kwargs.get('tags')).data]
    rows = row_gen(response)
    if kwargs.get('json'):
        return json.dumps(response, indent=4)
    return output(list(rows), **kwargs)
