"""
hudai.resources.person_key_term
"""
from ..helpers.resource import Resource


class PersonKeyTermResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/people/{person_id}/key-terms')
        self.resource_name = 'PersonKeyTerm'

    def list(self, person_id, page=None):
        query_params = self._set_limit_offset({'page': page})

        return self.http_get('/', params={'person_id': person_id},
                                  query_params=query_params)

    def create(self, person_id, term):
        return self.http_post('/', params={'person_id': person_id},
                                   data={'term': term})

    def fetch(self, person_id, term):
        return self.http_get('/{term}',
                             params={'person_id': person_id, 'term': term})

    def delete(self, person_id, term):
        return self.http_delete('/{term}',
                                params={'person_id': person_id, 'term': term})
