'''Nodes provides the methods for chef node resources'''

from .base import Base
from pastry.pastry_client import PastryClient


class Pushy(Base):
    '''
    Provides access to the chef pushy api
    '''
    _base_url = '/organizations/%(org)s/pushy'

    @classmethod
    def status(cls, nodename):
        '''
        Checks the push jobs status of a node

        :param nodename: The Node's nodename
        :type nodename: string
        :return: If pushy jobs is available on the node
        :rtype: boolean
        '''
        return PastryClient.call(
            '%s/node_states/%s' % (cls.base_url(), nodename))
