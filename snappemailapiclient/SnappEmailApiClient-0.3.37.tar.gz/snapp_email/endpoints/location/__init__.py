from .ListOfLocationsPage_19Endpoint import ListOfLocationsPage_19Endpoint


class LocationEndpoint:
    def __init__(self, api_client):
        self._api_client = api_client

    @property
    def ListOfLocationsPage_19(self):
        """
        :return: ListOfLocationsPage_19Endpoint
        """
        return ListOfLocationsPage_19Endpoint(self._api_client)
        