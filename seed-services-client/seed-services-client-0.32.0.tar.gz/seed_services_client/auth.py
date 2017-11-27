from demands import JSONServiceClient, HTTPServiceClient


class AuthApiClient(object):
    """
    Client for Auth Service.

    :param str email:

        An email address.

    :param str password:

        A password.

    :param str api_url:
        The full URL of the API.

    """

    def __init__(self, email, password, api_url, session=None,
                 session_http=None):
        if session is None:
            session = JSONServiceClient(url=api_url)
        # login
        data = {"email": email, "password": password}
        login = session.post('/user/tokens/', data=data)
        self.token = login["token"]
        headers = {'Authorization': 'Token %s' % self.token}
        session = JSONServiceClient(url=api_url, headers=headers)
        self.session = session
        if session_http is None:
            session_http = HTTPServiceClient(url=api_url, headers=headers)
        self.session_http = session_http

    def get_permissions(self):
        return self.session.get('/user/')

    def get_users(self):
        return self.session.get('/users/')

    def create_user(self, user):
        return self.session.post('/users/', data=user)

    def get_user(self, user):
        return self.session.get('/users/%s/' % user)

    def update_user(self, user_id, user):
        return self.session.put('/users/%s/' % user_id, data=user)

    def remove_user_from_team(self, user, team):
        # Returns a 204 with empty content so lets return True if it worked
        response = self.session_http.delete('/teams/%s/users/%s/' % (
                                            team, user,))
        if response.status_code == 204:
            return True
        else:
            return False

    def add_user_to_team(self, user, team):
        # Returns a 204 with empty content so lets return True if it worked
        response = self.session_http.put('/teams/%s/users/%s/' % (team, user,))
        if response.status_code == 204:
            return True
        else:
            return False

    def delete_user(self, user_id):
        # archives, soft delete
        response = self.session_http.delete('/users/%s/' % user_id)
        if response.status_code == 204:
            return True
        else:
            return False

    def get_teams(self):
        return self.session.get('/teams/')

    def create_team(self, org, team):
        return self.session.post('/organizations/%s/teams/' % org, data=team)

    def create_permission(self, team, permission):
        return self.session.post('/teams/%s/permissions/' % team,
                                 data=permission)
