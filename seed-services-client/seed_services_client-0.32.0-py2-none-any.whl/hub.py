from demands import JSONServiceClient
from .utils import get_paginated_response


class HubApiClient(object):
    """
    Client for Hub Service (registration and changes).

    :param str auth_token:

        An access token.

    :param str api_url:
        The full URL of the API.

    """

    def __init__(self, auth_token, api_url, session=None):
        headers = {'Authorization': 'Token ' + auth_token}
        if session is None:
            session = JSONServiceClient(url=api_url,
                                        headers=headers)
        self.session = session

    def get_registrations(self, params=None):
        """
        Filter params can include
        'stage', 'mother_id', 'validated', 'source', 'created_before'
        'created_after' """
        return {"results": get_paginated_response(self.session,
                '/registrations/', params=params)}

    def get_registration(self, registration):
        return self.session.get('/registrations/%s/' % registration)

    def create_registration(self, registration):
        return self.session.post('/registration/', data=registration)

    def update_registration(self, registration, data=None):
        return self.session.patch('/registration/%s/' % registration,
                                  data=data)

    def get_changes(self, params=None):
        """
        Filter params can include
        'action', 'mother_id', 'validated', 'source', 'created_before'
        'created_after' """
        return {"results": get_paginated_response(self.session, '/changes/',
                params=params)}

    def get_change(self, change):
        return self.session.get('/changes/%s/' % change)

    def create_change(self, change):
        return self.session.post('/change/', data=change)

    def trigger_report_generation(self, params=None):
        """
        Calls the Hub endpoint for generating reports """
        return self.session.post('/reports/', data=params)

    def create_optout_admin(self, optout):
        """
        Calls the hub endpoint for a optout from admin apps"""
        return self.session.post('/optout_admin/', data=optout)

    def create_change_admin(self, change):
        """
        Calls the hub endpoint for a change from admin apps"""
        return self.session.post('/change_admin/', data=change)

    def get_report_tasks(self, params=None):
        return {"results": get_paginated_response(self.session,
                '/reporttasks/', params=params)}
