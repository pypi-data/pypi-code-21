from .Campaign_12Endpoint import Campaign_12Endpoint


class UserCampaignEndpoint:
    def __init__(self, api_client):
        self._api_client = api_client

    @property
    def Campaign_12(self):
        """
        :return: Campaign_12Endpoint
        """
        return Campaign_12Endpoint(self._api_client)
        