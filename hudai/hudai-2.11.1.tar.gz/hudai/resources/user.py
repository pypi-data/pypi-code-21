"""
hudai.resources.user
"""
from ..helpers.resource import Resource


class UserResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/users')
        self.resource_name = 'User'

    def list(self,
             email=None,
             digest_subscription_day=None,
             digest_subscription_hour=None,
             name=None,
             key_term=None,
             company_id=None,
             page=None):
        return self._list(
            email=email,
            digest_subscription_day=digest_subscription_day,
            digest_subscription_hour=digest_subscription_hour,
            name=name,
            key_term=key_term,
            company_id=company_id,
            page=page
        )

    def create(self, email=None, name=None, time_zone=None):
        return self._create(email=email, name=name, time_zone=time_zone)

    def fetch(self, entity_id):
        return self._fetch(entity_id)

    def me(self):
        return self.http_get('/me')

    def update(self, entity_id, email=None, name=None, time_zone=None):
        return self._update(entity_id,
                            email=email,
                            name=name,
                            time_zone=time_zone)

    def delete(self, entity_id):
        return self._delete(entity_id)
