"""
hudai.resources.user_key_term
"""
from ..helpers.resource import Resource


class UserKeyTermResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/users/key-terms')
        self.resource_name = 'UserKeyTerm'

    def list(self, user_id, page=None):
        query_params = self._set_limit_offset({'page': page})
        query_params['user_id'] = user_id

        return self.http_get('/', query_params=query_params)

    def create(self, user_id, term):
        return self.http_post('/', data={'term': term, 'user_id': user_id})

    def fetch(self, user_id, term):
        return self.http_get('/{term}',
                             query_params={'user_id': user_id},
                             params={'term': term})

    def delete(self, user_id, term):
        return self.http_delete('/{term}',
                                query_params={'user_id': user_id},
                                params={'term': term})
