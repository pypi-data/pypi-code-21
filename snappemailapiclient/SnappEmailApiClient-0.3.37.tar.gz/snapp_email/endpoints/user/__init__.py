from .User_14Endpoint import User_14Endpoint


class UserEndpoint:
    def __init__(self, api_client):
        self._api_client = api_client

    @property
    def User_14(self):
        """
        :return: User_14Endpoint
        """
        return User_14Endpoint(self._api_client)
        