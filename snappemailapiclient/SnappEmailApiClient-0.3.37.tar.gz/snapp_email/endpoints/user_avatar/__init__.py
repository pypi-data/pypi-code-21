from .UserAvatar_17Endpoint import UserAvatar_17Endpoint


class UserAvatarEndpoint:
    def __init__(self, api_client):
        self._api_client = api_client

    @property
    def UserAvatar_17(self):
        """
        :return: UserAvatar_17Endpoint
        """
        return UserAvatar_17Endpoint(self._api_client)
        