from dnsimple import DNSimple

from .context import Context


context = Context()

api = DNSimple(
    username=context.dns['email'],
    password=context.dns['password']
)


def get(kind='A', name='', content='', *kwargs):
    recs = api.records(context.env['company.domain'])
    recs = [r['record'] for r in recs]
    if kind:
        recs = [r for r in recs if r['record_type'] == kind.upper()]
    if name:
        recs = [r for r in recs if r['name'].lower() == name.lower()]
    if content:
        recs = [r for r in recs if r['content'] == content]
    return recs


def add(kind='A', name='', content='', **kwargs):
    recs = get(kind, name, content, **kwargs)
    if recs:
        print('record exists, do not recreate')
        return False
    if not recs:
        print('record does not exist, creating')
        data = dict(
            record_type=kind.upper(),
            name=name,
            content=content
        )
        data.update(**kwargs)
        return api.add_record(context.env['company.domain'], data)


def delete(kind='A', name='', content='', **kwargs):
    recs = get(kind, name, content, **kwargs)
    for record_id in [rec['id'] for rec in recs]:
        api.delete_record(context.env['company.domain'], record_id)
    print('{} records deleted'.format(len(recs)))
