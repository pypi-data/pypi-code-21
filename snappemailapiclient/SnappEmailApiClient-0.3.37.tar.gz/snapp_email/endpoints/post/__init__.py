from .AssistantInsight_22Endpoint import AssistantInsight_22Endpoint
from .Invoice_22Endpoint import Invoice_22Endpoint
from .ListOfPostUnreadPage_22Endpoint import ListOfPostUnreadPage_22Endpoint
from .ListOfPostUnread_22Endpoint import ListOfPostUnread_22Endpoint
from .ListOfPostsPage_22Endpoint import ListOfPostsPage_22Endpoint
from .PostActionList_22Endpoint import PostActionList_22Endpoint
from .PostAssistant_22Endpoint import PostAssistant_22Endpoint
from .PostBoardLink_22Endpoint import PostBoardLink_22Endpoint
from .PostBody_22Endpoint import PostBody_22Endpoint
from .PostFlagManagedByAssistant_20Endpoint import PostFlagManagedByAssistant_20Endpoint
from .PostPinnedToList_20Endpoint import PostPinnedToList_20Endpoint
from .PostPinnedToList_21Endpoint import PostPinnedToList_21Endpoint
from .PostPinnedToList_22Endpoint import PostPinnedToList_22Endpoint
from .PostPreview_20Endpoint import PostPreview_20Endpoint
from .PostUnread_22Endpoint import PostUnread_22Endpoint
from .Post_18Endpoint import Post_18Endpoint
from .Post_20Endpoint import Post_20Endpoint
from .Post_22Endpoint import Post_22Endpoint


class PostEndpoint:
    def __init__(self, api_client):
        self._api_client = api_client

    @property
    def AssistantInsight_22(self):
        """
        :return: AssistantInsight_22Endpoint
        """
        return AssistantInsight_22Endpoint(self._api_client)
        
    @property
    def Invoice_22(self):
        """
        :return: Invoice_22Endpoint
        """
        return Invoice_22Endpoint(self._api_client)
        
    @property
    def ListOfPostUnreadPage_22(self):
        """
        :return: ListOfPostUnreadPage_22Endpoint
        """
        return ListOfPostUnreadPage_22Endpoint(self._api_client)
        
    @property
    def ListOfPostUnread_22(self):
        """
        :return: ListOfPostUnread_22Endpoint
        """
        return ListOfPostUnread_22Endpoint(self._api_client)
        
    @property
    def ListOfPostsPage_22(self):
        """
        :return: ListOfPostsPage_22Endpoint
        """
        return ListOfPostsPage_22Endpoint(self._api_client)
        
    @property
    def PostActionList_22(self):
        """
        :return: PostActionList_22Endpoint
        """
        return PostActionList_22Endpoint(self._api_client)
        
    @property
    def PostAssistant_22(self):
        """
        :return: PostAssistant_22Endpoint
        """
        return PostAssistant_22Endpoint(self._api_client)
        
    @property
    def PostBoardLink_22(self):
        """
        :return: PostBoardLink_22Endpoint
        """
        return PostBoardLink_22Endpoint(self._api_client)
        
    @property
    def PostBody_22(self):
        """
        :return: PostBody_22Endpoint
        """
        return PostBody_22Endpoint(self._api_client)
        
    @property
    def PostFlagManagedByAssistant_20(self):
        """
        :return: PostFlagManagedByAssistant_20Endpoint
        """
        return PostFlagManagedByAssistant_20Endpoint(self._api_client)
        
    @property
    def PostPinnedToList_20(self):
        """
        :return: PostPinnedToList_20Endpoint
        """
        return PostPinnedToList_20Endpoint(self._api_client)
        
    @property
    def PostPinnedToList_21(self):
        """
        :return: PostPinnedToList_21Endpoint
        """
        return PostPinnedToList_21Endpoint(self._api_client)
        
    @property
    def PostPinnedToList_22(self):
        """
        :return: PostPinnedToList_22Endpoint
        """
        return PostPinnedToList_22Endpoint(self._api_client)
        
    @property
    def PostPreview_20(self):
        """
        :return: PostPreview_20Endpoint
        """
        return PostPreview_20Endpoint(self._api_client)
        
    @property
    def PostUnread_22(self):
        """
        :return: PostUnread_22Endpoint
        """
        return PostUnread_22Endpoint(self._api_client)
        
    @property
    def Post_18(self):
        """
        :return: Post_18Endpoint
        """
        return Post_18Endpoint(self._api_client)
        
    @property
    def Post_20(self):
        """
        :return: Post_20Endpoint
        """
        return Post_20Endpoint(self._api_client)
        
    @property
    def Post_22(self):
        """
        :return: Post_22Endpoint
        """
        return Post_22Endpoint(self._api_client)
        