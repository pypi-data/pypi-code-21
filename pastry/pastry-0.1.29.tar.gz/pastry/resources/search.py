'''Search provides access to chef's search functionality'''

import urllib
from .base import Base
from pastry.pastry_client import PastryClient


class Search(Base):
    '''
    Provides access to chef `search`
    '''
    _base_url = '/organizations/%(org)s/search'

    @classmethod
    def index(cls):
        '''
        Fetches the available search indexes

        :return: The search indexes
        :rtype: hash
        '''
        return super(Search, cls).index()

    @classmethod
    def run(cls, index, query='*:*', rows=1000, start=0, filters=None):
        '''
        Runs the search query against the index. The default will return
        the a list of all of the properties of the match. Use the filters
        to select which fields should be returned by the query.

        The filters should be a hash where the key is the name of the field
        in the returned hash, and the value is a space separated list of
        where in the index to find the value. e.g.::

            {
                'name': [ 'name' ],
                'ip': [ 'ipaddress' ],
                'kernel_version': [ 'kernel', 'version' ]
            }

        :param index: The index to search against
        :param query: The SOLR query to match the index against
        :param rows: The maximum number of rows to return
        :param start: The row to start at
        :param filters: The filters to apply to the result
        :type index: string
        :type query: string
        :type rows: integer
        :type start: integer
        :type filters: hash
        :return: The matching (and filtered) results
        :rtype: hash
        '''
        query_string = cls.escape_query(urllib.urlencode({
            'q': query,
            'rows': rows,
            'start': start
        }))
        method = 'POST' if filters else 'GET'
        return PastryClient.call(
            '%s/%s?%s' % (cls.base_url(), index, query_string),
            method=method,
            data=filters
        )
