from .ListOfLanguagesPage_14Endpoint import ListOfLanguagesPage_14Endpoint
from .ListOfRegionsPage_14Endpoint import ListOfRegionsPage_14Endpoint
from .ListOfTimeZonesPage_14Endpoint import ListOfTimeZonesPage_14Endpoint


class LocalizationEndpoint:
    def __init__(self, api_client):
        self._api_client = api_client

    @property
    def ListOfLanguagesPage_14(self):
        """
        :return: ListOfLanguagesPage_14Endpoint
        """
        return ListOfLanguagesPage_14Endpoint(self._api_client)
        
    @property
    def ListOfRegionsPage_14(self):
        """
        :return: ListOfRegionsPage_14Endpoint
        """
        return ListOfRegionsPage_14Endpoint(self._api_client)
        
    @property
    def ListOfTimeZonesPage_14(self):
        """
        :return: ListOfTimeZonesPage_14Endpoint
        """
        return ListOfTimeZonesPage_14Endpoint(self._api_client)
        