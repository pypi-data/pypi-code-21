from dnsimple import DNSimple

from .context import context

api = DNSimple(
    username=context.dns['email'],
    password=context.dns['password']
)


def add(kind='A', name='', content='', **kwargs):
    data = dict(
        record_type=kind.upper(),
        name=name,
        content=content
    )
    data.update(**kwargs)
    api.add_record(context.env['company.domain'], data)
