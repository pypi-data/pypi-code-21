from .SignatureImage_20Endpoint import SignatureImage_20Endpoint


class SignatureImageEndpoint:
    def __init__(self, api_client):
        self._api_client = api_client

    @property
    def SignatureImage_20(self):
        """
        :return: SignatureImage_20Endpoint
        """
        return SignatureImage_20Endpoint(self._api_client)
        