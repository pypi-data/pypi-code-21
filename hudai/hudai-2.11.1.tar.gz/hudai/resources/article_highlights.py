"""
hudai.resources.article_highlights
"""
from ..helpers.resource import Resource


class ArticleHighlightsResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/article-highlights')
        self.resource_name = 'ArticleHighlights'

    def list(self, article_id=None, link_hash=None, user_id=None):
        return self._list(article_id=article_id,
                          link_hash=link_hash,
                          user_id=user_id)

    def create(self, article_id=None, user_id=None, body=None):
        return self._create(article_id=article_id, user_id=user_id, body=body)

    def fetch(self, entity_id):
        return self._fetch(entity_id)

    def update(self, entity_id, body=None):
        return self._update(entity_id, body=body)

    def delete(self, entity_id):
        return self._delete(entity_id)
