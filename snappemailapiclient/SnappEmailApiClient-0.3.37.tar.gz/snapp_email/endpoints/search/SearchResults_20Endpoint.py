"""
Auto generated code

"""

import json
from snapp_email.datacontract.classes import SearchResults_20
from snapp_email.datacontract.utils import export_dict, fill


class SearchResults_20Endpoint:
    def __init__(self, api_client):
        self.api_client = api_client
    
    def options(self, impersonate_user_id=None, accept_type=None):
        """
        Retrieve options available for resource 'SearchResults_20'.
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: SearchResults_20
        """
        url_parameters = {
        }
        endpoint_parameters = {
        }
        endpoint = 'search'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.search.results-v5.15+json',
            'Accept': 'application/vnd.4thoffice.search.results-v5.15+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('options', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(SearchResults_20, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def get(self, searchGroupId, size, offset, searchQuery=None, streamStatusFilter=None, streamReadFilter=None, UserStatusFilter=None, returnPinnedOnly=None, returnMineOnly=None, sort=None, sortDirection=None, impersonate_user_id=None, accept_type=None):
        """
        Retrieve search results.
        
        :param searchGroupId: Specify search scope
            Available values:
            - Stream
            - UserStream
            - GroupStream
            - Card
            - PostOnCard
            - PostOnChat
            - File
            - Board
        :type searchGroupId: String
        
        :param size: Specify size of requested page.
        :type size: Int32
        
        :param offset: Specify offset of requested page.
        :type offset: Int32
        
        :param searchQuery: Specify search query.
        :type searchQuery: String
        
        :param streamStatusFilter: Specify stream status filter
            Available values:
            - All
            - Visible
            - Muted
        :type streamStatusFilter: String
        
        :param streamReadFilter: Search filter by stream read status.
            Available values:
            - All
            - Read
            - Unread
        :type streamReadFilter: String
        
        :param UserStatusFilter: Search filter by user status
            Available values:
            - Active
            - Inactive
            - NotRegistered
        :type UserStatusFilter: String
        
        :param returnPinnedOnly: Return pinned resources only.
        :type returnPinnedOnly: Boolean
        
        :param returnMineOnly: Return mine resources only.
        :type returnMineOnly: Boolean
        
        :param sort: Specify sort id.
            Available values:
            - ByCreatedDate
            - ByLastEvent
            - ByModifiedDate
            - ByMostUsed
            - ByName
            - BySize
        :type sort: String
        
        :param sortDirection: Specify sort direction.
            Available values:
            - Ascending
            - Descending
        :type sortDirection: String
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: SearchResults_20
        """
        url_parameters = {
            'searchQuery': searchQuery,
            'searchGroupId': searchGroupId,
            'streamStatusFilter': streamStatusFilter,
            'streamReadFilter': streamReadFilter,
            'UserStatusFilter': UserStatusFilter,
            'returnPinnedOnly': returnPinnedOnly,
            'returnMineOnly': returnMineOnly,
            'sort': sort,
            'sortDirection': sortDirection,
            'size': size,
            'offset': offset,
        }
        endpoint_parameters = {
        }
        endpoint = 'search'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.search.results-v5.15+json',
            'Accept': 'application/vnd.4thoffice.search.results-v5.15+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('get', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(SearchResults_20, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
