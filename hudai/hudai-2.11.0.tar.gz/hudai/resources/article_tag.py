"""
hudai.resources.article_tag
"""
from ..helpers.resource import Resource


class ArticleTagResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/articles/{article_id}/tags')
        self.resource_name = 'ArticleTag'

    def list(self, article_id, page=None):
        query_params = self._set_limit_offset({'page': page})

        return self.http_get('/', params={'article_id': article_id},
                                  query_params=query_params)

    def create(self, article_id, tag):
        return self.http_post('/', params={'article_id': article_id},
                                   data={'tag': tag})

    def fetch(self, article_id, tag):
        return self.http_get('/{tag}',
                             params={'article_id': article_id, 'tag': tag})

    def delete(self, article_id, tag):
        return self.http_delete('/{tag}',
                                params={'article_id': article_id, 'tag': tag})
