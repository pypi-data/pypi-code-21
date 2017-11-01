"""
hudai.resources.company
"""
from ..helpers.resource import Resource


class CompanyResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/companies')
        self.resource_name = 'Company'

    def list(self, name=None, ticker=None, key_term=None, page=None):
        return self._list(name=name,
                          key_term=key_term,
                          ticker=ticker,
                          page=page)

    def create(self, name=None, ticker=None):
        return self._create(name=name, ticker=ticker)

    def fetch(self, entity_id):
        return self._fetch(entity_id)

    def update(self, entity_id, name=None, ticker=None):
        return self._update(entity_id, name=name, ticker=ticker)

    def delete(self, entity_id):
        return self._delete(entity_id)

    def domains(self, entity_id):
        return self.http_get('/{id}/domains',
                             params={'id': entity_id})

    def key_terms(self, entity_id):
        return self.http_get('/{id}/key-terms',
                             params={'id': entity_id})
