from .Drive_14Endpoint import Drive_14Endpoint


class DriveEndpoint:
    def __init__(self, api_client):
        self._api_client = api_client

    @property
    def Drive_14(self):
        """
        :return: Drive_14Endpoint
        """
        return Drive_14Endpoint(self._api_client)
        