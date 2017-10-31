"""
hudai.resources.company_key_term
"""
from ..helpers.resource import Resource


class CompanyKeyTermResource(Resource):
    def __init__(self, client):
        Resource.__init__(
            self, client, base_path='/companies/{company_id}/key-terms')
        self.resource_name = 'CompanyKeyTerm'

    def list(self, company_id, page=None):
        query_params = self._set_limit_offset({'page': page})

        return self.http_get('/', params={'company_id': company_id},
                             query_params=query_params)

    def create(self, company_id, term):
        return self.http_post('/', params={'company_id': company_id},
                              data={'term': term})

    def fetch(self, company_id, term):
        return self.http_get('/{term}',
                             params={'company_id': company_id, 'term': term})

    def delete(self, company_id, term):
        return self.http_delete('/{term}',
                                params={'company_id': company_id, 'term': term})
