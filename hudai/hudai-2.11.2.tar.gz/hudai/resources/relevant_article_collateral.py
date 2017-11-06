"""
hudai.resources.article_id
"""
from ..helpers.resource import Resource


class RelevantArticleCollateralResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/articles/relevant/{relevant_article_id}/collateral')
        self.resource_name = 'RelevantArticleCollateral'

    def list(self, relevant_article_id, collateral_id=None, page=None):
        query_params = self._set_limit_offset({
            'collateral_id': collateral_id,
            'page': page
        })

        return self.http_get('/', params={'relevant_article_id': relevant_article_id},
                                  query_params=query_params)

    def create(self, relevant_article_id, collateral_id):
        return self.http_post('/', params={'relevant_article_id': relevant_article_id},
                                   data={ 'collateral_id': collateral_id })

    def fetch(self, relevant_article_id, collateral_id):
        return self.http_get('/{id}',
                             params={
                                 'relevant_article_id': relevant_article_id,
                                 'id': collateral_id
                             })

    def delete(self, relevant_article_id, collateral_id):
        return self.http_delete('/{id}',
                                params={
                                    'relevant_article_id': relevant_article_id,
                                    'id': collateral_id
                                })
