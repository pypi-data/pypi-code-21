"""
Api description
"""

from messente.verigator import routes, client, controllers


class Api(object):
    """Main class for verigator api,
    contains references to other controllers

    Attributes:
        services (controllers.Services): controller for service resource

        users (controllers.Users): controller for user resource

        auth (controllers.Auth): controller for auth resource

    """

    def __init__(self, username, password, endpoint=routes.URL):
        """
        Initialize Verigator api

        Args:
            username (str): api username. Can be obtained from dashboard

            password (str): api password. Can be obtained from dashboard

            endpoint (str): api endpoint. Can be obtained from dashboard
        """
        rest_client = client.RestClient(endpoint, username, password)
        self.users = controllers.Users(rest_client)
        self.services = controllers.Services(rest_client)
        self.auth = controllers.Auth(rest_client)
