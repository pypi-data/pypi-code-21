from .ListOfNotificationsPage_15Endpoint import ListOfNotificationsPage_15Endpoint
from .ListOfNotificationsPage_20Endpoint import ListOfNotificationsPage_20Endpoint
from .ListOfNotificationsPage_22Endpoint import ListOfNotificationsPage_22Endpoint
from .NotificationActionListUpdatedLast_18Endpoint import NotificationActionListUpdatedLast_18Endpoint
from .NotificationActionListUpdated_18Endpoint import NotificationActionListUpdated_18Endpoint
from .NotificationAssistantNudge_20Endpoint import NotificationAssistantNudge_20Endpoint
from .NotificationReminderListUpdated_22Endpoint import NotificationReminderListUpdated_22Endpoint


class NotificationEndpoint:
    def __init__(self, api_client):
        self._api_client = api_client

    @property
    def ListOfNotificationsPage_15(self):
        """
        :return: ListOfNotificationsPage_15Endpoint
        """
        return ListOfNotificationsPage_15Endpoint(self._api_client)
        
    @property
    def ListOfNotificationsPage_20(self):
        """
        :return: ListOfNotificationsPage_20Endpoint
        """
        return ListOfNotificationsPage_20Endpoint(self._api_client)
        
    @property
    def ListOfNotificationsPage_22(self):
        """
        :return: ListOfNotificationsPage_22Endpoint
        """
        return ListOfNotificationsPage_22Endpoint(self._api_client)
        
    @property
    def NotificationActionListUpdatedLast_18(self):
        """
        :return: NotificationActionListUpdatedLast_18Endpoint
        """
        return NotificationActionListUpdatedLast_18Endpoint(self._api_client)
        
    @property
    def NotificationActionListUpdated_18(self):
        """
        :return: NotificationActionListUpdated_18Endpoint
        """
        return NotificationActionListUpdated_18Endpoint(self._api_client)
        
    @property
    def NotificationAssistantNudge_20(self):
        """
        :return: NotificationAssistantNudge_20Endpoint
        """
        return NotificationAssistantNudge_20Endpoint(self._api_client)
        
    @property
    def NotificationReminderListUpdated_22(self):
        """
        :return: NotificationReminderListUpdated_22Endpoint
        """
        return NotificationReminderListUpdated_22Endpoint(self._api_client)
        