from .DocumentPinnedToList_15Endpoint import DocumentPinnedToList_15Endpoint
from .DocumentShareList_14Endpoint import DocumentShareList_14Endpoint
from .Document_14Endpoint import Document_14Endpoint
from .Document_18Endpoint import Document_18Endpoint
from .File_14Endpoint import File_14Endpoint


class DocumentEndpoint:
    def __init__(self, api_client):
        self._api_client = api_client

    @property
    def DocumentPinnedToList_15(self):
        """
        :return: DocumentPinnedToList_15Endpoint
        """
        return DocumentPinnedToList_15Endpoint(self._api_client)
        
    @property
    def DocumentShareList_14(self):
        """
        :return: DocumentShareList_14Endpoint
        """
        return DocumentShareList_14Endpoint(self._api_client)
        
    @property
    def Document_14(self):
        """
        :return: Document_14Endpoint
        """
        return Document_14Endpoint(self._api_client)
        
    @property
    def Document_18(self):
        """
        :return: Document_18Endpoint
        """
        return Document_18Endpoint(self._api_client)
        
    @property
    def File_14(self):
        """
        :return: File_14Endpoint
        """
        return File_14Endpoint(self._api_client)
        