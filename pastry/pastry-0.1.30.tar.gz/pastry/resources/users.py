'''users provides the methods for chef user resources'''

from .base import Base
from pastry.pastry_client import PastryClient


class Users(Base):
    '''
    Provides access to the chef `users` resource
    '''
    _base_url = '/users'

    @classmethod
    def index(cls):
        '''
        Fetches all of the users on the chef server

        :return: All the chef users with a url for each user
        :rtype: hash
        '''
        return super(Users, cls).index()

    @classmethod
    def get(cls, username):
        '''
        Fetches a user from the chef server

        :param username: The User's username
        :type username: string
        :return: The chef user
        :rtype: hash
        '''
        return super(Users, cls).get(username)

    @classmethod
    def create(cls, user):
        '''
        Creates a new chef user on the server

        The user hash should be in the form::

            {
                'username': <username>,
                'display_name': <display_name>,
                'first_name': <first name>,
                'middle_name': <middle name>, # optional
                'last_name': <last name>,
                'email': <email>,
                'password': <password>
            }

        :param user: The user to create
        :type user: hash
        :return: The username and url
        :rtype: hash
        '''
        return super(Users, cls).create(user)

    @classmethod
    def update(cls, username, user):
        '''
        Updates a user on the chef server

        :param username: The User's username
        :param user: The User members and content
        :type username: string
        :type user: hash
        :return: The username and url
        :rtype: hash
        '''
        return super(Users, cls).update(username, user)

    @classmethod
    def delete(cls, username):
        '''
        Deletes a user from the chef server

        :param username: The User's username
        :type usename: string
        :return: The deleted user's name
        :rtype: hash
        '''
        return super(Users, cls).delete(username)

    @classmethod
    def exists(cls, username):
        '''
        Checks if a user exists on the chef server

        :param username: The User's username
        :type usename: string
        :return: If the user exists
        :rtype: boolean
        '''
        return super(Users, cls).exists(username)

    @classmethod
    def invite(cls, username, orgname):
        '''
        Invite a user to an org

        :param username: The User's username
        :param orgname: The chef organization
        :type username: string
        :type orgname: string
        :return: If the request was successful
        :rtype: boolean
        '''
        return PastryClient.call(
            '/organizations/%s/association_requests' % orgname,
            method='POST',
            data={'user': username}
        )
