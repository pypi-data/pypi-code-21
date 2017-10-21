from .BoardBase_15Endpoint import BoardBase_15Endpoint
from .BoardBase_22Endpoint import BoardBase_22Endpoint
from .BoardGroup_22Endpoint import BoardGroup_22Endpoint
from .BoardName_22Endpoint import BoardName_22Endpoint
from .BoardPersonal_15Endpoint import BoardPersonal_15Endpoint
from .BoardPersonal_20Endpoint import BoardPersonal_20Endpoint
from .BoardPersonal_21Endpoint import BoardPersonal_21Endpoint
from .BoardPersonal_22Endpoint import BoardPersonal_22Endpoint
from .ListOfBoardsPage_15Endpoint import ListOfBoardsPage_15Endpoint
from .ListOfBoardsPage_20Endpoint import ListOfBoardsPage_20Endpoint
from .ListOfBoardsPage_21Endpoint import ListOfBoardsPage_21Endpoint
from .ListOfBoardsPage_22Endpoint import ListOfBoardsPage_22Endpoint
from .ListOfBoards_15Endpoint import ListOfBoards_15Endpoint


class BoardEndpoint:
    def __init__(self, api_client):
        self._api_client = api_client

    @property
    def BoardBase_15(self):
        """
        :return: BoardBase_15Endpoint
        """
        return BoardBase_15Endpoint(self._api_client)
        
    @property
    def BoardBase_22(self):
        """
        :return: BoardBase_22Endpoint
        """
        return BoardBase_22Endpoint(self._api_client)
        
    @property
    def BoardGroup_22(self):
        """
        :return: BoardGroup_22Endpoint
        """
        return BoardGroup_22Endpoint(self._api_client)
        
    @property
    def BoardName_22(self):
        """
        :return: BoardName_22Endpoint
        """
        return BoardName_22Endpoint(self._api_client)
        
    @property
    def BoardPersonal_15(self):
        """
        :return: BoardPersonal_15Endpoint
        """
        return BoardPersonal_15Endpoint(self._api_client)
        
    @property
    def BoardPersonal_20(self):
        """
        :return: BoardPersonal_20Endpoint
        """
        return BoardPersonal_20Endpoint(self._api_client)
        
    @property
    def BoardPersonal_21(self):
        """
        :return: BoardPersonal_21Endpoint
        """
        return BoardPersonal_21Endpoint(self._api_client)
        
    @property
    def BoardPersonal_22(self):
        """
        :return: BoardPersonal_22Endpoint
        """
        return BoardPersonal_22Endpoint(self._api_client)
        
    @property
    def ListOfBoardsPage_15(self):
        """
        :return: ListOfBoardsPage_15Endpoint
        """
        return ListOfBoardsPage_15Endpoint(self._api_client)
        
    @property
    def ListOfBoardsPage_20(self):
        """
        :return: ListOfBoardsPage_20Endpoint
        """
        return ListOfBoardsPage_20Endpoint(self._api_client)
        
    @property
    def ListOfBoardsPage_21(self):
        """
        :return: ListOfBoardsPage_21Endpoint
        """
        return ListOfBoardsPage_21Endpoint(self._api_client)
        
    @property
    def ListOfBoardsPage_22(self):
        """
        :return: ListOfBoardsPage_22Endpoint
        """
        return ListOfBoardsPage_22Endpoint(self._api_client)
        
    @property
    def ListOfBoards_15(self):
        """
        :return: ListOfBoards_15Endpoint
        """
        return ListOfBoards_15Endpoint(self._api_client)
        