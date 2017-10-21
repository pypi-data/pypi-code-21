from .GroupAvatar_17Endpoint import GroupAvatar_17Endpoint


class GroupAvatarEndpoint:
    def __init__(self, api_client):
        self._api_client = api_client

    @property
    def GroupAvatar_17(self):
        """
        :return: GroupAvatar_17Endpoint
        """
        return GroupAvatar_17Endpoint(self._api_client)
        