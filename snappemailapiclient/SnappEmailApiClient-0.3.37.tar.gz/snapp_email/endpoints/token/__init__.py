from .AccessTokenInfoUser_13Endpoint import AccessTokenInfoUser_13Endpoint
from .AccessTokenInfo_13Endpoint import AccessTokenInfo_13Endpoint
from .AccessTokenInfo_17Endpoint import AccessTokenInfo_17Endpoint
from .AccessToken_14Endpoint import AccessToken_14Endpoint


class TokenEndpoint:
    def __init__(self, api_client):
        self._api_client = api_client

    @property
    def AccessTokenInfoUser_13(self):
        """
        :return: AccessTokenInfoUser_13Endpoint
        """
        return AccessTokenInfoUser_13Endpoint(self._api_client)
        
    @property
    def AccessTokenInfo_13(self):
        """
        :return: AccessTokenInfo_13Endpoint
        """
        return AccessTokenInfo_13Endpoint(self._api_client)
        
    @property
    def AccessTokenInfo_17(self):
        """
        :return: AccessTokenInfo_17Endpoint
        """
        return AccessTokenInfo_17Endpoint(self._api_client)
        
    @property
    def AccessToken_14(self):
        """
        :return: AccessToken_14Endpoint
        """
        return AccessToken_14Endpoint(self._api_client)
        