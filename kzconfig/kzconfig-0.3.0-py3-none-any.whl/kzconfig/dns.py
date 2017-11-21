from dnsimple import DNSimple


class DNS:
    def __init__(self, context, domain='telephone.org'):
        self.context = context
        self.domain = domain
        creds = self.context.secrets['dns.dnsimple']

        self.api = DNSimple(
            username=creds['email'],
            password=creds['password']
        )

    def get(self, kind='A', name='', content='', **kwargs):
        recs = self.api.records(self.domain)
        recs = [r['record'] for r in recs]
        if kind:
            recs = [r for r in recs if r['record_type'] == kind.upper()]
        if name:
            recs = [r for r in recs if r['name'].lower() == name.lower()]
        if content:
            recs = [r for r in recs if r['content'] == content]
        return recs


    def add(self, kind='A', name='', content='', **kwargs):
        recs = self.get(kind, name, content, **kwargs)
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
            return self.api.add_record(self.domain, data)

    def delete(self, kind='A', name='', content='', **kwargs):
        recs = self.get(kind, name, content, **kwargs)
        for record_id in [rec['id'] for rec in recs]:
            self.api.delete_record(self.domain, record_id)
        print('{} records deleted'.format(len(recs)))
