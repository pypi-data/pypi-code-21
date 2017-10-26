import re
from ahqapiclient.resources import Resource


class InboundFilter(Resource):

    def __init__(self, http_client):
        super(InboundFilter, self).__init__('/inboundfilters', http_client)

    def make_doc(self, type, match_type, filter_value, action, type_attr=None,
                 action_attr=None):
        return {
            'type': type,
            'type_attr': type_attr,
            'match_type': match_type,
            'filter_value': filter_value,
            'action': action,
            'action_attr': action_attr,
        }

    def create_inbound_filter(self, type, match_type, filter_value, action,
                              type_attr=None, action_attr=None):
        return self.post(
            path=self.rurl(),
            data=self.make_doc(
                type, match_type, filter_value, action, type_attr,
                action_attr
            )
        )

    def get_inbound_filter(self, _id):
        return self.get(path=self.rurl(_id))

    def update_inbound_filter(self, _id, type, match_type, filter_value,
                              action, type_attr=None, action_attr=None):
        return self.put(
            path=self.rurl(_id),
            data=self.make_doc(
                type, match_type, filter_value, action, type_attr,
                action_attr
            )
        )

    def delete_inbound_filter(self, _id):
        return self.delete(path=self.rurl(_id))

    def get_inbound_filters(self, limit=10, offset=0, raw=False):
        return self.get(
            path=self.rurl(),
            params={
                'limit': limit,
                'offset': offset,
            },
            raw=raw,
        )

    def total(self):
        total = self.get_inbound_filters(limit=0, raw=True)

        try:
            return total.headers['x-total']
        except KeyError:
            return None

    def filter_rules(self):
        rules = []

        filters = self.get_inbound_filters(limit=self.total())

        for f in filters:
            action = f['action']
            action_value = None
            header_field = None
            regex = None
            _type = f['type']

            if action == 'forward':
                if f['action_attr']:
                    action_value = f['action_attr']
                else:
                    raise ValueError(
                        'Forward action missing the mail recipient.'
                    )

            if _type == 'header':
                if f['type_attr']:
                    header_field = f['type_attr']
                else:
                    raise ValueError('Header type is missing the header key.')

            if f['match_type'] == 'exact':
                regex = '^%s$' % re.escape(f['filter_value'])
            elif f['match_type'] == 'contains':
                regex = re.escape(f['filter_value'])
            elif f['match_type'] == 'regex':
                regex = f['filter_value']

            rules.append({
                'action': action,
                'action-value': action_value,
                'header-field': header_field,
                'regex': regex,
                'type': _type
            })

        return rules
