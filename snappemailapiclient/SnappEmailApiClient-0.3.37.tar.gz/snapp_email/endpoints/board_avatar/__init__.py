from .BoardAvatar_22Endpoint import BoardAvatar_22Endpoint


class BoardAvatarEndpoint:
    def __init__(self, api_client):
        self._api_client = api_client

    @property
    def BoardAvatar_22(self):
        """
        :return: BoardAvatar_22Endpoint
        """
        return BoardAvatar_22Endpoint(self._api_client)
        