"""
hudai.resources.person_quote
"""
from ..helpers.resource import Resource


class PersonQuoteResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/people/{person_id}/quotes')
        self.resource_name = 'PersonQuote'

    def list(self, person_id, article_id=None, term=None, page=None):
        query_params = self._set_limit_offset({'page': page})
        query_params['article_id'] = article_id
        query_params['term'] = term

        return self.http_get('/', params={'person_id': person_id},
                             query_params=query_params)

    def create(self, person_id, article_id, term, text):
        return self.http_post('/', params={'person_id': person_id},
                              data={
                                  'article_id': article_id,
                                  'term': term,
                                  'text': text
                              })

    def fetch(self, person_id, quote_id):
        return self.http_get('/{id}',
                             params={'person_id': person_id, 'id': quote_id})

    def delete(self, person_id, quote_id):
        return self.http_delete('/{id}',
                                params={'person_id': person_id, 'id': quote_id})
