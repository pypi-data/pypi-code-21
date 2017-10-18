"""
hudai.resources.article_id
"""
from ..helpers.resource import Resource


class CollateralResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/organizations/{organization_id}/collateral')
        self.resource_name = 'Collateral'

    def list(self, organization_id, page=None):
        query_params = self._set_limit_offset({'page': page})

        return self.http_get('/', params={'organization_id': organization_id},
                                  query_params=query_params)

    def metadata(self, organization_id):
        return self.http_get('/metadata',
                             params={'organization_id': organization_id})

    def create(self, organization_id,
               name=None,
               description=None,
               content_url=None,
               plaintext_url=None,
               filetype=None,
               size=None,
               data_science_metadata=None):
        return self.http_post('/', params={'organization_id': organization_id},
                              data={
                                  'name': name,
                                  'description': description,
                                  'content_url': content_url,
                                  'plaintext_url': plaintext_url,
                                  'filetype': filetype,
                                  'size': size,
                                  'data_science_metadata': data_science_metadata
                              })

    def fetch(self, organization_id, entity_id):
        return self.http_get('/{id}',
                             params={
                                 'organization_id': organization_id,
                                 'id': entity_id
                             })

    def update(self, organization_id, entity_id,
               name=None,
               description=None,
               content_url=None,
               plaintext_url=None,
               filetype=None,
               size=None,
               data_science_metadata=None):
        return self.http_patch('/{id}',
                               params={
                                   'organization_id': organization_id,
                                   'id': entity_id
                               },
                               data={
                                   'name': name,
                                   'description': description,
                                   'content_url': content_url,
                                   'plaintext_url': plaintext_url,
                                   'filetype': filetype,
                                   'size': size,
                                   'data_science_metadata': data_science_metadata
                               })

    def delete(self, organization_id, entity_id):
        return self.http_delete('/{id}',
                                params={
                                    'organization_id': organization_id,
                                    'id': entity_id
                                })
