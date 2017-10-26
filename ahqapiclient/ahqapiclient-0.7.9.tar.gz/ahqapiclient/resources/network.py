from ahqapiclient.resources import Resource


class Network(Resource):

    def __init__(self, http_client):
        super(Network, self).__init__('/networks', http_client)

    def make_doc(self, name, ip, mask, color, tags):
        return {
            'name': name,
            'ip': ip,
            'mask': mask,
            'color': color,
            'tags': tags,
        }

    def create_network(self, name, ip, mask, color, tags=[]):
        return self.post(
            path=self.rurl(),
            data=self.make_doc(name, ip, mask, color, tags)
        )

    def get_network(self, _id):
        return self.get(path=self.rurl(_id))

    def update_network(self, _id, name, ip, mask, color, tags=[]):
        return self.put(
            path=self.rurl(_id),
            data=self.make_doc(name, ip, mask, color, tags)
        )

    def verification(self, _id, abuse_contact):
        return self.put(
            path=self.rurl('%s/verification' % _id),
            data={'abuse_contact': abuse_contact}
        )

    def delete_network(self, _id):
        return self.delete(path=self.rurl(_id))

    def get_networks(self, limit=10, offset=0, raw=False, query='',
                     sort='name:asc'):
        return self.get(
            path=self.rurl(),
            params={
                'limit': limit,
                'offset': offset,
                'query': query,
                'sort': sort
            },
            raw=raw,
        )

    def get_tags(self, limit=10, offset=0):
        return self.get(
            path=self.rurl('tags'),
            params={
                'limit': limit,
                'offset': offset
            },
        )

    def get_by_tag(self, limit=10, offset=0, tag='', raw=False):
        return self.get(
            path=self.rurl('tags/%s') % tag,
            params={
                'limit': limit,
                'offset': offset
            },
            raw=raw,
        )

    def total(self):
        total = self.get_networks(limit=0, raw=True)

        try:
            return total.headers['x-total']
        except KeyError:
            return None

    def total_by_tag(self, tag=''):
        total = self.get(
            path=self.rurl('tags/%s') % tag,
            params={
                'limit': 0,
                'offset': 0
            },
            raw=True
        )

        try:
            return total.headers['x-total']
        except:
            return None

    def get_asn_2_cidrs(self, asn='', raw=False):
        return self.get(
            path=self.rurl('asn2cidrs/%s') % asn,
            raw=raw,
        )

    def get_by_ip(self, ip=''):
        return self.get(
            path=self.rurl('ips/%s') % ip
        )
