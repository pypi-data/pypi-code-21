from .Menu_22Endpoint import Menu_22Endpoint


class NavigationEndpoint:
    def __init__(self, api_client):
        self._api_client = api_client

    @property
    def Menu_22(self):
        """
        :return: Menu_22Endpoint
        """
        return Menu_22Endpoint(self._api_client)
        