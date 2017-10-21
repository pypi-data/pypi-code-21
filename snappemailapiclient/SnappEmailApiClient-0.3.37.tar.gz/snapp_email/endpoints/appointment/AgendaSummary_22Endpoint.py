"""
Auto generated code

"""

import json
from snapp_email.datacontract.classes import AgendaSummary_22
from snapp_email.datacontract.utils import export_dict, fill


class AgendaSummary_22Endpoint:
    def __init__(self, api_client):
        self.api_client = api_client
    
    def options(self, impersonate_user_id=None, accept_type=None):
        """
        Retrieve options available for resource 'AgendaSummary_22'.
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: AgendaSummary_22
        """
        url_parameters = {
        }
        endpoint_parameters = {
        }
        endpoint = 'appointment'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.agenda.summary-v5.18+json',
            'Accept': 'application/vnd.4thoffice.agenda.summary-v5.18+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('options', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(AgendaSummary_22, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def get(self, appointmentId, dateTimeStart, dateTimeEnd=None, impersonate_user_id=None, accept_type=None):
        """
        Retrieve agenda summary resource
        
        :param appointmentId: 
        :type appointmentId: 
        
        :param dateTimeStart: Start time of a certain time span
        :type dateTimeStart: DateTime
        
        :param dateTimeEnd: End time of a certain time span
        :type dateTimeEnd: DateTime
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: AgendaSummary_22
        """
        url_parameters = {
            'dateTimeStart': dateTimeStart,
            'dateTimeEnd': dateTimeEnd,
        }
        endpoint_parameters = {
            'appointmentId': appointmentId,
        }
        endpoint = 'appointment/{appointmentId}'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.agenda.summary-v5.18+json',
            'Accept': 'application/vnd.4thoffice.agenda.summary-v5.18+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('get', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(AgendaSummary_22, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
