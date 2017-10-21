from .ReminderAppointment_20Endpoint import ReminderAppointment_20Endpoint
from .ReminderBase_20Endpoint import ReminderBase_20Endpoint
from .ReminderCalendar_20Endpoint import ReminderCalendar_20Endpoint
from .ReminderFollowup_20Endpoint import ReminderFollowup_20Endpoint
from .ReminderMention_20Endpoint import ReminderMention_20Endpoint
from .ReminderQuestion_20Endpoint import ReminderQuestion_20Endpoint
from .Reminder_20Endpoint import Reminder_20Endpoint
from .Reminder_21Endpoint import Reminder_21Endpoint
from .Reminder_22Endpoint import Reminder_22Endpoint


class ReminderEndpoint:
    def __init__(self, api_client):
        self._api_client = api_client

    @property
    def ReminderAppointment_20(self):
        """
        :return: ReminderAppointment_20Endpoint
        """
        return ReminderAppointment_20Endpoint(self._api_client)
        
    @property
    def ReminderBase_20(self):
        """
        :return: ReminderBase_20Endpoint
        """
        return ReminderBase_20Endpoint(self._api_client)
        
    @property
    def ReminderCalendar_20(self):
        """
        :return: ReminderCalendar_20Endpoint
        """
        return ReminderCalendar_20Endpoint(self._api_client)
        
    @property
    def ReminderFollowup_20(self):
        """
        :return: ReminderFollowup_20Endpoint
        """
        return ReminderFollowup_20Endpoint(self._api_client)
        
    @property
    def ReminderMention_20(self):
        """
        :return: ReminderMention_20Endpoint
        """
        return ReminderMention_20Endpoint(self._api_client)
        
    @property
    def ReminderQuestion_20(self):
        """
        :return: ReminderQuestion_20Endpoint
        """
        return ReminderQuestion_20Endpoint(self._api_client)
        
    @property
    def Reminder_20(self):
        """
        :return: Reminder_20Endpoint
        """
        return Reminder_20Endpoint(self._api_client)
        
    @property
    def Reminder_21(self):
        """
        :return: Reminder_21Endpoint
        """
        return Reminder_21Endpoint(self._api_client)
        
    @property
    def Reminder_22(self):
        """
        :return: Reminder_22Endpoint
        """
        return Reminder_22Endpoint(self._api_client)
        