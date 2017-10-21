from .DocumentThumbnailInfo_13Endpoint import DocumentThumbnailInfo_13Endpoint
from .DocumentThumbnailPageInfo_13Endpoint import DocumentThumbnailPageInfo_13Endpoint
from .DocumentThumbnail_4Endpoint import DocumentThumbnail_4Endpoint
from .ThumbnailTextMapPage_19Endpoint import ThumbnailTextMapPage_19Endpoint


class DocumentThumbnailEndpoint:
    def __init__(self, api_client):
        self._api_client = api_client

    @property
    def DocumentThumbnailInfo_13(self):
        """
        :return: DocumentThumbnailInfo_13Endpoint
        """
        return DocumentThumbnailInfo_13Endpoint(self._api_client)
        
    @property
    def DocumentThumbnailPageInfo_13(self):
        """
        :return: DocumentThumbnailPageInfo_13Endpoint
        """
        return DocumentThumbnailPageInfo_13Endpoint(self._api_client)
        
    @property
    def DocumentThumbnail_4(self):
        """
        :return: DocumentThumbnail_4Endpoint
        """
        return DocumentThumbnail_4Endpoint(self._api_client)
        
    @property
    def ThumbnailTextMapPage_19(self):
        """
        :return: ThumbnailTextMapPage_19Endpoint
        """
        return ThumbnailTextMapPage_19Endpoint(self._api_client)
        