from .BatchRequest_22Endpoint import BatchRequest_22Endpoint


class BatchEndpoint:
    def __init__(self, api_client):
        self._api_client = api_client

    @property
    def BatchRequest_22(self):
        """
        :return: BatchRequest_22Endpoint
        """
        return BatchRequest_22Endpoint(self._api_client)
        