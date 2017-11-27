from .seed_services import SeedServicesApiClient
from .utils import get_paginated_response


class StageBasedMessagingApiClient(SeedServicesApiClient):
    """
    Client for Stage Based Messaging Service.

    :param str auth_token:
        An access token.

    :param str api_url:
        The full URL of the API.

    :param JSONServiceClient session:
        An instance of JSONServiceClient to use

    :param HTTPServiceClient session_https:
        An instance of HTTPServiceClient to use

    """

    def get_schedules(self, params=None):
        return {"results": get_paginated_response(self.session, '/schedule/',
                params=params)}

    def get_schedule(self, schedule_id):
        return self.session.get('/schedule/%s/' % schedule_id)

    def get_messagesets(self, params=None):
        return {"results": get_paginated_response(self.session, '/messageset/',
                params=params)}

    def get_messageset(self, messageset_id):
        return self.session.get('/messageset/%s/' % messageset_id)

    def get_messageset_languages(self):
        return self.session.get('/messageset_languages/')

    def get_subscription(self, subscription):
        return self.session.get('/subscriptions/%s/' % subscription)

    def get_subscriptions(self, params=None):
        return {"results": get_paginated_response(self.session,
                '/subscriptions/', params=params)}

    def get_messages(self, params=None):
        return {"results": get_paginated_response(self.session, '/message/',
                params=params)}

    def get_message(self, message_id):
        return self.session.get('/message/%s/' % message_id)

    def delete_message(self, message_id):
        return self.session.delete('/message/%s/' % message_id)

    def update_message(self, message_id, data=None):
        return self.session.patch(
            '/message/{0}/'.format(message_id),
            data=data)

    def delete_binarycontent(self, binarycontent_id):
        return self.session.delete('/binarycontent/%s/' % binarycontent_id)

    def create_message(self, message):
        return self.session.post('/message/', data=message)

    def create_binarycontent(self, content):
        return self.session_http.post('/binarycontent/', files=content).json()

    def update_subscription(self, subscription, data=None):
        return self.session.patch('/subscriptions/%s/' % subscription,
                                  data=data)

    def create_subscription(self, subscription):
        return self.session.post('/subscriptions/', data=subscription)

    def get_failed_tasks(self, params=None):
        return {"results": get_paginated_response(self.session,
                '/failed-tasks/', params=params)}

    def requeue_failed_tasks(self):
        return self.session.post('/failed-tasks/')
