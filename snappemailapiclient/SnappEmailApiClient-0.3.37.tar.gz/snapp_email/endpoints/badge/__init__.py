from .BadgeBase_15Endpoint import BadgeBase_15Endpoint


class BadgeEndpoint:
    def __init__(self, api_client):
        self._api_client = api_client

    @property
    def BadgeBase_15(self):
        """
        :return: BadgeBase_15Endpoint
        """
        return BadgeBase_15Endpoint(self._api_client)
        