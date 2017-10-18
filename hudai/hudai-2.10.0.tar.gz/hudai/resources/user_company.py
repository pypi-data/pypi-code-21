"""
hudai.resources.user_company
"""
from ..helpers.resource import Resource


class UserCompanyResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/users/companies')
        self.resource_name = 'UserCompany'

    def list(self, user_id, page=None):
        query_params = self._set_limit_offset({'page': page})
        query_params['user_id'] = user_id

        return self.http_get('/', query_params=query_params)

    def create(self, user_id, company_id):
        return self.http_post('/', data={'company_id': company_id, 'user_id': user_id})

    def fetch(self, user_id, company_id):
        return self.http_get('/{company_id}',
                             query_params={'user_id': user_id},
                             params={'company_id': company_id})

    def delete(self, user_id, company_id):
        return self.http_delete('/{company_id}',
                                query_params={'user_id': user_id},
                                params={'company_id': company_id})
