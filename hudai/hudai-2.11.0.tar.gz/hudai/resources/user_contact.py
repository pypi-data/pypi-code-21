"""
hudai.resources.user_contacts
"""
from ..helpers.resource import Resource


class UserContactResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/users/contacts')
        self.resource_name = 'UserContact'

    def list(self, user_id, company_id=None, page=None):
        return self._list(user_id=user_id, company_id=company_id, page=page)

    def create(self,
               user_id,
               company_id,
               name=None,
               email=None,
               phone_number=None):
        return self._create(
            user_id=user_id,
            company_id=company_id,
            name=name,
            email=email,
            phone_number=phone_number)

    def fetch(self, user_id, contact_id):
        return self.http_get('/{id}',
                             query_params={'user_id': user_id},
                             params={'id': contact_id})

    def update(self,
               user_id,
               contact_id,
               company_id=None,
               name=None,
               email=None,
               phone_number=None):
        return self.http_get('/{id}',
                             query_params={'user_id': user_id},
                             params={'id': contact_id},
                             body={
                                 'company_id': company_id,
                                 'name': name,
                                 'email': email,
                                 'phone_number': phone_number,
                             })

    def delete(self, user_id, contact_id):
        return self.http_delete('/{id}',
                                query_params={'user_id': user_id},
                                params={'id': contact_id})
