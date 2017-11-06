"""
hudai.resources.company_key_term
"""
from ..helpers.resource import Resource


class CompanyEventResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/companies/events')
        self.resource_name = 'CompanyEvent'

    def list(self,
             company_id=None,
             starting_before=None,
             starting_after=None,
             ending_before=None,
             ending_after=None,
             occurring_at=None,
             title=None,
             event_type=None,
             page=None):
        query_params = self._set_limit_offset({
            'company_id': company_id,
            'starting_before': starting_before,
            'starting_after': starting_after,
            'ending_before': ending_before,
            'ending_after': ending_after,
            'occurring_at': occurring_at,
            'title': title,
            'type': event_type,
            'page': page
        })

        return self.http_get('/', query_params=query_params)

    def create(self,
               company_id=None,
               title=None,
               description=None,
               event_type=None,
               link_url=None,
               starts_at=None,
               ends_at=None):
        return self.http_post('/',
                              data={'company_id': company_id,
                                    'title': title,
                                    'description': description,
                                    'type': event_type,
                                    'link_url': link_url,
                                    'starts_at': starts_at,
                                    'ends_at': ends_at})

    def fetch(self, entity_id):
        return self.http_get('/{id}', params={'id': entity_id})

    def update(self, entity_id,
               company_id=None,
               title=None,
               description=None,
               event_type=None,
               link_url=None,
               starts_at=None,
               ends_at=None):
        return self.http_put('/{id}',
                             params={'id': entity_id},
                             data={'company_id': company_id,
                                   'title': title,
                                   'description': description,
                                   'type': event_type,
                                   'link_url': link_url,
                                   'starts_at': starts_at,
                                   'ends_at': ends_at})


    def delete(self, entity_id):
        return self.http_delete('/{id}', params={'id': entity_id})
