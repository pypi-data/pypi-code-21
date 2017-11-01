"""
hudai.resources.domain
"""
from ..helpers.resource import Resource


class DomainResource(Resource):
    def __init__(self, client):
        Resource.__init__(
            self, client, base_path='/companies/domains')
        self.resource_name = 'Domain'

    def list(self, company_id, page=None):
        query_params = self._set_limit_offset({'page': page})
        query_params['company_id'] = company_id

        return self.http_get('/', query_params=query_params)

    def create(self, company_id, hostname):
        return self.http_post('/', data={'hostname': hostname,'company_id': company_id})

    def fetch(self, entity_id):
        return self.http_get('/{id}',
                             params={'id': entity_id})

    def delete(self, entity_id):
        return self.http_delete('/{id}',
                                params={'id': entity_id})
