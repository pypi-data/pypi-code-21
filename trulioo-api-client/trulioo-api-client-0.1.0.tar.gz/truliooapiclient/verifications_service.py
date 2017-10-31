class VerificationsService:
    def __init__(self, client):
        self.client = client

    def Verify(self, data, headers=None, query_params=None, content_type="application/json"):
        """
        It is method for POST /verifications/v1/verify
        """
        uri = self.client.base_url + "/verifications/v1/verify"
        return self.client.post(uri, data, headers, query_params, content_type)
