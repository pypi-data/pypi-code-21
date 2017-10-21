from .ListOfClientEventLogsPage_15Endpoint import ListOfClientEventLogsPage_15Endpoint
from .ListOfClientEventLogs_15Endpoint import ListOfClientEventLogs_15Endpoint


class EventEndpoint:
    def __init__(self, api_client):
        self._api_client = api_client

    @property
    def ListOfClientEventLogsPage_15(self):
        """
        :return: ListOfClientEventLogsPage_15Endpoint
        """
        return ListOfClientEventLogsPage_15Endpoint(self._api_client)
        
    @property
    def ListOfClientEventLogs_15(self):
        """
        :return: ListOfClientEventLogs_15Endpoint
        """
        return ListOfClientEventLogs_15Endpoint(self._api_client)
        