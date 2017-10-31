"""
hudai.resources.article_key_term
"""
from ..helpers.resource import Resource


class ArticleKeyTermResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/articles/{article_id}/key-terms')
        self.resource_name = 'ArticleKeyTerm'

    def list(self, article_id, page=None):
        query_params = self._set_limit_offset({'page': page})

        return self.http_get('/', params={'article_id': article_id},
                                  query_params=query_params)

    def create(self, article_id, term):
        return self.http_post('/', params={'article_id': article_id},
                                   data={'term': term})

    def fetch(self, article_id, term):
        return self.http_get('/{term}',
                             params={'article_id': article_id, 'term': term})

    def delete(self, article_id, term):
        return self.http_delete('/{term}',
                                params={'article_id': article_id, 'term': term})
