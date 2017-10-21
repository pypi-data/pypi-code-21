from .StreamAssistant_22Endpoint import StreamAssistant_22Endpoint
from .StreamBase_17Endpoint import StreamBase_17Endpoint
from .StreamBase_22Endpoint import StreamBase_22Endpoint
from .StreamCards_22Endpoint import StreamCards_22Endpoint
from .StreamChat_22Endpoint import StreamChat_22Endpoint
from .StreamGroup_17Endpoint import StreamGroup_17Endpoint
from .StreamGroup_22Endpoint import StreamGroup_22Endpoint
from .StreamName_22Endpoint import StreamName_22Endpoint
from .StreamUser_17Endpoint import StreamUser_17Endpoint
from .StreamUser_22Endpoint import StreamUser_22Endpoint
from .StreamVisibility_22Endpoint import StreamVisibility_22Endpoint


class StreamEndpoint:
    def __init__(self, api_client):
        self._api_client = api_client

    @property
    def StreamAssistant_22(self):
        """
        :return: StreamAssistant_22Endpoint
        """
        return StreamAssistant_22Endpoint(self._api_client)
        
    @property
    def StreamBase_17(self):
        """
        :return: StreamBase_17Endpoint
        """
        return StreamBase_17Endpoint(self._api_client)
        
    @property
    def StreamBase_22(self):
        """
        :return: StreamBase_22Endpoint
        """
        return StreamBase_22Endpoint(self._api_client)
        
    @property
    def StreamCards_22(self):
        """
        :return: StreamCards_22Endpoint
        """
        return StreamCards_22Endpoint(self._api_client)
        
    @property
    def StreamChat_22(self):
        """
        :return: StreamChat_22Endpoint
        """
        return StreamChat_22Endpoint(self._api_client)
        
    @property
    def StreamGroup_17(self):
        """
        :return: StreamGroup_17Endpoint
        """
        return StreamGroup_17Endpoint(self._api_client)
        
    @property
    def StreamGroup_22(self):
        """
        :return: StreamGroup_22Endpoint
        """
        return StreamGroup_22Endpoint(self._api_client)
        
    @property
    def StreamName_22(self):
        """
        :return: StreamName_22Endpoint
        """
        return StreamName_22Endpoint(self._api_client)
        
    @property
    def StreamUser_17(self):
        """
        :return: StreamUser_17Endpoint
        """
        return StreamUser_17Endpoint(self._api_client)
        
    @property
    def StreamUser_22(self):
        """
        :return: StreamUser_22Endpoint
        """
        return StreamUser_22Endpoint(self._api_client)
        
    @property
    def StreamVisibility_22(self):
        """
        :return: StreamVisibility_22Endpoint
        """
        return StreamVisibility_22Endpoint(self._api_client)
        