from .AsyncJobStatus_22Endpoint import AsyncJobStatus_22Endpoint


class JobEndpoint:
    def __init__(self, api_client):
        self._api_client = api_client

    @property
    def AsyncJobStatus_22(self):
        """
        :return: AsyncJobStatus_22Endpoint
        """
        return AsyncJobStatus_22Endpoint(self._api_client)
        