"""
Auto generated code

"""

import json
from snapp_email.datacontract.classes import ListOfNotificationsPage_22
from snapp_email.datacontract.utils import export_dict, fill


class ListOfNotificationsPage_22Endpoint:
    def __init__(self, api_client):
        self.api_client = api_client
    
    def options(self, impersonate_user_id=None, accept_type=None):
        """
        Retrieve options available for resource 'ListOfNotificationsPage_22'.
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: ListOfNotificationsPage_22
        """
        url_parameters = {
        }
        endpoint_parameters = {
        }
        endpoint = 'notification'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.notification.list.page-v5.18+json',
            'Accept': 'application/vnd.4thoffice.notification.list.page-v5.18+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('options', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(ListOfNotificationsPage_22, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def get(self, size, offset, sinceId=None, notificationType=None, sortDirection=None, longPolling=None, returnFullResource=None, skipOlderThan=None, htmlFormat=None, impersonate_user_id=None, accept_type=None):
        """
        Get notification list.
        
        :param size: Specify size of requested page.
        :type size: Int32
        
        :param offset: Specify offset of requested page.
        :type offset: Int32
        
        :param sinceId: Specify since id. That is an id of a resource from which incremental list load should take place.
        :type sinceId: String
        
        :param notificationType: Filter by type of notification.
            Available values:
            - PostCreated
            - PostUnread
            - CardCreated
            - CardUpdated
            - CardPinnedToListUpdated
            - BoardCreated
            - BoardUpdated
            - BoardDeleted
            - ReminderCreated
            - ReminderUpdated
            - ReminderDeleted
        :type notificationType: String
        
        :param sortDirection: Specify sort direction.
        :type sortDirection: String
        
        :param longPolling: Perform long polling while reading the resource.
        :type longPolling: Boolean
        
        :param returnFullResource: Boolean flag indicating whether fully loaded resources should get returned.
        :type returnFullResource: Boolean
        
        :param skipOlderThan: Filter by resource created criterion. String presentation of date that complies with ISO 8601 format.
        :type skipOlderThan: DateTime
        
        :param htmlFormat: Mime format for html body of post resource.
            Available values:
            - text/html-stripped
            - text/html-stripped.mobile
        :type htmlFormat: String
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: ListOfNotificationsPage_22
        """
        url_parameters = {
            'sinceId': sinceId,
            'notificationType': notificationType,
            'sortDirection': sortDirection,
            'longPolling': longPolling,
            'returnFullResource': returnFullResource,
            'skipOlderThan': skipOlderThan,
            'htmlFormat': htmlFormat,
            'size': size,
            'offset': offset,
        }
        endpoint_parameters = {
        }
        endpoint = 'notification'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.notification.list.page-v5.18+json',
            'Accept': 'application/vnd.4thoffice.notification.list.page-v5.18+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('get', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(ListOfNotificationsPage_22, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def get_2(self, size, offset, sinceId=None, skipNotificationType=None, sortDirection=None, returnFullResource=None, skipOlderThan=None, htmlFormat=None, impersonate_user_id=None, accept_type=None):
        """
        Get notification list.
        
        :param size: Specify size of requested page.
        :type size: Int32
        
        :param offset: Specify offset of requested page.
        :type offset: Int32
        
        :param sinceId: Specify since id. That is an id of a resource from which incremental list load should take place.
        :type sinceId: String
        
        :param skipNotificationType: Skip filter by type of notification.
            Available values:
            - PostCreated
            - PostUnread
            - CardCreated
            - CardUpdated
            - CardPinnedToListUpdated
            - BoardCreated
            - BoardUpdated
            - BoardDeleted
            - ReminderCreated
            - ReminderUpdated
            - ReminderDeleted
        :type skipNotificationType: String
        
        :param sortDirection: Specify sort direction.
        :type sortDirection: String
        
        :param returnFullResource: Boolean flag indicating whether fully loaded resources should get returned.
        :type returnFullResource: Boolean
        
        :param skipOlderThan: Filter by resource created criterion. String presentation of date that complies with ISO 8601 format.
        :type skipOlderThan: DateTime
        
        :param htmlFormat: Mime format for html body of post resource.
            Available values:
            - text/html-stripped
            - text/html-stripped.mobile
        :type htmlFormat: String
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: ListOfNotificationsPage_22
        """
        url_parameters = {
            'sinceId': sinceId,
            'skipNotificationType': skipNotificationType,
            'sortDirection': sortDirection,
            'returnFullResource': returnFullResource,
            'skipOlderThan': skipOlderThan,
            'htmlFormat': htmlFormat,
            'size': size,
            'offset': offset,
        }
        endpoint_parameters = {
        }
        endpoint = 'notification'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.notification.list.page-v5.18+json',
            'Accept': 'application/vnd.4thoffice.notification.list.page-v5.18+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('get', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(ListOfNotificationsPage_22, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def get_3(self, sinceId, size, offset, longPolling, returnFullResource=None, skipOlderThan=None, htmlFormat=None, impersonate_user_id=None, accept_type=None):
        """
        Get incremental notification list via long polling.
        
        :param sinceId: Specify since id. That is an id of a resource from which incremental list load should take place.
        :type sinceId: String
        
        :param size: Specify size of requested page.
        :type size: Int32
        
        :param offset: Specify offset of requested page.
        :type offset: Int32
        
        :param longPolling: Perform long polling while reading the resource.
        :type longPolling: Boolean
        
        :param returnFullResource: Boolean flag indicating whether fully loaded resources should get returned.
        :type returnFullResource: Boolean
        
        :param skipOlderThan: Filter by resource created criterion. String presentation of date that complies with ISO 8601 format.
        :type skipOlderThan: DateTime
        
        :param htmlFormat: Mime format for html body of post resource.
            Available values:
            - text/html-stripped
            - text/html-stripped.mobile
        :type htmlFormat: String
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: ListOfNotificationsPage_22
        """
        url_parameters = {
            'sinceId': sinceId,
            'returnFullResource': returnFullResource,
            'skipOlderThan': skipOlderThan,
            'htmlFormat': htmlFormat,
            'size': size,
            'offset': offset,
            'longPolling': longPolling,
        }
        endpoint_parameters = {
        }
        endpoint = 'notification'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.notification.list.page-v5.18+json',
            'Accept': 'application/vnd.4thoffice.notification.list.page-v5.18+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('get', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(ListOfNotificationsPage_22, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
