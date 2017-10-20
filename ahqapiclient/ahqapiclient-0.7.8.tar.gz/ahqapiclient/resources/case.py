from ahqapiclient.resources import Resource


class Case(Resource):

    def __init__(self, http_client):
        super(Case, self).__init__('/cases', http_client)

    def get_case(self, _id):
        return self.get(path=self.rurl(_id))

    def get_cases(self, limit=10, offset=0, query='',
                  sort='date:desc', raw=False):
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

    def get_transitions(self, case_id):
        return self.get(
            path=self.rurl('%s/transitions' % case_id),
            params={
            }
        )

    def trigger_transition(self, case_id, trans_id, params={}):
        return self.post(
            path=self.rurl('%s/transitions' % case_id),
            data={
                'id': trans_id,
                'params': params
            }
        )
