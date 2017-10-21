from .GroupNotificationSettings_17Endpoint import GroupNotificationSettings_17Endpoint


class GroupNotificationEndpoint:
    def __init__(self, api_client):
        self._api_client = api_client

    @property
    def GroupNotificationSettings_17(self):
        """
        :return: GroupNotificationSettings_17Endpoint
        """
        return GroupNotificationSettings_17Endpoint(self._api_client)
        