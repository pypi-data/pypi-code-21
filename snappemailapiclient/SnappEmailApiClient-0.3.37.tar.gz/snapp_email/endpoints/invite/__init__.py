from .Invite_20Endpoint import Invite_20Endpoint


class InviteEndpoint:
    def __init__(self, api_client):
        self._api_client = api_client

    @property
    def Invite_20(self):
        """
        :return: Invite_20Endpoint
        """
        return Invite_20Endpoint(self._api_client)
        