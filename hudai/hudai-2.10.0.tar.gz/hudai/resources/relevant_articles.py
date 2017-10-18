"""
hudai.resources.relevant_articles
"""
from ..helpers.resource import Resource


class RelevantArticlesResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/articles/relevant')
        self.resource_name = 'RelevantArticles'

    def list(self,
             user_id=None,
             article_id=None,
             published_before=None,
             published_after=None,
             scored_above=None,
             scored_below=None,
             scored_before=None,
             scored_after=None,
             page=None):
        return self._list(
            user_id=user_id,
            article_id=article_id,
            published_before=published_before,
            published_after=published_after,
            scored_above=scored_above,
            scored_below=scored_below,
            scored_before=scored_before,
            scored_after=scored_after,
            page=page
        )

    def create(self,
               user_id=None,
               article_id=None,
               score=None,
               scored_at=None,
               article_published_at=None):
        return self._create(
            user_id=user_id,
            article_id=article_id,
            score=score,
            scored_at=scored_at,
            article_published_at=article_published_at
        )

    def fetch(self, entity_id):
        return self._fetch(entity_id)

    def delete(self, entity_id):
        return self._delete(entity_id)
