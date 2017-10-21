"""
Auto generated code

"""

import json
from snapp_email.datacontract.classes import ReminderCalendar_20
from snapp_email.datacontract.utils import export_dict, fill


class ReminderCalendar_20Endpoint:
    def __init__(self, api_client):
        self.api_client = api_client
    
    def options(self, impersonate_user_id=None, accept_type=None):
        """
        Retrieve options available for resource 'ReminderCalendar_20'.
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: ReminderCalendar_20
        """
        url_parameters = {
        }
        endpoint_parameters = {
        }
        endpoint = 'reminder'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.reminder.calendar-v5.15+json',
            'Accept': 'application/vnd.4thoffice.reminder.calendar-v5.15+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('options', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(ReminderCalendar_20, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def get(self, reminderId, impersonate_user_id=None, accept_type=None):
        """
        Get reminder
        
        :param reminderId: 
        :type reminderId: 
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: ReminderCalendar_20
        """
        url_parameters = {
        }
        endpoint_parameters = {
            'reminderId': reminderId,
        }
        endpoint = 'reminder/{reminderId}'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.reminder.calendar-v5.15+json',
            'Accept': 'application/vnd.4thoffice.reminder.calendar-v5.15+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('get', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(ReminderCalendar_20, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def create(self, obj, impersonate_user_id=None, accept_type=None):
        """
        Create reminder
        
        :param obj: Object to be persisted
        :type obj: ReminderCalendar_20
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: ReminderCalendar_20
        """
        url_parameters = {
        }
        endpoint_parameters = {
        }
        endpoint = 'reminder'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.reminder.calendar-v5.15+json',
            'Accept': 'application/vnd.4thoffice.reminder.calendar-v5.15+json' if accept_type is None else accept_type,
        }
        data = export_dict(obj)
        response = self.api_client.api_call('post', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id, data=json.dumps(data))
        
        return fill(ReminderCalendar_20, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def delete(self, reminderId, impersonate_user_id=None, accept_type=None):
        """
        Delete reminder
        
        :param reminderId: 
        :type reminderId: 
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: True if object was deleted, otherwise an exception is raised
        :rtype: bool
        """
        url_parameters = {
        }
        endpoint_parameters = {
            'reminderId': reminderId,
        }
        endpoint = 'reminder/{reminderId}'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.reminder.calendar-v5.15+json',
            'Accept': 'application/vnd.4thoffice.reminder.calendar-v5.15+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('delete', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return True
