'''environments provides the methods for chef environment resources'''

from .base import Base


class Environments(Base):
    '''
    Provides access to the chef `environments` resource
    '''
    _base_url = '/organizations/%(org)s/environments'

    @classmethod
    def index(cls):
        '''
        Fetches all of the environments on the chef server

        :return: All the chef environments with a url for each environment
        :rtype: hash
        '''
        return super(Environments, cls).index()

    @classmethod
    def get(cls, environmentname):
        '''
        Fetches a environment from the chef server

        :param environmentname: The Environment's environmentname
        :type environmentname: string
        :return: The chef environment
        :rtype: hash
        '''
        return super(Environments, cls).get(environmentname)

    @classmethod
    def create(cls, environment):
        '''
        Creates a new chef environment on the server

        :param environment: The environment to create
        :type environment: hash
        :return: The environmentname and url
        :rtype: hash
        '''
        return super(Environments, cls).create(environment)

    @classmethod
    def update(cls, environmentname, environment):
        '''
        Updates a environment on the chef server

        :param environmentname: The Environment's name
        :param environment: The Environment's config
        :type environmentname: string
        :type environment: hash
        :return: The environment name and url
        :rtype: hash
        '''
        return super(Environments, cls).update(environmentname, environment)

    @classmethod
    def delete(cls, environmentname):
        '''
        Deletes a environment from the chef server

        :param environmentname: The Environment's environmentname
        :type usename: string
        :return: The deleted environment's name
        :rtype: hash
        '''
        return super(Environments, cls).delete(environmentname)

    @classmethod
    def exists(cls, environmentname):
        '''
        Checks if a environment exists on the chef server

        :param environmentname: The Environment's environmentname
        :type usename: string
        :return: If the environment exists
        :rtype: boolean
        '''
        return super(Environments, cls).exists(environmentname)
