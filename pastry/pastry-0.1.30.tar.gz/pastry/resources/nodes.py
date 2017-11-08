'''Nodes provides the methods for chef node resources'''

from .base import Base


class Nodes(Base):
    '''
    Provides access to the chef nodes
    '''
    _base_url = '/organizations/%(org)s/nodes'

    @classmethod
    def exists(cls, nodename):
        '''
        Checks if a node exists on the chef server

        :param nodename: The Node's nodename
        :type nodename: string
        :return: If the node exists
        :rtype: boolean
        '''
        return super(Nodes, cls).exists(nodename)

    @classmethod
    def get_acl(cls, nodename):
        '''
        Gets the access control list for the node

        :param nodename: The Node's nodename
        :type nodename: string
        :return: The acl for the node
        :rtype: hash
        '''
        return super(Nodes, cls).get_acl(nodename)

    @classmethod
    def set_permission(cls, nodename, permission, actors):
        '''
        Grants the specified actors a permission on the node. Chef only
        supports setting one permission at a time.

        The actors hash should be in the form::

            {
                'actors': <list of usernames>
                'groups': <list of groupnames>
            }

        :param nodename: The Node's nodename
        :param permission: One of: create, read, update, delete, grant
        :param actors: The set of actors to grant this permission to
        :type nodename: string
        :type permission: string
        :type actors: hash
        :return: empty hash
        :type: hash
        '''
        return super(Nodes, cls).set_permission(nodename, permission, actors)
