"""
hudai.resources.company_key_term
"""
from ..helpers.resource import Resource


class CompanyEventResource(Resource):
    def __init__(self, client):
        Resource.__init__(
            self, client, base_path='/companies/{company_id}/events')
        self.resource_name = 'CompanyEvent'

    def list(self, company_id,
             starting_before=None,
             starting_after=None,
             ending_before=None,
             ending_after=None,
             occurring_at=None,
             title=None,
             event_type=None,
             page=None):
        query_params = self._set_limit_offset({
            'starting_before': starting_before,
            'starting_after': starting_after,
            'ending_before': ending_before,
            'ending_after': ending_after,
            'occurring_at': occurring_at,
            'title': title,
            'type': event_type,
            'page': page
        })

        return self.http_get('/',
                             params={'company_id': company_id},
                             query_params=query_params)

    def create(self, company_id,
               title=None,
               description=None,
               event_type=None,
               link_url=None,
               starts_at=None,
               ends_at=None):
        return self.http_post('/',
                              params={'company_id': company_id},
                              data={'title': title,
                                    'description': description,
                                    'type': event_type,
                                    'link_url': link_url,
                                    'starts_at': starts_at,
                                    'ends_at': ends_at})

    def fetch(self, company_id, entity_id):
        return self.http_get('/{id}',
                             params={'company_id': company_id, 'id': entity_id})

    def update(self, company_id, entity_id,
               title=None,
               description=None,
               event_type=None,
               link_url=None,
               starts_at=None,
               ends_at=None):
        return self.http_put('/{id}',
                             params={'company_id': company_id,
                                     'id': entity_id},
                             data={'title': title,
                                   'description': description,
                                   'type': event_type,
                                   'link_url': link_url,
                                   'starts_at': starts_at,
                                   'ends_at': ends_at})


    def delete(self, company_id, entity_id):
        return self.http_delete('/{id}',
                                params={'company_id': company_id, 'id': entity_id})
