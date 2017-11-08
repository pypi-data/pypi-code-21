'''Cookbook provides the methods for chef cookbooks'''

import requests

from .base import Base
from pastry.exceptions import HttpError
from pastry.pastry_client import PastryClient


class Cookbooks(Base):
    '''
    Provides methods for interacting with chef cookbooks
    '''
    _base_url = '/organizations/%(org)s/cookbooks'

    @classmethod
    def index(cls):
        '''
        Fetches all of the cookbooks (and versions) on the chef server

        :return: All the chef cookbooks and versions
        :rtype: hash
        '''
        return super(Cookbooks, cls).index()

    @classmethod
    def exists(cls, cookbook):
        '''
        Checks if a cookbook exists on the chef server

        :param cookbook: The Cookbook's name
        :type cookbook: string
        :return: If the cookbook exists
        :rtype: boolean
        '''
        return super(Cookbooks, cls).exists(cookbook)

    @classmethod
    def contents(cls, cookbook, version='_latest'):
        '''
        Fetches the cookbooks list of files that chef knows about

        :param cookbook: The cookbook's name
        :param version: The cookbook's version
        :type cookbook: string
        :type version: string
        :return: All of the files the cookbook knows about
        :rtype: hash
        '''
        return PastryClient.call(
            '%s/%s/%s' % (cls.base_url(), cookbook, version))

    @classmethod
    def parse_filename(cls, filename):
        '''
        Splits the file path so that it can be used to call the chef api

        :param filename: The file's path relative to the cookbook root
        :type filename: string
        :return: The type of file, specificity, and filename
        :rtype: iterable
        '''
        parts = filename.split('/')
        if len(parts) == 1:
            return ['root_files', 'default', filename]
        return parts

    @classmethod
    def file_content(cls, cookbook, filename, version='_latest'):
        '''
        Fetches the contents of a specific file in a cookbook

        :param cookbook: The cookbook's name
        :param filename: The name (and path) of the file to fetch
        :param version: The cookbook's version
        :type cookbook: string
        :type filename: string
        :type version: string
        :return: The raw contents of the specified file
        :rtype: string
        '''
        file_type, specificity, name = cls.parse_filename(filename)
        files = cls.contents(cookbook, version=version)
        for file_info in files[file_type]:
            if name == file_info['name'] and \
                    specificity == file_info['specificity']:
                resp = requests.get(
                    file_info['url'], verify=PastryClient.verify)
                if not resp.ok:
                    raise HttpError(resp.text, resp.status_code)
                return resp.text
