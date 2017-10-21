from .LogOnUserMobile_4Endpoint import LogOnUserMobile_4Endpoint
from .LogOnUser_14Endpoint import LogOnUser_14Endpoint


class UserSessionLogonEndpoint:
    def __init__(self, api_client):
        self._api_client = api_client

    @property
    def LogOnUserMobile_4(self):
        """
        :return: LogOnUserMobile_4Endpoint
        """
        return LogOnUserMobile_4Endpoint(self._api_client)
        
    @property
    def LogOnUser_14(self):
        """
        :return: LogOnUser_14Endpoint
        """
        return LogOnUser_14Endpoint(self._api_client)
        