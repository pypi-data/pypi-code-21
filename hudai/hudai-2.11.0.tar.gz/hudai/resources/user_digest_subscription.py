"""
hudai.resources.user_digest_subscription
"""
from ..helpers.resource import Resource


class UserDigestSubscriptionResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/users/digest-subscriptions')
        self.resource_name = 'UserDigestSubscription'

    def list(self, user_id, day_of_week=None, iso_hour=None, page=None):
        query_params = self._set_limit_offset({
            'day_of_week': day_of_week,
            'iso_hour': iso_hour,
            'page': page,
            'user_id': user_id
        })

        return self.http_get('/', query_params=query_params)

    def create(self, user_id, day_of_week=None, iso_hour=None):
        return self.http_post('/',
                              data={'day_of_week': day_of_week,
                                    'iso_hour': iso_hour,
                                    'user_id': user_id})

    def fetch(self, user_id, digest_id):
        return self.http_get('/{id}',
                             query_params={'user_id': user_id},
                             params={'id': digest_id})

    def delete(self, user_id, digest_id):
        return self.http_delete('/{id}',
                                query_params={'user_id': user_id},
                                params={'id': digest_id})
