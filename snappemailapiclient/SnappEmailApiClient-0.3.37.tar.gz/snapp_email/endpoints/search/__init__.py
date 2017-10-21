from .SearchGroup_18Endpoint import SearchGroup_18Endpoint
from .SearchResultsGroupedPage_18Endpoint import SearchResultsGroupedPage_18Endpoint
from .SearchResults_20Endpoint import SearchResults_20Endpoint
from .SearchResults_22Endpoint import SearchResults_22Endpoint


class SearchEndpoint:
    def __init__(self, api_client):
        self._api_client = api_client

    @property
    def SearchGroup_18(self):
        """
        :return: SearchGroup_18Endpoint
        """
        return SearchGroup_18Endpoint(self._api_client)
        
    @property
    def SearchResultsGroupedPage_18(self):
        """
        :return: SearchResultsGroupedPage_18Endpoint
        """
        return SearchResultsGroupedPage_18Endpoint(self._api_client)
        
    @property
    def SearchResults_20(self):
        """
        :return: SearchResults_20Endpoint
        """
        return SearchResults_20Endpoint(self._api_client)
        
    @property
    def SearchResults_22(self):
        """
        :return: SearchResults_22Endpoint
        """
        return SearchResults_22Endpoint(self._api_client)
        