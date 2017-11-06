"""
hudai.resources.key_term
"""
from ..helpers.resource import Resource


class KeyTermResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/key-terms')
        self.resource_name = 'KeyTerm'

    def list(self, page=None):
        return self._list(page=page)

    def create(self, term=None):
        return self._create(term=term)

    def fetch(self, term):
        return self._fetch(term)

    def delete(self, term):
        return self._delete(term)
