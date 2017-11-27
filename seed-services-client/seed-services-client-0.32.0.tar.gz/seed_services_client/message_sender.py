from .seed_services import SeedServicesApiClient
from .utils import get_paginated_response


class MessageSenderApiClient(SeedServicesApiClient):
    """
    Client for Message Sender Service.

    :param str auth_token:
        An access token.

    :param str api_url:
        The full URL of the API.

    :param JSONServiceClient session:
        An instance of JSONServiceClient to use

    """

    def create_outbound(self, payload):
        return self.session.post('/outbound/', data=payload)

    def get_outbounds(self, params=None):
        return {"results": get_paginated_response(self.session, '/outbound/',
                params=params)}

    def create_inbound(self, payload):
        return self.session.post('/inbound/', data=payload)

    def get_inbounds(self, params=None):
        return {"results": get_paginated_response(self.session, '/inbound/',
                params=params)}

    def get_failed_tasks(self, params=None):
        return {"results": get_paginated_response(self.session,
                '/failed-tasks/', params=params)}

    def requeue_failed_tasks(self):
        return self.session.post('/failed-tasks/')
