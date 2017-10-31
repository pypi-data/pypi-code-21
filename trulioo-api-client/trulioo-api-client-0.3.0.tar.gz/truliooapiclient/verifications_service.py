class VerificationsService:
    def __init__(self, client):
        self.client = client

    def GetTransactionRecordVerbose(self, id, headers=None, query_params=None, content_type="application/json"):
        """
        Fetch the results of a verification with the TransactionRecordId for the transaction this will include additional information if your account includes address cleansing and watchlist details.
        It is method for GET /verifications/v1/transactionrecord/{id}/verbose
        """
        uri = self.client.base_url + "/verifications/v1/transactionrecord/" + id + "/verbose"
        return self.client.get(uri, None, headers, query_params, content_type)

    def GetTransactionRecordWithAddress(self, id, headers=None, query_params=None, content_type="application/json"):
        """
        Fetch the results of a verification with the TransactionRecordId for the transaction this will include additional information if your account includes address cleansing.
        It is method for GET /verifications/v1/transactionrecord/{id}/withaddress
        """
        uri = self.client.base_url + "/verifications/v1/transactionrecord/" + id + "/withaddress"
        return self.client.get(uri, None, headers, query_params, content_type)

    def GetTransactionRecord(self, id, headers=None, query_params=None, content_type="application/json"):
        """
        This method is used to retrieve the request and results of a verification performed using the verify method. The response for this method includes the same information as verify method's response, along with data present in the input fields of the verify request.
        It is method for GET /verifications/v1/transactionrecord/{id}
        """
        uri = self.client.base_url + "/verifications/v1/transactionrecord/" + id
        return self.client.get(uri, None, headers, query_params, content_type)

    def Verify(self, data, headers=None, query_params=None, content_type="application/json"):
        """
        Calling this method will perform a verification. If your account includes address cleansing set the CleansedAddress flag to get additional address information in the result. You can query configuration to get what fields are available to you in each each country. It is also possible to get sample requests from the customer portal.
        It is method for POST /verifications/v1/verify
        """
        uri = self.client.base_url + "/verifications/v1/verify"
        return self.client.post(uri, data, headers, query_params, content_type)
