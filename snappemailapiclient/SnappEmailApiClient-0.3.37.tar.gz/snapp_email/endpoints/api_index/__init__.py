from .ApiIndex_1Endpoint import ApiIndex_1Endpoint
from .LocalizedResult_1Endpoint import LocalizedResult_1Endpoint
from .Result_1Endpoint import Result_1Endpoint


class ApiIndexEndpoint:
    def __init__(self, api_client):
        self._api_client = api_client

    @property
    def ApiIndex_1(self):
        """
        :return: ApiIndex_1Endpoint
        """
        return ApiIndex_1Endpoint(self._api_client)
        
    @property
    def LocalizedResult_1(self):
        """
        :return: LocalizedResult_1Endpoint
        """
        return LocalizedResult_1Endpoint(self._api_client)
        
    @property
    def Result_1(self):
        """
        :return: Result_1Endpoint
        """
        return Result_1Endpoint(self._api_client)
        