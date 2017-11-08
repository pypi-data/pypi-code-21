'''base is a class that resources inherit from to provide common http
methods'''

from pastry.pastry_client import PastryClient
from pastry.exceptions import HttpError


class Base(object):
    '''
    Base class for chef resources to inherit from
    '''
    _base_url = None

    @classmethod
    def base_url(cls):
        '''
        Get the base url for this resource - raise a ValueError if the
        child class has not set it's url
        '''
        if not cls._base_url:
            raise ValueError('Base url has not been set of this resource')
        return cls._base_url

    @classmethod
    def index(cls):
        '''
        Fetch all instances of this resource
        '''
        return PastryClient.call(cls.base_url())

    @classmethod
    def get(cls, instanceid):
        '''
        Fetch a specific instance of a resource
        '''
        return PastryClient.call('%s/%s' % (cls.base_url(), instanceid))

    @classmethod
    def create(cls, instance):
        '''
        Create a new instance
        '''
        return PastryClient.call(
            '%s' % cls.base_url(), method='POST', data=instance)

    @classmethod
    def update(cls, instanceid, instance):
        '''
        Update an instance
        '''
        return PastryClient.call(
            '%s/%s' % (cls.base_url(), instanceid),
            method='PUT',
            data=instance
        )

    @classmethod
    def delete(cls, instanceid):
        '''
        Delete an instance
        '''
        return PastryClient.call(
            '%s/%s' % (cls.base_url(), instanceid), method='DELETE')

    @classmethod
    def exists(cls, instanceid):
        '''
        Check if an instance exists
        '''
        try:
            cls.get(instanceid)
        except HttpError as err:
            if err.statuscode == 404:
                return False
        return True

    @classmethod
    def escape_query(cls, query_string):
        '''
        Escape '%' characters in query_string
        '''
        return query_string.replace('%', '%%')

    @classmethod
    def get_acl(cls, instanceid):
        '''
        Fetch the acl for a chef resource
        '''
        return PastryClient.call(
            '%s/%s/_acl' % (cls.base_url(), instanceid))

    @classmethod
    def set_permission(cls, instanceid, permission, actors):
        '''
        Set a permission on a chef resource
        '''
        return PastryClient.call(
            '%s/%s/_acl/%s' % (cls.base_url(), instanceid, permission),
            method='PUT',
            data={permission: actors}
        )
