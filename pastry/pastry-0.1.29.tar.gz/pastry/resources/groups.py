'''Groups provides the methods for chef group resources'''

from .base import Base


class Groups(Base):
    '''
    Provides access to the chef `groups` resource
    '''
    _base_url = '/organizations/%(org)s/groups'

    @classmethod
    def index(cls):
        '''
        Fetches all of the groups on the chef server

        :return: All the chef groups with a url for each group
        :rtype: hash
        '''
        return super(Groups, cls).index()

    @classmethod
    def get(cls, groupname):
        '''
        Fetches a group from the chef server

        .. note::

            Chef returns a slightly different format to
            what it expects for create/update groups.

        :param groupname: The Group's name
        :type groupname: string
        :return: The chef group and members
        :rtype: hash
        '''
        return super(Groups, cls).get(groupname)

    @classmethod
    def create(cls, group):
        '''
        Creates a new chef group on the server

        The group hash should be in the form::

            {
                'groupname': <groupname>,
                'name': <groupname>,
                'actors': { #optional
                    'users': <list of usernames>, # optional
                    'clients': <list of clients>, #optional
                    'groups': <list of groups> #optional
                }
            }

        :param group: The group to create
        :type group: hash
        :return: The groupname and url
        :rtype: hash
        '''
        return super(Groups, cls).create(group)

    @classmethod
    def update(cls, groupname, group):
        '''
        Updates a group on the chef server

        the group hash should be in the same format as for create

        :param groupname: The Group's groupname
        :param group: The Group members and content
        :type groupname: string
        :type group: hash
        :return: The groupname and url
        :rtype: hash
        '''
        return super(Groups, cls).update(groupname, group)

    @classmethod
    def delete(cls, groupname):
        '''
        Deletes a group from the chef server

        :param groupname: The Group's groupname
        :type groupname: string
        :return: The deleted group's name
        :rtype: hash
        '''
        return super(Groups, cls).delete(groupname)

    @classmethod
    def exists(cls, groupname):
        '''
        Checks if a group exists on the chef server

        :param username: The Group's groupname
        :type usename: string
        :return: If the group exists
        :rtype: boolean
        '''
        return super(Groups, cls).exists(groupname)
