from .ClientErrorLog_4Endpoint import ClientErrorLog_4Endpoint


class ErrorlogEndpoint:
    def __init__(self, api_client):
        self._api_client = api_client

    @property
    def ClientErrorLog_4(self):
        """
        :return: ClientErrorLog_4Endpoint
        """
        return ClientErrorLog_4Endpoint(self._api_client)
        