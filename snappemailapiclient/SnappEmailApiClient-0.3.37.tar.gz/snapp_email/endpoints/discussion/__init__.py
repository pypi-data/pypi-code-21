from .DiscussionCardCombined_20Endpoint import DiscussionCardCombined_20Endpoint
from .DiscussionCardCombined_22Endpoint import DiscussionCardCombined_22Endpoint
from .DiscussionCardTrash_22Endpoint import DiscussionCardTrash_22Endpoint
from .DiscussionCard_20Endpoint import DiscussionCard_20Endpoint
from .DiscussionCard_22Endpoint import DiscussionCard_22Endpoint


class DiscussionEndpoint:
    def __init__(self, api_client):
        self._api_client = api_client

    @property
    def DiscussionCardCombined_20(self):
        """
        :return: DiscussionCardCombined_20Endpoint
        """
        return DiscussionCardCombined_20Endpoint(self._api_client)
        
    @property
    def DiscussionCardCombined_22(self):
        """
        :return: DiscussionCardCombined_22Endpoint
        """
        return DiscussionCardCombined_22Endpoint(self._api_client)
        
    @property
    def DiscussionCardTrash_22(self):
        """
        :return: DiscussionCardTrash_22Endpoint
        """
        return DiscussionCardTrash_22Endpoint(self._api_client)
        
    @property
    def DiscussionCard_20(self):
        """
        :return: DiscussionCard_20Endpoint
        """
        return DiscussionCard_20Endpoint(self._api_client)
        
    @property
    def DiscussionCard_22(self):
        """
        :return: DiscussionCard_22Endpoint
        """
        return DiscussionCard_22Endpoint(self._api_client)
        